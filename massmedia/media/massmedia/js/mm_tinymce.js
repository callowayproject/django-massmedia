function myFileBrowser (field_name, url, type, win) {
    // alert("Field_Name: " + field_name + "\nURL: " + url + "\nType: " + type + "\nWin: " + win); // debug/testing
    
    var cmsURL = window.location.toString();    // script URL - use an absolute path!
    if (cmsURL.indexOf("?") < 0) {
        cmsURL = cmsURL + "?type=" + type;
    } else {
        cmsURL = cmsURL + "&type=" + type;
    }
    
    var param1 = {
        file : cmsURL,
        title : 'My File Browser',
        width : 420,  // Your dimensions may differ - toy around with them!
        height : 400,
        resizable : "yes",
        inline : "yes",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous : "no"
    };
    var param2 = {
        window : win,
        input : field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    };
    alert("I'm in myFileBrowser!");
    tinyMCE.activeEditor.windowManager.open(param1, param2);
    return false;
}

var FileBrowserDialogue = {
    init : function () {
        // remove tinymce stylesheet.
        var allLinks = document.getElementsByTagName("link");
        allLinks[allLinks.length-1].parentNode.removeChild(allLinks[allLinks.length-1]);
    },
    fileSubmit : function (FileURL) {
        var URL = FileURL;
        var win = tinyMCEPopup.getWindowArg("window");
        
        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;
        
        // change width/height & show preview
        if (win.ImageDialog){
            if (win.ImageDialog.getImageData)
                win.ImageDialog.getImageData();
            if (win.ImageDialog.showPreviewImage)
                win.ImageDialog.showPreviewImage(URL);
        }
        
        // close popup window
        tinyMCEPopup.close();
    }
};

function addEvent( obj, type, fn ) {
    if ( obj.attachEvent ) {
        obj['e'+type+fn] = fn;
        obj[type+fn] = function(){obj['e'+type+fn]( window.event );};
        obj.attachEvent( 'on'+type, obj[type+fn] );
    } else
        obj.addEventListener( type, fn, false );
}

addEvent(window, 'load', function(){
    tinyMCEPopup.onInit.add(FileBrowserDialogue.init, FileBrowserDialogue);
});


