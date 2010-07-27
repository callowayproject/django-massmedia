function djangoFileBrowser (field_name, url, type, win) {
    // alert("Field_Name: " + field_name + "\nURL: " + url + "\nType: " + type + "\nWin: " + win); // debug/testing
    
    var cmsURL = "{{ fb_url }}?pop=2&type=" + type;
    
    var param1 = {
        file : cmsURL,
        title : 'Massmedia Image Browser',
        width : 900,  // Your dimensions may differ - toy around with them!
        height : 600,
        resizable : "yes",
        inline : "yes",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous : "no"
    };
    var param2 = {
        window : win,
        input : field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    };
    tinyMCE.activeEditor.windowManager.open(param1, param2);
    return false;
}
