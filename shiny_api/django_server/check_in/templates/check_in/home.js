
var customerSearchForm = $("#customer_search_form");
const csrfToken = customerSearchForm.data('csrf-token');
var lastNameInput = customerSearchForm.find("#id_last_name_input");
var firstNameInput = customerSearchForm.find("#id_first_name_input");
var phoneNumberInput = customerSearchForm.find("#id_phone_number_input");
var emailAddressInput = customerSearchForm.find("#id_email_address_input");
var customerOutput = customerSearchForm.find("#id_customer_output");
const outputField = $('#id_text_output');
var customerDetailForm = $('#customer-detail-container');
var customerDetailContainer = $('#customer-detail-container');
var customerPhoneContainer = $('#customer-phone-container');
var customerEmailContainer = $('#customer-email-container');

customerDetailForm.submit(function () {
    var csrfInput = '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrfToken + '">';
    customerDetailForm.append(csrfInput);
});

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
                customerDetailContainer.html(data.customer_detail_form);
                customerPhoneContainer.html(data.customer_phone_form);
                customerEmailContainer.html(data.customer_email_form);
            },
            error: function (xhr, status, error) {
                console.log('Error:', error);
            }
        });
    } else {
        customerDetailContainer.html('');
        customerPhoneContainer.html('');
        customerEmailContainer.html('');
    }
});

lastNameInput.on("input", function () {
    updateCustomerOutput();
});
firstNameInput.on("input", function () {
    updateCustomerOutput();
});
phoneNumberInput.on("input", function () {
    updateCustomerOutput();
});
emailAddressInput.on("change", function () {
    updateCustomerOutput();
});

function updateCustomerOutput() {

    $.ajax({
        url: customerSearchForm.data("url"),
        type: 'POST',
        data: {
            last_name_input: lastNameInput.val(),
            first_name_input: firstNameInput.val(),
            phone_number_input: phoneNumberInput.val(),
            email_address_input: emailAddressInput.val(),
            csrfmiddlewaretoken: csrfToken
        },
        dataType: "json",
        success: function (data) {
            if (data.customer_options) {
                customerOutput.html(data.customer_options);
                customerOutput.val(customerOutput.find('option:first').val());
                customerOutput.trigger('change');
            }
        },
    });
};
customerOutput.val(customerOutput.find('option:first').val());
customerOutput.trigger('change');