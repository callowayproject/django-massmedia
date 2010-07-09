var ImageDialog = {
	preInit: function() {
		var url;

		tinyMCEPopup.requireLangPack();

		if (url = tinyMCEPopup.getParam("external_image_list_url")) document.write('<script language="javascript" type="text/javascript" src="' + tinyMCEPopup.editor.documentBaseURI.toAbsolute(url) + '"></script>');
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

		ed.onClick.add(function(ed, e) {
			e = e.target;
			if (e.nodeName == 'IMG') {
				if (dom.getAttrib(e.parent, 'class') === 'mce_image_container') {
					ed.selection.select(e.parent);
				}
			}
		});

		tinyMCEPopup.resizeToInnerSize();

		this.fillFormFromExisting(nl);

		// Setup browse button
		document.getElementById('srcbrowsercontainer').innerHTML = getBrowserHTML('srcbrowser', 'src', 'image', 'theme_advanced_image');
		if (isVisible('srcbrowser')) document.getElementById('src').style.width = '260px';

		// If option enabled default contrain proportions to checked
		if (ed.getParam("advimage_constrain_proportions", true)) f.constrain.checked = true;

		this.changeAppearance();
		this.showPreviewImage(nl.src.value, 1);
	},

	fillFormFromExisting: function(nl) {
	    container = this.container;
		if (!nl) return;
		if (!container) return;
		try {
			var img = this.getImage(container);
			var cap = this.getCaption(container);
			selectByValue(f, 'align', this.getAttrib(container, 'align'));

			if (img) {
				nl.src.value = dom.getAttrib(img, 'src');
				nl.width.value = dom.getAttrib(img, 'width');
				nl.height.value = dom.getAttrib(img, 'height');
				nl.alt.value = dom.getAttrib(img, 'alt');
				nl.title.value = dom.getAttrib(img, 'title');
				nl.id.value = dom.getAttrib(img, 'id');
				nl.classes.value = dom.getAttrib(img, 'class');
			}
			if (cap) {
				nl.caption.value = cap.innerHTML;
			}
			nl.insert.value = ed.getLang('update');

		} catch(e) {
			console.log(e);
		}
	},

	getImageContainer: function(el) {
		var ed = tinyMCEPopup.editor;

		if (el && ed.dom.getAttrib(el, 'class') === 'mce_image_container') {
			return el;
		}
		var pel = ed.dom.getParent(el, 'div');
		if (el && el.nodeName == 'IMG') {
			if (epl && pel.hasClass('mce_image_container')) {
				return pel;
			}
		}
		if (el && el.nodeName == 'P' && ed.dom.hasClass(el, 'mce_image_caption')) {
			if (pel && ed.dom.hasClass(pel, 'mce_image_container')) {
				return pel;
			}
		}
		return null;
	},

    updateImageContainer : function(cont_args, img_args, cap_args){
        
    },

	getImage: function(el) {
		// Given the container, return the image
		console.dir(el);
		return null;
	},

	getCaption: function(el) {
		// Given the container, return the <p> tag with the caption
		return null;
	},

	createImageContainer: function(container_args, image_args, caption_args, caption) {
	    // Create an empty image container with some given attributes.
	    // Set it to this.
		var ed = tinyMCEPopup.editor;
		var cont_args = container_args || {};
		var img_args = image_args || {};
		var cap_args = caption_args || {};
		var caption = caption || '';
        
		this.container = ed.dom.create('div', cont_args);
        ed.dom.add(this.container, ed.dom.create('img', img_args));
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
				tinyMCEPopup.confirm(tinyMCEPopup.getLang('advimage_dlg.missing_alt'), function(s) {
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
		var cap_args = {};
		var cont_args = {};
		var el;

		tinyMCEPopup.restoreSelection();

		// Fixes crash in Safari
		if (tinymce.isWebKit) ed.getWin().focus();

		var align = getSelectValue(f, 'align');
		var id = nl.id;
        var caption = nl.caption.value;
		tinymce.extend(img_args, {
			src: nl.src.value,
			width: nl.width.value,
			height: nl.height.value,
			alt: nl.alt.value,
			title: nl.title.value,
			'class': nl.classes.value,
			id: '__mce_tmp'
		});
        tinymce.extend(cap_args, {
            'class': 'mce_image_caption'
        });
        tinymce.extend(cont_args, {
            'class': 'mce_image_container mceItemVisualAid',
            id: '__mce_tmp_1'
        });
		if (el) {
			this.updateImageContainer(cont_args, img_args, cap_args, caption);
		} else {
		    try{
		        this.createImageContainer(cont_args, img_args, cap_args, caption);
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

	getAttrib: function(e, at) {
		var ed = tinyMCEPopup.editor,
			dom = ed.dom,
			v, v2;

		if (ed.settings.inline_styles) {
			switch (at) {
			case 'align':
				if (v = dom.getStyle(e, 'float')) return v;

				if (v = dom.getStyle(e, 'vertical-align')) return v;

				break;

			case 'hspace':
				v = dom.getStyle(e, 'margin-left')
				v2 = dom.getStyle(e, 'margin-right');

				if (v && v == v2) return parseInt(v.replace(/[^0-9]/g, ''));

				break;

			case 'vspace':
				v = dom.getStyle(e, 'margin-top')
				v2 = dom.getStyle(e, 'margin-bottom');
				if (v && v == v2) return parseInt(v.replace(/[^0-9]/g, ''));

				break;

			case 'border':
				v = 0;

				tinymce.each(['top', 'right', 'bottom', 'left'], function(sv) {
					sv = dom.getStyle(e, 'border-' + sv + '-width');

					// False or not the same as prev
					if (!sv || (sv != v && v !== 0)) {
						v = 0;
						return false;
					}

					if (sv) v = sv;
				});

				if (v) return parseInt(v.replace(/[^0-9]/g, ''));

				break;
			}
		}

		if (v = dom.getAttrib(e, at)) return v;

		return '';
	},

	setSwapImage: function(st) {
		var f = document.forms[0];

		f.onmousemovecheck.checked = st;
		setBrowserDisabled('overbrowser', !st);
		setBrowserDisabled('outbrowser', !st);

		if (f.over_list) f.over_list.disabled = !st;

		if (f.out_list) f.out_list.disabled = !st;

		f.onmouseoversrc.disabled = !st;
		f.onmouseoutsrc.disabled = !st;
	},

	fillClassList: function(id) {
		var dom = tinyMCEPopup.dom,
			lst = dom.get(id),
			v, cl;

		if (v = tinyMCEPopup.getParam('theme_advanced_styles')) {
			cl = [];

			tinymce.each(v.split(';'), function(v) {
				var p = v.split('=');

				cl.push({
					'title': p[0],
					'class': p[1]
				});
			});
		} else cl = tinyMCEPopup.editor.dom.getClasses();

		if (cl.length > 0) {
			lst.options.length = 0;
			lst.options[lst.options.length] = new Option(tinyMCEPopup.getLang('not_set'), '');

			tinymce.each(cl, function(o) {
				lst.options[lst.options.length] = new Option(o.title || o['class'], o['class']);
			});
		} else dom.remove(dom.getParent(id, 'tr'));
	},

	fillFileList: function(id, l) {
		var dom = tinyMCEPopup.dom,
			lst = dom.get(id),
			v, cl;

		l = window[l];
		lst.options.length = 0;

		if (l && l.length > 0) {
			lst.options[lst.options.length] = new Option('', '');

			tinymce.each(l, function(o) {
				lst.options[lst.options.length] = new Option(o[0], o[1]);
			});
		} else dom.remove(dom.getParent(id, 'tr'));
	},

	resetImageData: function() {
		var f = document.forms[0];

		f.elements.width.value = f.elements.height.value = '';
	},

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
			if (ed.getParam('inline_styles')) {
				ed.dom.setAttrib(img, 'style', f.style.value);
			} else {
				img.align = f.align.value;
				img.border = f.border.value;
				img.hspace = f.hspace.value;
				img.vspace = f.vspace.value;
			}
		}
	},

	changeHeight: function() {
		var f = document.forms[0],
			tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "") return;

		tp = (parseInt(f.width.value) / parseInt(t.preloadImg.width)) * t.preloadImg.height;
		f.height.value = tp.toFixed(0);
	},

	changeWidth: function() {
		var f = document.forms[0],
			tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "") return;

		tp = (parseInt(f.height.value) / parseInt(t.preloadImg.height)) * t.preloadImg.width;
		f.width.value = tp.toFixed(0);
	},

	updateStyle: function(ty) {
		// var dom = tinyMCEPopup.dom;
		// var st;
		// var v;
		// var f = document.forms[0];
		// var img = dom.create('img', {style : dom.get('style').value});
		// 
		// if (tinyMCEPopup.editor.settings.inline_styles) {
		//  // Handle align
		//  if (ty == 'align') {
		//      dom.setStyle(img, 'float', '');
		//      dom.setStyle(img, 'vertical-align', '');
		// 
		//      v = getSelectValue(f, 'align');
		//      if (v) {
		//          if (v == 'left' || v == 'right')
		//              dom.setStyle(img, 'float', v);
		//          else
		//              img.style.verticalAlign = v;
		//      }
		//  }
		// 
		//  // Handle border
		//  if (ty == 'border') {
		//      dom.setStyle(img, 'border', '');
		// 
		//      v = f.border.value;
		//      if (v || v == '0') {
		//          if (v == '0')
		//              img.style.border = '0';
		//          else
		//              img.style.border = v + 'px solid black';
		//      }
		//  }
		// 
		//  // Handle hspace
		//  if (ty == 'hspace') {
		//      dom.setStyle(img, 'marginLeft', '');
		//      dom.setStyle(img, 'marginRight', '');
		// 
		//      v = f.hspace.value;
		//      if (v) {
		//          img.style.marginLeft = v + 'px';
		//          img.style.marginRight = v + 'px';
		//      }
		//  }
		// 
		//  // Handle vspace
		//  if (ty == 'vspace') {
		//      dom.setStyle(img, 'marginTop', '');
		//      dom.setStyle(img, 'marginBottom', '');
		// 
		//      v = f.vspace.value;
		//      if (v) {
		//          img.style.marginTop = v + 'px';
		//          img.style.marginBottom = v + 'px';
		//      }
		//  }
		// 
		//  // Merge
		//  dom.get('style').value = dom.serializeStyle(dom.parseStyle(img.style.cssText), 'img');
		// }
	},

	changeMouseMove: function() {},

	showPreviewImage: function(u, st) {
		if (!u) {
			tinyMCEPopup.dom.setHTML('prev', '');
			return;
		}

		if (!st && tinyMCEPopup.getParam("advimage_update_dimensions_onchange", true)) this.resetImageData();

		u = tinyMCEPopup.editor.documentBaseURI.toAbsolute(u);

		if (!st) tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this);" onerror="ImageDialog.resetImageData();" />');
		else tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this, 1);" />');
	}
};

ImageDialog.preInit();
tinyMCEPopup.onInit.add(ImageDialog.init, ImageDialog);
