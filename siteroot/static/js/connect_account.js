$(function () {
    // Form display
    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function() {
                $("#modal-connect-account .modal-content").html("");
                $("#modal-connect-account").modal("show");
            },
            success: function(data) {
                $("#modal-connect-account .modal-content").html(data.html_form);
            }
        });
    };

    // Form validation
    var saveForm = function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    protocol = window.location.protocol;
                    host = window.location.host;
                    window.location.replace(protocol+"//"+host+"/dashboard");
                }
                else {
                    $("#modal-connect-account .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };

    // Bind to buttons
    $(".js-connect-account").click(loadForm);
    $("#modal-connect-account").on("submit", ".js-connect-account-form", saveForm);
});