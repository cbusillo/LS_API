
$(document).ready(
    function () {
        const lastNameField = $('#id_last_name_input');
        const firstNameField = $('#id_first_name_input');

        const customerSelectField = $('select[name="customer_output"]');
        const outputField = $('#id_text_output');
        const form = $('#check-in-form');
        const url = form.data('url');
        const csrfToken = form.data('csrf-token');
        let lastResponse;

        function fetchData() {
            const lastName = lastNameField.val();
            const firstName = firstNameField.val();

            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'last_name': lastName,
                    'first_name': firstName,
                    'csrfmiddlewaretoken': csrfToken
                },
                dataType: 'json',
                success: function (response) {

                    outputField.val(response.message);
                    displayCustomers(response.customers);

                    lastResponse = response;
                },
                error: function (response) {
                    console.error(response.message);
                }
            });
        }
        fetchData();
        lastNameField.on('input', fetchData);
        firstNameField.on('input', fetchData);


        function displayCustomers(customers) {
            customerSelectField.empty();
            customers.forEach((customer, index) => {
                const option = $('<option>');
                option.text(customer.first_name + ' ' + customer.last_name);
                option.val(customer.id);
                if (index === 0) {
                    option.attr('selected', true); // select first option
                    displayCustomerDetails(customer); // display details for first customer
                }
                customerSelectField.append(option);
            });
        }

        function displayCustomerDetails(customer) {
            const container = $('.customer-detail-container');
            container.empty();

            const fields = [['First Name', customer.first_name],
            ['Last Name', customer.last_name],
            ['Title', customer.title],
            ['Company', customer.company],
            ['Create Time', customer.create_time],
            ['Update Time', customer.update_time],
            ['Updated from LS Time', customer.updated_from_ls_time],

            ];

            fields.forEach(field => {
                const row = $('<p>');
                row.text(`${field[0]}: ${field[1]}`);
                container.append(row);
            });

            const nameRow = $('<p>');
            nameRow.text(`Name: ${customer.first_name} ${customer.last_name}`);
            container.prepend(nameRow);
        }
        customerSelectField.on('change', function () {
            const selectedCustomerId = parseInt($(this).val());
            const selectedCustomer = lastResponse.customers.find(customer => customer.id === selectedCustomerId);
            displayCustomerDetails(selectedCustomer);
        });
    }
);

