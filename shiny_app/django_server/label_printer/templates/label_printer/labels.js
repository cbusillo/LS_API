$(document).keydown(function (event) {
    if (event.metaKey && event.keyCode === 80) {
        $('#custom_label_print').click();
        event.preventDefault();
    }
});

$(document).ready(function () {
    const textArea = $('#custom-label-text');

    if (textArea.length) {
        textArea.focus(function () {
            const self = $(this);
            setTimeout(function () {
                self.select();
            }, 10);
        });
    }
});
