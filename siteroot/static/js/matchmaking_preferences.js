$(function () {
    // Form display
    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function() {
                $("#modal-matchmaking-preferences .modal-content").html("");
                $("#modal-matchmaking-preferences").modal("show");
            },
            success: function(data) {
                $("#modal-matchmaking-preferences .modal-content").html(data.html_form);
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
                    $("#modal-matchmaking-preferences .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };

    // Bind to buttons
    $(".js-matchmaking-preferences").click(loadForm);
    $("#modal-matchmaking-preferences").on("submit", ".js-matchmaking-preferences-form", saveForm);
});