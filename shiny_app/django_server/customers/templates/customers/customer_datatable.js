$(document).ready(function () {
    const createWorkorderButton = $('.create-workorder-btn');
    const csrfToken = createWorkorderButton.data('csrf_token');
    const dataTable = AjaxDatatableViewUtils.initialize_table(
        $('#customer_datatable'),
        "{% url 'customers:customer_data' %}",
        {
            // extra_options (example)
            processing: false,
            autoWidth: false,
            full_row_select: true,
            scrollX: false,
            initComplete: function () {
                const createWorkorderColumnIndex = $('table thead tr th').length - 1;

                $('table thead tr th:nth-child(' + (createWorkorderColumnIndex + 1) + ')').html(createWorkorderButton.show());
            }
        }, {
        // extra_data
        // ...
    },);

    $('body').on('click', '.create-workorder-btn', function () {
        console.log("Button clicked"); // Debugging
        const customerId = $(this).data('customer-id');
        const url = $(this).data('url');

        $.ajax({
            url: url,
            method: 'POST',
            data: {
                'customer_id': customerId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (response) {
                let workorderId = response.workorder_id;
                if (workorderId > 0) {
                    openWorkorderInSafari(workorderId);
                }
            },
            error: function (error) {
                console.log('Error:', error);
            },
        });
    });
    function openWorkorderInSafari(workorderId) {
        console.info(`Opening workorder ${workorderId} in Safari...`)
        const windowName = "workorderWindow"
        const workorderUrl = `https://us.merchantos.com/?name=workbench.views.beta_workorder&form_name=view&id=${workorderId}&tab=details`
        window.open(workorderUrl, '_blank');
    }
});

