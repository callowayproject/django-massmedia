.. _media_and_templates:

============================
Rendering media in templates
============================

Each type of media has a customizable template for displaying a thumbnail version and a detail version

They are stored in ``massmedia/mediatypes/``

Templates for each type of media are based on MIME type

Each item looks for a template in this order:

For detail templates::

	massmedia/mediatypes/<base_type>/<specific_type>_detail.html
	massmedia/mediatypes/<base_type>/generic_detail.html
	massmedia/mediatypes/generic_detail.html

For thumbnail templates::

	massmedia/mediatypes/<base_type>/<specific_type>_thumb.html
	massmedia/mediatypes/<base_type>/generic_thumb.html
	massmedia/mediatypes/generic_thumb.html

As an example, an item with a MIME type of ``application/x-shockwave-flash`` would look for its templates in::

	massmedia/mediatypes/application/x-shockwave-flash_detail.html
	massmedia/mediatypes/application/generic_detail.html
	massmedia/mediatypes/generic_detail.html

These templates are only snippets of html for rendering one item and should not contain extra HTML tags (like ``<head>`` or ``<body>``)