
$(document).ready(function () {

    var onFieldChange = function () {
        var today = new Date();
        var formattedDate = (today.getMonth() + 1) + '-' + today.getDate() + '-' + today.getFullYear();
        $('#id_date').val(formattedDate);

        var device_type_id = $('#id_device_type').val();
        var device_part_id = $('#id_device_part').val();

        if (device_part_id === '' || device_type_id === '')
            return;

        // Clear the containers
        $('#tests-container').empty();
        $('#specifications-container').empty();

        // Fetch specifications
        $.get('/checklists/device/' + device_type_id + '/' + device_part_id + '/specifications', function (data) {
            data.forEach(function (spec) {
                var inputHTML = '<div class="row mb-2">'
                    + '<label class="col-sm-4 col-form-label">' + spec.name + '</label>'
                    + '<div class="col-sm-8"><input class="form-control" type="text" name="spec_' + spec.id + '"></div></div>';
                $('#specifications-container').append(inputHTML);
            });
        });

        // Fetch tests
        $.get('/checklists/device/' + device_type_id + '/' + device_part_id + '/tests', function (data) {
            data.tests.forEach(function (test) {
                var inputHTML = '<div class="row mb-2">'
                    + '<label class="col-sm-4 col-form-label">' + test.name + '</label>'
                    + '<div class="col-sm-8 btn-group btn-group-toggle" data-toggle="buttons">';
                for (var key in data.choices) {
                    inputHTML += '<button type="button" class="btn btn-secondary test-button' + (key === 'NT' ? ' active' : '') + '" data-value="' + key + '">' + data.choices[key] + '</button>';
                }
                inputHTML += '<input type="hidden" name="test_' + test.id + '" value="NT">'
                    + '</div><div class="col-sm-5"><input class="form-control test-comment" type="text" name="comment_' + test.id + '" style="display: none;" placeholder="Comment"></div></div>';
                $('#tests-container').append(inputHTML);
            });

            // Handle button clicks
            $(".test-button").click(function () {
                var button = $(this);
                var hiddenInput = button.parent().find("input[type='hidden']");
                button.siblings().removeClass('active');
                button.addClass('active');
                hiddenInput.val(button.data('value'));

                // Show comment box if "Other" is selected
                var commentBox = button.closest('.row').find(".test-comment");
                if (button.data('value') === 'O') {
                    commentBox.show();
                } else {
                    commentBox.hide();
                }
            });
        });
    };

    $('#id_device_part, #id_device_type').change(onFieldChange);

    // trigger the change event to run the function when the page loads
    $('#id_device_part, #id_device_type').trigger('change');
});

