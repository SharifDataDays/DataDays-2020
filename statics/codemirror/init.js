(function () {
    var $ = django.jQuery;
    $(document).ready(function () {
        $('textarea.python-editor').each(function (idx, el) {
            CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                mode: 'htmlmixed',
            });
        });
    });
})();