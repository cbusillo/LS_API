
var customerSearchForm = $("#customer_search_form");
const csrfToken = customerSearchForm.data('csrf-token');
var lastNameInput = customerSearchForm.find("#id_last_name_input");
var firstNameInput = customerSearchForm.find("#id_first_name_input");
var customerOutput = customerSearchForm.find("#id_customer_output");
const outputField = $('#id_text_output');
var customerDetailForm = $('.customer-detail-container form');
var customerDetailContainer = $('.customer-detail-container');

// Add an event listener to the customer_detail_form to include the CSRF token in the POST data
customerDetailForm.submit(function () {
    var csrfInput = '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrfToken + '">';
    customerDetailForm.append(csrfInput);
});

// Add an event listener to the customerOutput select to display the selected customer's information
customerOutput.change(function () {
    var customerId = $(this).val();
    if (customerId) {
        $.ajax({
            url: customerSearchForm.data("url"),
            type: 'POST',
            dataType: 'json',
            data: {
                customer_id: customerId,
                csrfmiddlewaretoken: csrfToken
            },
            success: function (data) {
                outputField.val(data.customer_detail_form);
                customerDetailContainer.html(data.customer_detail_form);
                customerDetailForm = $('.customer-detail-container form');
                customerDetailForm.submit(function () {
                    if (!customerDetailForm.find('input[name="csrfmiddlewaretoken"]').length) { // check if CSRF token input field already exists
                        var csrfInput = '<input type="hidden" name="csrfmiddlewaretoken" value="' + cCsrfToken + '">';
                        customerDetailForm.append(csrfInput);
                    }
                });
            },
            error: function (xhr, status, error) {
                console.log('Error:', error);
            }
        });
    } else {
        customerDetailContainer.html('');
    }
});

lastNameInput.on("keyup", function () {
    updateCustomerOutput();
});
firstNameInput.on("keyup", function () {
    updateCustomerOutput();
});

function updateCustomerOutput() {
    customerDetailContainer.html('');
    $.ajax({
        url: customerSearchForm.data("url"),
        type: 'POST',
        data: {
            last_name_input: lastNameInput.val(),
            first_name_input: firstNameInput.val(),
            csrfmiddlewaretoken: csrfToken
        },
        dataType: "json",
        success: function (data) {
            outputField.val(data.message);
            if (data.html_customer_options) {
                customerOutput.html(data.html_customer_options);
            }
        },
    });
};
