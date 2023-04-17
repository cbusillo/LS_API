let customerSearchForm = $("#customer_search_form");
const csrfToken = customerSearchForm.data('csrf-token');
let lastNameInput = customerSearchForm.find("#id_last_name_input");
let firstNameInput = customerSearchForm.find("#id_first_name_input");
let phoneNumberInput = customerSearchForm.find("#id_phone_number_input");
let emailAddressInput = customerSearchForm.find("#id_email_address_input");
let everythingInput = customerSearchForm.find("#id_everything_input");
let customerOutput = customerSearchForm.find("#id_customer_output");
const outputField = $('#id_text_output');
let customerDetailForm = $('#customer-detail-container');
let customerDetailContainer = $('#customer-detail-container');
let customerPhoneContainer = $('#customer-phone-container');
let customerEmailContainer = $('#customer-email-container');
let workorderButtonsContainer = $('#workorder-buttons-container');
const createWorkorderButton = document.getElementById('create-workorder-button');

customerDetailForm.submit(function () {
    let csrfInput = '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrfToken + '">';
    customerDetailForm.append(csrfInput);
});

createWorkorderButton.addEventListener('click', async function (event) {
    event.preventDefault();
    let customerId = customerOutput.val();
    let submitData; // define the variable here

    if (!customerId) {
        if (!validateCustomerInput()) {
            return;
        }

        submitData = {
            form: customerSearchForm.serialize(),
            csrfmiddlewaretoken: csrfToken
        };
    } else {
        submitData = {
            customer_id: customerId,
            csrfmiddlewaretoken: csrfToken
        };
    }

    $.ajax({
        url: createWorkorderButton.getAttribute('data-url'),
        type: 'POST',
        dataType: 'json',
        data: submitData, // use the variable here
        success: function (data) {
            let workorderId = data.workorder_id;
            if (workorderId > 0) {
                openWorkorderInSafari(workorderId);
            }
        },
        error: function (xhr, status, error) {
            console.log('Error:', error);
        }
    });
});


customerOutput.change(function () {
    removeInvalidFeedback();
    let customerId = $(this).val();
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
                workorderButtonsContainer.removeClass('d-none');
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
    removeInvalidFeedback($(this));
});
firstNameInput.on("input", function () {
    updateCustomerOutput();
    removeInvalidFeedback($(this));
});
phoneNumberInput.on("input", function () {
    updateCustomerOutput();
    removeInvalidFeedback($(this));
});
emailAddressInput.on("input", function () {
    updateCustomerOutput();
    removeInvalidFeedback($(this));
});
everythingInput.on("input", function () {
    updateCustomerOutput();
});

function removeInvalidFeedback(field) {
    if (customerOutput.val()) {
        [firstNameInput, lastNameInput, phoneNumberInput, emailAddressInput].forEach((input) => {
            input.removeClass('is-invalid');
            input.next('.invalid-feedback').remove();
        });
    } else if (field) {
        if (field.is(phoneNumberInput) && !isPhoneNumberValid(field.val().trim())) {
            return;
        }
        if (field.is(emailAddressInput) && !isEmailAddressValid(field.val().trim())) {
            return;
        }

        field.removeClass('is-invalid');
        field.next('.invalid-feedback').remove();
    }
}



function isPhoneNumberValid(phoneNumber) {
    const digitCount = phoneNumber.replace(/\D+/g, '').length;
    return digitCount >= 10;
}

function isEmailAddressValid(emailAddress) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(emailAddress);
}

function updateCustomerOutput() {

    $.ajax({
        url: customerSearchForm.data("url"),
        type: 'POST',
        data: {
            last_name_input: lastNameInput.val(),
            first_name_input: firstNameInput.val(),
            phone_number_input: phoneNumberInput.val(),
            email_address_input: emailAddressInput.val(),
            everything_input: everythingInput.val(),
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

function openWorkorderInSafari(workorderId) {
    console.info(`Opening workorder ${workorderId} in Safari...`)
    const windowName = "workorderWindow"
    const workorderUrl = `https://us.merchantos.com/?name=workbench.views.beta_workorder&form_name=view&id=${workorderId}&tab=details`
    window.open(workorderUrl, '_blank');
}

function validateCustomerInput() {
    const firstName = firstNameInput.val().trim();
    const lastName = lastNameInput.val().trim();
    const phoneNumber = phoneNumberInput.val().trim();
    const emailAddress = emailAddressInput.val().trim();

    if (firstName === '') {
        firstNameInput.addClass('is-invalid');
        firstNameInput.after('<div class="invalid-feedback">First name is required.</div>');
        valid = false;
    }
    if (lastName === '') {
        lastNameInput.addClass('is-invalid');
        lastNameInput.after('<div class="invalid-feedback">Last name is required.</div>');
        valid = false;
    }
    if (!isPhoneNumberValid(phoneNumber)) {
        phoneNumberInput.addClass('is-invalid');
        phoneNumberInput.after('<div class="invalid-feedback">Phone number must be at least 10 digits long.</div>');
        valid = false;
    }

    if (!isEmailAddressValid(emailAddress)) {
        emailAddressInput.addClass('is-invalid');
        emailAddressInput.after('<div class="invalid-feedback">Invalid email address format.</div>');
        valid = false;
    }

    return valid;
}

customerOutput.val(customerOutput.find('option:first').val());
customerOutput.trigger('change');