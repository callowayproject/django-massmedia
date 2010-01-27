var opts = 'width=800,height=400,scrollbars=yes,scrolling=yes,location=no,toolbar=no';

//Audio
var MassAudioCommand=function(){};
MassAudioCommand.GetState=function() {return FCK_TRISTATE_OFF;}
MassAudioCommand.Execute=function() {
    window.open('/admin/massmedia/audio/?t=id&pop=1', 'MassAudio', opts);
}
FCKCommands.RegisterCommand('MassAudio', MassAudioCommand ); 
var oMassAudios = new FCKToolbarButton('MassAudio', 'insert audio');
oMassAudios.IconPath = FCKConfig.PluginsPath + 'fckmassmedia/audio.png'; 
FCKToolbarItems.RegisterItem( 'MassAudio', oMassAudios );

//Video
var MassVideoCommand=function(){};
MassVideoCommand.GetState=function() {return FCK_TRISTATE_OFF;}
MassVideoCommand.Execute=function() {
    window.open('/admin/massmedia/video/?t=id&pop=1', 'MassVideo', opts);
}
FCKCommands.RegisterCommand('MassVideo', MassVideoCommand ); 
var oMassVideos = new FCKToolbarButton('MassVideo', 'insert media');
oMassVideos.IconPath = FCKConfig.PluginsPath + 'fckmassmedia/video.png'; 
FCKToolbarItems.RegisterItem( 'MassVideo', oMassVideos );

//Image
var MassImageCommand=function(){};
MassImageCommand.GetState=function() {return FCK_TRISTATE_OFF;}
MassImageCommand.Execute=function() {
    window.open('/admin/massmedia/image/?t=id&pop=1', 'MassImage', opts);
}
FCKCommands.RegisterCommand('MassImage', MassImageCommand ); 
var oMassImages = new FCKToolbarButton('MassImage', 'insert image');
oMassImages.IconPath = FCKConfig.PluginsPath + 'fckmassmedia/image.png'; 
FCKToolbarItems.RegisterItem( 'MassImage', oMassImages );

//Flash
var MassFlashCommand=function(){};
MassFlashCommand.GetState=function() {return FCK_TRISTATE_OFF;}
MassFlashCommand.Execute=function() {
    window.open('/admin/massmedia/flash/?t=id&pop=1', 'MassFlash', opts);
}
FCKCommands.RegisterCommand('MassFlash', MassFlashCommand ); 
var oMassFlashs = new FCKToolbarButton('MassFlash', 'insert flash');
oMassFlashs.IconPath = FCKConfig.PluginsPath + 'fckmassmedia/flash.png'; 
FCKToolbarItems.RegisterItem( 'MassFlash', oMassFlashs );

// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
}

// IE doesn't accept periods or dashes in the window name, but the element IDs
// we use to generate popup window names may contain them, therefore we map them
// to allowed characters in a reversible way so that we can locate the correct 
// element when the popup window is dismissed.
function id_to_windowname(text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    return text;
}

function windowname_to_id(text) {
    text = text.replace(/__dot__/g, '.');
    text = text.replace(/__dash__/g, '-');
    return text;
}

function showRelatedObjectLookupPopup(triggeringLink) {
    return false;
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);
    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1';
    } else {
        href = triggeringLink.href + '?pop=1';
    }
    var win = window.open(href, name, opts);
    win.focus();
    return false;
}
function insert_content(url, editor){
    var page_request = false;
    if (window.XMLHttpRequest) 
        page_request = new XMLHttpRequest();
    else if (window.ActiveXObject){ 
        try {
            page_request = new ActiveXObject("Msxml2.XMLHTTP");
        } 
        catch (e){
            try{
                page_request = new ActiveXObject("Microsoft.XMLHTTP");
            }
            catch (e){
                alert(e);
            }
        }
    } else
        return false;
    page_request.onreadystatechange=function(){
        loadpage(page_request, editor);
    }
    page_request.open('GET', url, true);
    page_request.send(null);
    return true;
}

function loadpage(page_request, editor){
    if (page_request.readyState == 4 && (page_request.status==200 || window.location.href.indexOf("http")==-1))
        alert(page_request.responseText);
        editor.InsertHtml(page_request.responseText);
}

function load_widget(win, id){
    name = id_to_windowname(win.name);
    if (name == 'MassAudio')
            type = 'audio';
    else if (name == 'MassImage')
            type = 'image';
    else if (name == 'MassFlash')
            type = 'flash';
    else if (name == 'MassVideo')
            type = 'video';
    url = '/massmedia/widget/' + id + '/' + type + '/';
    var allPageTags = win.opener.parent.document.getElementsByTagName("textarea");
    for (i = 0; i < allPageTags.length; i++) {
            if (allPageTags[i].className == "vLargeTextField") {
                try{
                    var oEditor = FCKeditorAPI.GetInstance(allPageTags[i].id) ;
                    oEditor.InsertHtml('<iframe id="'+ type + id +'" scrolling="no" frameborder="0" vspace="0" hspace="0" marginheight="0" marginwidth="0" src="'+ url +'"></iframe>');
                    //insert_content(url, oEditor);
                    break;
                } catch(e){
                    alert(e);
                    continue;
                }
            }
    }
    win.close();
}

function dismissRelatedLookupPopup(win, chosenId) {
    return load_widget(win, chosenId);
}


function dismissAddAnotherPopup(win, newId, newRepr) {
    return load_widget(win, newId);
}
