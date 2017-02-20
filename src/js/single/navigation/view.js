$(function() {
    "use strict";

    $('.sortable').sortable({
        connectWith: $('.sortable'),
        handle: ".sortable_handler",
        items: '> div[class!="leave-alone"]',
        stop: function() {
            var list = crawl_entries($('#outer'));

            $.post(
                Flask.url_for("navigation.reorder"),
                {entries: JSON.stringify(list)},
                function() {
                    utils.flash.clear();
                    utils.flash.new('De volgorde is succesvol opgeslagen',
                        'success', false);
                }
            );
        }
    });
});

function crawl_entries($list) {
    "use strict";

    var list = [];

    $list.children('div').each(function (index, element) {
        var $element = $(element);
        var $deeper_list = $element.children('div.sortable:first');
        var children = crawl_entries($deeper_list);
        var data = {
            'id': $element.data('entry-id'),
            'children': children
        };
        list.push(data);
    });
    return list;
}
