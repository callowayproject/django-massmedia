.. _youtube_collections_and_templates:

=================================
YouTube Collections and Templates
=================================

mm_youtube template tag library
===============================

The ``mm_youtube`` template tag library handles all the communication with YouTube, plus there are some extra helper tags and filters.

* :ref:`get_youtube_feed`
* :ref:`split`
* :ref:`format_seconds`

.. _get_youtube_feed:

{% get_youtube_feed %}
**********************

**Usage:** ``{% get_youtube_feed <object> as <result> %}``

This tag onverts the :py:class:`massmedia.models.Collection` ``<object>`` into an object with the information about the YouTube playlist. The information is stored in the variable specified as ``<result>``\ . The ``<result>`` object has two attributes: metadata and entries. The metadata contains information about the playlist, and entries is a list of the videos in the playlist.


result.metadata
---------------

**author**
	*Type:* A list of dictionaries containing ``name`` and ``uri`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.author.0.name }}
		{{ result.metadata.author.0.url }}
	
	could result in::
	
		washingtontimes
		http://gdata.youtube.com/feeds/api/users/washingtontimes
	

**category**
	*Type:* A list of strings.
	
	*Example:* 
	
	.. code-block:: django
	
		{% for cat in result.metadata.category %}
		    {{ cat }}
		{% endfor %}
	
	could result in::
	
		http://gdata.youtube.com/schemas/2007#playlist
		washington
		news
		politics
	

**items_per_page**
	*Type:* A string representation of a number for the default number of items retrieved per page.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.items_per_page }}
	
	could result in::
	
		25
	
**link**
	*Type:* A list of dictionaries containing ``href``\ , ``rel``\ , and ``type`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.link.0.href }}
		{{ result.metadata.link.0.rel }}
		{{ result.metadata.link.0.type }}
	
	could result in::
	
		http://www.youtube.com/view_play_list?p=3C046B163FA3957C
		alternate
		text/html
	
	
	*Comment:* Typically there are four links with ``rel`` attributes of:
	
	* ``alternate``
	* ``http://schemas.google.com/g/2005#feed``
	* ``http://schemas.google.com/g/2005#batch``
	* ``self``

**logo**
	*Type:* A string of the URL to the logo set for this playlist.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.logo }}
	
	could result in::
	
		http://www.youtube.com/img/pic_youtubelogo_123x63.gif
	

**playlistId**
	*Type:* A string representing the ID of the playlist.
	
	*Example:*
	
	.. code-block:: django
	
		{{ result.metadata.playlistId }}
	
	could result in::
	
		3C046B163FA3957C
	

**start_index**
	*Type:* A string representation of a item number of a paginated result list.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.start_index }}
	
	could result in::
	
		1
	

**subtitle**
	*Type:* A string of the subtitle of the playlist
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.subtitle }}
	
	could result in::
	
		The best of The Washington Times YouTube Channel
	

**title**
	*Type:* A string of the title of the playlist
	
	*Example:* ::
	
		{{ result.metadata.title }}
	
	could result in::
	
		TWT Home
	

**total_results**
	*Type:* A string representation of the number of items returned.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.total_results }}
	
	could result in::
	
		15
	

**updated**
	*Type:* A string representation of the date this playlist was last modified.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.updated }}
	
	could result in::
	
		2011-04-13T16:37:29.000Z
	
result.entries
--------------

