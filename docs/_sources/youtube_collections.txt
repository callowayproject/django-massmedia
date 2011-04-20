====================
You Tube Collections
====================

In version 0.8 preliminary support for external services was added. The first service supported was creating a :class:`Collection` of a youtube.com playlist.

Creating a collection from a YouTube playlist **will not import the videos** on the playlist. Because you can change the playlist independently of the Django admin interface, it would be difficult to keep it in sync with YouTube. It is easy to use the Google YouTube API to get all the videos dynamically. See :ref:`youtube_collections_and_templates`\ .

Settings
========

The YouTube API requires 3 settings, ``EMAIL``\ , ``USERNAME``\ , ``PASSWORD``:

.. code-block:: python

   MASSMEDIA_SERVICES = {
       'YOUTUBE': {
           'EMAIL': '',
           'USERNAME': '',
           'PASSWORD': '',
       },
   }

Getting the playlist URL
========================

YouTube has several different URLs that reference the playlist, depending on how you get to the playlist page.

User's playlist page
********************

If you go to any user's page and click on the "Playlists" button

.. image:: images/playlist_tab.png

you can select a playlist from the list on the right.

.. image:: images/playlist_list.png

The address bar address will change to look similar to::

	http://www.youtube.com/washingtontimes#p/c/4A35EB2544D73557

Playlist management page
************************

If you go to **My Videos & Playlists**

.. image:: images/myplaylists.png

and select **Playlists** from the list on the left.

.. image:: images/playlists.png

You can use the **Link:** field URL; which is formatted like::

	http://www.youtube.com/view_play_list?p=4A35EB2544D73557

If you look at the URL in the **Embed:** field, it contains a URL like::

	http://www.youtube.com/p/4A35EB2544D73557?hl=en_US&amp;fs=1

This URL requires you to chop off the question mark and everything after it::

	http://www.youtube.com/p/4A35EB2544D73557

Creating the Collection
=======================

1. Create a new :class:`Collection` object in the admin.

2. Give the new collection a name

3. Enter the playlist URL retrieved earlier into the **External URL** field.

4. Select the **Site**.

5. Save.

For information on displaying the collection, see :ref:`youtube_collections_and_templates`\ .