function showGenericRelatedObjectLookupPopup(triggeringLink, ctArray) {
    var realName = triggeringLink.id.replace(/^lookup_/, '');
    var name = id_to_windowname(realName);
    realName = realName.replace(/object_id/, 'content_type');
    var select = document.getElementById(realName);
    if (select.selectedIndex === 0) {
        alert("Select a content type first.");
        return false;
    }
    var selectedItem = select.item(select.selectedIndex).value;
    var href = triggeringLink.href.replace(/#/,'../../../'+ctArray[selectedItem]+"/?t=id");
    if (href.search(/\?/) >= 0) {
        href = href + '&pop=1';
    } else {
        href = href + '?pop=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}
/* This script takes inspiration from http://djangosnippets.org/snippets/1053/
    Depending on the context it can be broken so it needs to be improved...
    Franck Bret, 2010 - franckbret@gmail.com
*/
jQuery(function($) {
    /* We first need to be sure that a position field is here */
    if($(this).find('td.position input:text')){
        if ($('div.inline-group > div.tabular').size() > 0){
            /* For tabular inline related, ie admin.TabularInline */
            $('div.inline-group').sortable({
                items: 'tr.has_original',
                handle: 'td',
                update: function() {
                    $(this).find('tr.has_original').each(function(i) {
                        $(this).find('input[name$=order]').val(i+1);
                        $(this).removeClass('row1').removeClass('row2');
                        $(this).addClass('row'+((i%2)+1));
                        $(this).find('td.position input:text').val(i+1);
                    });
                }
            });
            $('tr.has_original').css('cursor', 'move');
        } else {
            /* For inline-related, ie admin.StackedInline */
            $('div.inline-group').sortable({
                items: 'div.inline-related',
                handle: 'h3:first',
                update: function() {
                    alert('Sorry, the script is not done yet for Stackedinline. Check the code and improve');
                    $(this).find('div.inline-related').each(function(i) {
                        // NOT DONE YET ;-)
                        //if ($(this).find('select option:selected').val()) {
                        //    $(this).find('input:text').val(i+1);
                        //    }
                    });
                }
            });
            $('div.inline-related h3').css('cursor', 'move');
        }
    }
});