**author**
	*Type:* A list of dictionaries containing ``name`` and ``uri`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.author.0.name }}
		{{ result.entries.0.author.0.url }}
	
	could result in::
	
		washingtontimes
		http://gdata.youtube.com/feeds/api/users/washingtontimes

**category**
	*Type:* A list of strings.
	
	*Example:* 
	
	.. code-block:: django
	
		{% for cat in result.entries.0.category %}
		    {{ cat }}
		{% endfor %}
	
	could result in::
	
		http://gdata.youtube.com/schemas/2007#playlist
		{'label': 'Entertainment', 'term': 'Entertainment'}
		evan rachel wood
		the conspirator
		robert redford
		mildred pierce
		liz glover
		dawne langford
		gucci
		jill stuart
		washington
		d.c.
		ford's theater
	
**comments**
	*Type:* A list of dictionaries containing ``count_hint`` and ``href`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{% for item in result.entries.0.comments %}
		    {{ item.count_hint }}
		    {{ item.href }}
		{% endfor %}
	
	could result in::
	
		0
		http://gdata.youtube.com/feeds/api/videos/DLyt64ZtZcw/comments
	
**content**
	*Type:* A string
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.content }}
	
	could result in::
	
		Liz Glover chats with Evan Rachel Wood at the D.C. Premiere of "The Conspirator."
	

**description**
	*Type:* A string
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.description }}
	
	could result in::
	
		Liz Glover chats with Evan Rachel Wood at the D.C. Premiere of "The Conspirator."
	

