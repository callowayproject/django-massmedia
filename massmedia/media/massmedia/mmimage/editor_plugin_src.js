/**
 * editor_plugin_src.js
 *
 * Copyright 2009, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://tinymce.moxiecode.com/license
 * Contributing: http://tinymce.moxiecode.com/contributing
 */

(function() {
	tinymce.create('tinymce.plugins.MassmediaImagePlugin', {
		init : function(ed, url) {
			// Register commands
			ed.addCommand('mceMMImage', function() {
				// Internal image object like a flash placeholder
				if (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1)
				    return;

				ed.windowManager.open({
					file : url + '/image.htm',
					width : 480 + parseInt(ed.getLang('mmimage.delta_width', 0), 10),
					height : 480 + parseInt(ed.getLang('mmimage.delta_height', 0), 10),
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register buttons
			ed.addButton('mmimage', {
				title : 'Insert/Edit Image with caption',
				cmd : 'mceMMImage',
				image : url + '/img/mmimage.gif'
			});
		    
		    ed.onNodeChange.add(this._nodeChange, this);
			ed.onVisualAid.add(this._visualAid, this);
		},

        _nodeChange: function(ed, cm, n) {
			var p = ed.dom.getParent(n, 'DIV.mce_image_container');

			if (p) {
				cm.setActive('mmimage', 1);
				ed.selection.select(p);
			} else {
			    cm.setActive('mmimage', 0);
			}
        },
        
        _visualAid : function(ed, e, s) {
            var dom = ed.dom;

			tinymce.each(dom.select('DIV.mce_image_container', e), function(e) {
				if (s)
					dom.addClass(e, 'mceItemVisualAid');
				else
					dom.removeClass(e, 'mceItemVisualAid');	
			});
		},

		getInfo : function() {
			return {
				longname : 'Massmedia Image',
				author : 'Corey Oordt, based on Moxicode',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/advimage',
				version : tinymce.majorVersion + "." + tinymce.minorVersion
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('mmimage', tinymce.plugins.MassmediaImagePlugin);
})();