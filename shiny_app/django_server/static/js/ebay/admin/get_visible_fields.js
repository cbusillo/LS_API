$(document).ready(function () {
    var $showAllButton = $('<button>', { type: 'button', id: 'show-all-fields', text: 'Show All Fields' });
    $('form').prepend($showAllButton);

    // Show all fields when the button is clicked
    $showAllButton.click(function () {
        $(".form-row").show();
    });
    const $deviceField = $('#id_device');
    const $partField = $('#id_part');

    function updateVisibleFields() {
        const device = $deviceField.val();
        const part = $partField.val();

        $.getJSON('/ebay/get_visible_fields/', { device: device, part: part }, function (data) {
            for (const [fieldName, isVisible] of Object.entries(data.visible_fields)) {
                const $field = $(`#id_${fieldName}`);
                if (isVisible) {
                    $field.closest(`.field-${fieldName}`).show();
                } else if (fieldName !== 'sku') {
                    $field.closest(`.field-${fieldName}`).hide();
                }
            }
        });
    }

    // Initially hide all fields
    //$('.form-row').hide();
    $deviceField.closest('.form-row').show();

    updateVisibleFields();  // Run on page load
    $deviceField.on('change', updateVisibleFields);
    $partField.on('change', updateVisibleFields);
});
