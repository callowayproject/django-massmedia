========================
TinyMCE and Filebrowsing
========================


Add to project settings::

	TINYMCE_FILEBROWSER = True

In TINYMCE_DEFAULT_CONFIG add::

    extended_valid_elements "-p[class|style]," and "-div[class|style],"

Create URL definition::

	url(r'^browse/', 'massmedia.views.browse', name="fb_browse"),

