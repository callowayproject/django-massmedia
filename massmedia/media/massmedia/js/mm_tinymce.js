var FileBrowserDialogue = {
    init : function () {
        // remove tinymce stylesheet.
        var allLinks = document.getElementsByTagName("link");
        allLinks[allLinks.length-1].parentNode.removeChild(allLinks[allLinks.length-1]);
    },
    fileSubmit : function (FileURL, caption, linkURL) {
        var URL = FileURL;
        var win = tinyMCEPopup.getWindowArg("window");
        
        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;
        
        // change width/height & show preview
        if (win.MMImageDialog){
            if (win.MMImageDialog.getImageData)
                win.MMImageDialog.getImageData();
            if (win.MMImageDialog.setImageData)
                win.MMImageDialog.setImageData(caption, linkURL);
            if (win.MMImageDialog.showPreviewImage)
                win.MMImageDialog.showPreviewImage(URL);
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


