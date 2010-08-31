var MMImageDialog = {
	preInit: function() {
		var url;

		tinyMCEPopup.requireLangPack();

		if (url = tinyMCEPopup.getParam("external_image_list_url")) document.write('<script language="javascript" type="text/javascript" src="' + tinyMCEPopup.editor.documentBaseURI.toAbsolute(url) + '"></script>');
		this.use_transmogrify = tinyMCEPopup.getParam("use_transmogrify", false);
	},

	isNew: true,
    
    container : {},
    
	init: function(ed) {
		var f = document.forms[0];
		var nl = f.elements;
		var ed = tinyMCEPopup.editor;
		var dom = ed.dom;
		this.container = this.getImageContainer(ed.selection.getNode());

		this.isNew = (this.container === null);

		tinyMCEPopup.resizeToInnerSize();

		this.fillFormFromExisting(nl);

		// Setup browse button
		document.getElementById('srcbrowsercontainer').innerHTML = getBrowserHTML('srcbrowser', 'src', 'image', 'theme_advanced_image');
		if (isVisible('srcbrowser')) document.getElementById('src').style.width = '260px';

		// If option enabled default contrain proportions to checked
		if (ed.getParam("mmimage_constrain_proportions", true)) f.constrain.checked = true;
		nl.insert.value = ed.getLang('update');
		this.changeAppearance();
		this.showPreviewImage(nl.src.value, 1);
	},

	fillFormFromExisting: function(nl) {
	    var container = this.container;
	    var dom = tinyMCEPopup.editor.dom;
		if (!nl) return;
		if (!container) return;
		try {
			var img = this.getImage(container);
			var link = this.getLink(container);
			var cap = this.getCaption(container);
			var style = '';
			try {
			    style = container.style.getPropertyCSSValue('float').cssText;
			} catch(e) {}
			
			selectByValue(document.forms[0], 'align', style);

			if (img) {
				nl.src.value = dom.getAttrib(img, 'src');
				nl.width.value = dom.getAttrib(img, 'width');
				nl.height.value = dom.getAttrib(img, 'height');
				nl.alt.value = dom.getAttrib(img, 'alt');
				nl.title.value = dom.getAttrib(img, 'title');
				nl.id.value = dom.getAttrib(img, 'id');
				nl.linkurl.value = dom.getAttrib(link, 'href');
				nl.classes.value = dom.getAttrib(img, 'class');
			}
			if (cap) {
				nl.caption.value = cap.innerHTML;
			}

		} catch(e) {
			console.log(e);
			alert(e);
		}
	},

	getImageContainer: function(el) {
		var ed = tinyMCEPopup.editor;
        var p = ed.dom.getParent(el, 'DIV.mce_image_container');
        return p;
	},

    updateImageContainer : function(cont_args, img_args, a_args, cap_args, caption){
        
    },

    getLink: function(el) {
        if (typeof(el) == "undefined") return null;
        if (el.children[0].tagName == 'A') {
            return el.children[0];
        }
        return null;
    },
    
	getImage: function(el) {
		// Given the container, return the image
        if (typeof(el) == "undefined") return null;
        switch (el.children[0].tagName) {
            case "A":
                return el.children[0].children[0];
                break;
            case "IMG":
                return el.children[0];
                break;
        }
        return null;
	},
    getImageUrl: function() {
        var f = document.forms[0];
        var link = f.elements.src.value;
        var width = f.elements.width.value;
        var height = f.elements.height.value;
        if (this.use_transmogrify) {
            link = link.replace(/_r(\d+x\d+|x\d+|\d+)/, '');
            var sizeString = '_r' + width + 'x' + height;
            var prefix = link.substring(0, link.length - 4);
            var suffix = link.substring(link.length-4, link.length);
            return  prefix + sizeString + suffix;
        } else {
            return f.elements.src.value;
        }
    },
    
	getCaption: function(el) {
		// Given the container, return the <p> tag with the caption
        if (typeof(el) == "undefined") return null;
        if (el.children[1].tagName == 'P') {
            return el.children[1];
        }
        return null;
	},

	createImageContainer: function(container_args, image_args, a_args, caption_args, caption) {
	    // Create an empty image container with some given attributes.
	    // Set it to this.
		var ed = tinyMCEPopup.editor;
		var cont_args = container_args || {};
		var img_args = image_args || {};
		var a_args = a_args || {};
		var cap_args = caption_args || {};
		var caption = caption || '';
        
		this.container = ed.dom.create('div', cont_args);
		if (typeof(a_args.href) != "undefined") {
    		var anchor = ed.dom.add(this.container, ed.dom.create('a', a_args));
            ed.dom.add(anchor, ed.dom.create('img', img_args));
		} else {
		    ed.dom.add(this.container, ed.dom.create('img', img_args));
		}
        ed.dom.add(this.container, ed.dom.create('p', cap_args, caption));
	},

	insert: function(file, title) {
		var ed = tinyMCEPopup.editor,
			t = this,
			f = document.forms[0];

		if (f.src.value === '' && this.container) {
			if (container) {
				ed.dom.remove(this.container);
				ed.execCommand('mceRepaint');
			}

			tinyMCEPopup.close();
			return;
		}
		if (tinyMCEPopup.getParam("accessibility_warnings", 1)) {
			if (!f.alt.value) {
				tinyMCEPopup.confirm(tinyMCEPopup.getLang('mmimage_dlg.missing_alt'), function(s) {
					if (s) t.insertAndClose();
				});

				return;
			}
		}

		t.insertAndClose();
	},

	insertAndClose: function() {
		var ed = tinyMCEPopup.editor;
		var f = document.forms[0];
		var nl = f.elements;
		var v;
		var img_args = {};
		var a_args = {};
		var cap_args = {};
		var cont_args = {};
		var el = this.container;

		tinyMCEPopup.restoreSelection();

		// Fixes crash in Safari
		if (tinymce.isWebKit) ed.getWin().focus();

		var align = getSelectValue(f, 'align');
		if (align !== "") cont_args = {style: 'float: ' + align + ";"};
		var id = nl.id;
        var caption = nl.caption.value;
		tinymce.extend(img_args, {
			src: this.getImageUrl(),
			width: nl.width.value,
			height: nl.height.value,
			alt: nl.alt.value,
			title: nl.title.value,
			'class': nl.classes.value,
			id: '__mce_tmp'
		});
		tinymce.extend(a_args, {
		    href: nl.linkurl.value,
		    target: '_blank'
		});
        tinymce.extend(cap_args, {
            'class': 'mce_image_caption'
        });
        tinymce.extend(cont_args, {
            'class': 'mce_image_container',
            id: '__mce_tmp_1'
        });
		if (el) {
	        this.createImageContainer(cont_args, img_args, a_args, cap_args, caption);
	        var node = ed.selection.getNode();
            ed.selection.setNode(this.container);
		} else {
		    try{
		        this.createImageContainer(cont_args, img_args, a_args, cap_args, caption);
		        var cur_sel = ed.selection.getNode();
		        ed.dom.insertAfter(this.container, cur_sel);
		        ed.dom.insertAfter(ed.dom.create('p', {},' '), this.container);
			    ed.undoManager.add();
		    } catch(e){
    		    console.log(e);
    		    alert(e);
		    }
		}

        ed.execCommand('mceRepaint');
		tinyMCEPopup.close();
		ed.execCommand('mceCleanup');
	},

	getAttrib: function(e, at) { },

	setSwapImage: function(st) { },

	fillClassList: function(id) { },

	fillFileList: function(id, l) { },

	resetImageData: function() {
		var f = document.forms[0];

		f.elements.width.value = f.elements.height.value = '';
	},
    
    setImageData: function(caption, linkURL) {
        var f = document.forms[0];
        f.elements.linkurl.value = linkURL;
        f.elements.caption.value = caption;
    },
    
    getImageData: function(caption, linkURL) {},
    
	updateImageData: function(img, st) {
		var f = document.forms[0];

		if (!st) {
			f.elements.width.value = img.width;
			f.elements.height.value = img.height;
		}

		this.preloadImg = img;
	},

	changeAppearance: function() {
		var ed = tinyMCEPopup.editor,
			f = document.forms[0],
			img = document.getElementById('alignSampleImg');

		if (img) {
			img.align = f.align.value;
		}
	},

	changeHeight: function() {
		var f = document.forms[0],
			tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) return;
		if (f.width.value == "" || f.height.value == "") return;

		tp = (parseInt(f.width.value) / parseInt(t.preloadImg.width)) * t.preloadImg.height;
		f.height.value = tp.toFixed(0);
	},

	changeWidth: function() {
		var f = document.forms[0],
			tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) return;
		if (f.width.value == "" || f.height.value == "") return;

		tp = (parseInt(f.height.value) / parseInt(t.preloadImg.height)) * t.preloadImg.width;
		f.width.value = tp.toFixed(0);
	},

	updateStyle: function(ty) {},

	changeMouseMove: function() {},

	showPreviewImage: function(u, st) {
		if (!u) {
			tinyMCEPopup.dom.setHTML('prev', '');
			return;
		}

		if (!st && tinyMCEPopup.getParam("mmimage_update_dimensions_onchange", true)) this.resetImageData();

		u = tinyMCEPopup.editor.documentBaseURI.toAbsolute(u);

		if (!st) tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="MMImageDialog.updateImageData(this);" onerror="MMImageDialog.resetImageData();" />');
		else tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="MMImageDialog.updateImageData(this, 1);" />');
	}
};

MMImageDialog.preInit();
tinyMCEPopup.onInit.add(MMImageDialog.init, MMImageDialog);
