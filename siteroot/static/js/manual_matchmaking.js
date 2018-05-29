$(function () {
    var showMatchmakingList = function () {
        $.ajax({
            url: '/dashboard/manual_matchmaking/',
            type: 'get',
            dataType: 'json',
            success: function(data) {
                $('#manual-matchmaking-list .list-content').html(data.html_match_list);
            }
        });
        return false;
    };

    $(".js-load-manual-matches").click(showMatchmakingList);
});