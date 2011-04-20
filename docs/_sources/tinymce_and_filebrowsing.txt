========================
TinyMCE and Filebrowsing
========================


Add to project settings::

	TINYMCE_FILEBROWSER = True

In TINYMCE_DEFAULT_CONFIG add::

    extended_valid_elements "-p[class|style]," and "-div[class|style],"

Create two URL definitions::

	url(r'^browse/', 'massmedia.views.browse', name="fb_browse"),
	url(r'^tinymcepopup$', 'massmedia.views.tinymcepopup_url', name="tinymcepopupurl"),