**link**
	*Type:* A list of dictionaries containing ``href``\ , ``rel``\ , and ``type`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.link.0.href }}
		{{ result.entries.0.link.0.rel }}
		{{ result.entries.0.link.0.type }}
	
	could result in::
	
		http://www.youtube.com/watch?v=DLyt64ZtZcw&feature=youtube_gdata
		alternate
		text/html
	
	
	*Comment:* Typically there are six links with ``rel`` attributes of:
	
	* ``alternate``
	* ``http://gdata.youtube.com/schemas/2007#video.responses``
	* ``http://gdata.youtube.com/schemas/2007#video.related``
	* ``http://gdata.youtube.com/schemas/2007#mobile``
	* ``related`` 
	* ``self``

**media**
	*Type:* A dictionary.
	
	*Comment:* Because the ``media`` field is complex, each field is discussed separately.

**media.category**
	*Type:* A list of dictionaries with ``label``\ , and ``text`` fields.
	
	*Example:* 
	
	.. code-block:: django
	
		{% for cat in result.entries.0.media.category %}
		    {{ cat.label }}
		    {{ cat.text }}
		{% endfor %}
	
	could result in::
	
		Entertainment
		Entertainment

**media.content**
	*Type:* A list of dictionaries with fields: ``duration``\ , ``expression``\ , ``isDefault``\ , ``medium``\ , ``type``\ , ``url``\ , and ``{http://gdata.youtube.com/schemas/2007}format``\ .
	
	*Example:*
	
	.. code-block:: django
	
		{% for item in result.entries.0.media.content %}
		    {{ item.duration|format_seconds:"i:s" }}
		    {{ item.expression }}
		    {{ item.isDefault }}
		    {{ item.medium }}
		    {{ item.type }}
		    {{ item.url }}
		    {{ item.{http://gdata.youtube.com/schemas/2007}format }}
		    ---------------------------------
		{% endfor %}
	
	could result in::
	
		01:05
		full
		true
		video
		application/x-shockwave-flash
		http://www.youtube.com/v/DLyt64ZtZcw?f=playlists&app=youtube_gdata
		5
		---------------------------------
		01:05
		full
		
		video
		video/3gpp
		rtsp://v4.cache4.c.youtube.com/CiULENy73wIaHAnMZW2G6628DBMYDSANFEgGUglwbGF5bGlzdHMM/0/0/0/video.3gp
		1
		---------------------------------
		01:05
		full
		
		video
		video/3gpp
		rtsp://v4.cache5.c.youtube.com/CiULENy73wIaHAnMZW2G6628DBMYESARFEgGUglwbGF5bGlzdHMM/0/0/0/video.3gp
		6
		---------------------------------
	
**media.description**
	*Type:* A string
	
	*Example:*
	
	.. code-block:: django
	
		{{ result.entries.0.media.description }}
	
	could result in::
	
		Liz Glover chats with Evan Rachel Wood at the D.C. Premiere of "The Conspirator."
	

**media.description**
	*Type:* A string representing the number of seconds of the movie's duration.
	
	*Example:*
	
	.. code-block:: django
	
		{{ result.entries.0.media.duration|format_seconds:"i:s" }}
	
	could result in::
	
		01:05
	

**media.keywords**
	*Type:* string of comma-delimited keywords
	
	*Example:* 
	
	.. code-block:: django
	
		{% split result.entries.0.media.keywords ", " as keywords %}
		{% for i in keywords %}
		    {{ i }}
		{% endfor %}
	
	could result in::
	
		evan rachel wood
		the conspirator
		robert redford
		mildred pierce
		liz glover
		dawne langford
		gucci
		jill stuart
		washington
		d.c.
		ford's theater
	

**media.player**
	*Type:* A URL string
	
	*Example:*
	
	.. code-block:: django
	
		{{ result.entries.0.media.player }}
	
	could result in::
	
		http://www.youtube.com/watch?v=DLyt64ZtZcw&feature=youtube_gdata_player
	
**media.thumbnail**
	*Type:* A list of dictionaries with ``height``\ , ``time``\ , ``url``\ , and ``width``\ .
	
	*Example:*
	
	.. code-block:: django
	
		{% for i in result.entries.0.media.thumbnail %}
		    <img height="{{i.height}}" width="{{i.width}}" src="{{i.url}}" alt="{{time}}">
		{% endfor %}
	
	could result in::
	
		<img height="240" width="320" src="http://i.ytimg.com/vi/DLyt64ZtZcw/0.jpg" alt="00:00:32.500">
		<img height="90" width="120" src="http://i.ytimg.com/vi/DLyt64ZtZcw/1.jpg" alt="00:00:16.250">
		<img height="90" width="120" src="http://i.ytimg.com/vi/DLyt64ZtZcw/2.jpg" alt="00:00:32.500">
		<img height="90" width="120" src="http://i.ytimg.com/vi/DLyt64ZtZcw/3.jpg" alt="00:00:48.750">
	
**media.title**
	*Type:* A string
	
	*Example:*
	
	.. code-block:: django
	
		{{ result.entries.0.media.title }}
	
	could result in::
	
		Evan Rachel Wood at the D.C. Premiere of "The Conspirator"
	

**position**
	*Type:* A string representing the position of the item in the results.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.position }}
	
	could result in::
	
		1
	
**statistics**
	*Type:* A dictionary with fields ``favorite_count`` and ``view_count``\ .
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.statistics.favorite_count }}
		{{ result.entries.0.statistics.view_count }}
	
	could result in::
	
		0
		151
	

**title**
	*Type:* A string
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.entries.0.title }}
	
	could result in::
	
		Evan Rachel Wood at the D.C. Premiere of "The Conspirator"
	

**updated**
	*Type:* A string representation of the date this playlist was last modified.
	
	*Example:* 
	
	.. code-block:: django
	
		{{ result.metadata.updated }}
	
	could result in::
	
		2011-04-13T16:37:29.000Z

.. _split:

{% split %}
***********

**Usage:** ``{% split <string or variable> [<split_str>] as <result> %}``

This tag is useful for converting a string to a list of strings. Without the ``split_str`` parameter, it will split by space.

**Example:**

.. code-block:: django

	{% split "1 2 3 4" as result %} {# result == ['1', '2', '3', '4'] #}
	{% split "1, 2, 3, 4" ", " as result %} {# result == ['1', '2', '3', '4'] #}

	{# assuming commalist == "1,2,3,4" #}
	{% split commalist "," as result %} {# result == ['1', '2', '3', '4'] #}

.. _format_seconds:

format_seconds filter
*********************

**Usage:** ``{{ secondsvar|format_seconds:"i:s"}}``

This filter formats a number of seconds using the format provided. It is the same formatting options for Django's date filter.
