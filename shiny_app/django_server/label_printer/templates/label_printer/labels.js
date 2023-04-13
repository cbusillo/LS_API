document.addEventListener('keydown', function (event) {
    if (event.metaKey && event.keyCode === 80) {
        document.getElementById('custom_label_print').click();
        event.preventDefault();
    }
});
const textArea = document.getElementById('custom-label-text');

document.addEventListener('DOMContentLoaded', function () {
    const textArea = document.getElementById('custom-label-text');

    if (textArea) {
        textArea.addEventListener('focus', function () {
            const self = this;
            setTimeout(function () {
                self.select();
            }, 10);
        });
    }
});