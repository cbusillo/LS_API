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
            full_row_select: false,
            scrollX: false,
            dom: 'rt<"bottom"iflp><"clear">',

            initComplete: function () {
                const createWorkorderColumnIndex = $('table thead tr th').length;

                $('table thead tr th:nth-child(' + (createWorkorderColumnIndex) + ')').html(createWorkorderButton.show());
                lastNameInput = $('.datatable-column-filter-row > th:nth-child(2) > input:nth-child(1)')
                firstNameInput = $('.datatable-column-filter-row > th:nth-child(3) > input:nth-child(1)')
                phoneNumberInput = $('.datatable-column-filter-row > th:nth-child(4) > input:nth-child(1)')
                emailAddressInput = $('.datatable-column-filter-row > th:nth-child(5) > input:nth-child(1)')
                lastNameInput.on("input", function () {
                    removeInvalidFeedback($(this));
                });
                firstNameInput.on("input", function () {
                    removeInvalidFeedback($(this));
                });
                phoneNumberInput.on("input", function () {
                    removeInvalidFeedback($(this));
                });
                emailAddressInput.on("input", function () {
                    removeInvalidFeedback($(this));
                });

            },
            drawCallback: function (settings) {
                const createWorkorderColumnIndex = $('table thead tr th').length;
                let createWorkorderButtonNewCustomer = $('.datatable-column-filter-row > th:nth-child(' + createWorkorderColumnIndex / 2 + ')');
                createWorkorderButtonNewCustomer.html(createWorkorderButton.show().removeClass("btn-secondary").addClass("btn-primary"));


                const numberOfRows = $(settings.nTable).DataTable().rows().count(); // Access the number of data rows
                if (numberOfRows == 0) {
                    createWorkorderButtonNewCustomer.html(createWorkorderButton.show().removeClass("btn-secondary").addClass("btn-primary"));
                } else {
                    createWorkorderButtonNewCustomer.html("")
                }

            }

        }, {
        // extra_data
        // ...
    },);




    $('body').on('click', '.create-workorder-btn', function (event) {
        if ($(this).hasClass("btn-primary")) {

            if (!validateCustomerInput()) { return }
        }
        console.info("valid")
        event.stopPropagation();
        const customerId = $(this).data('customer-id');
        const url = $(this).data('url');

        $.ajax({
            url: url,
            method: 'POST',
            data: {
                'customer_id': customerId,
                'last_name': lastNameInput.val().trim(),
                'first_name': firstNameInput.val().trim(),
                'phone_number': phoneNumberInput.val().trim(),
                'email_address': emailAddressInput.val().trim(),
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

    function validateCustomerInput() {
        const firstName = firstNameInput.val().trim().charAt(0).toUpperCase() + firstNameInput.val().trim().slice(1);
        const lastName = lastNameInput.val().trim().charAt(0).toUpperCase() + lastNameInput.val().trim().slice(1);
        const phoneNumber = phoneNumberInput.val().trim().replace(/\D+/g, '');
        const emailAddress = emailAddressInput.val().trim();
        firstNameInput.val(firstName);
        lastNameInput.val(lastName);
        phoneNumberInput.val(phoneNumber);
        emailAddressInput.val(emailAddress);

        let valid = true;

        if (firstName === '') {
            if (!firstNameInput.hasClass("is-invalid")) {
                firstNameInput.addClass('is-invalid');
                firstNameInput.after('<div class="invalid-feedback">First name is required.</div>');
            }
            valid = false;
        }
        if (lastName === '') {
            if (!lastNameInput.hasClass("is-invalid")) {
                lastNameInput.addClass('is-invalid');
                lastNameInput.after('<div class="invalid-feedback">Last name is required.</div>');
            }
            valid = false;
        }
        if (!isPhoneNumberValid(phoneNumber)) {
            if (!phoneNumberInput.hasClass("is-invalid")) {
                phoneNumberInput.addClass('is-invalid');
                phoneNumberInput.after('<div class="invalid-feedback">Phone number is required.</div>');
            }
            valid = false;
        }

        if (!isEmailAddressValid(emailAddress)) {
            if (!emailAddressInput.hasClass("is-invalid")) {
                emailAddressInput.addClass('is-invalid');
                emailAddressInput.after('<div class="invalid-feedback">Invalid email address format.</div>');
            }
            valid = false;
        }

        return valid;
    }
    function isPhoneNumberValid(phoneNumber) {
        const digitCount = phoneNumber.replace(/\D+/g, '').length;
        return digitCount >= 10;
    }

    function isEmailAddressValid(emailAddress) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(emailAddress);
    }



    function removeInvalidFeedback(field) {
        if (field) {
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


});

