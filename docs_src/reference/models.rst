======
Models
======

.. module:: massmedia.models
   :synopsis: Storage of various types of media metadata and files

.. autoclass:: massmedia.models.Media
   :members:
   :undoc-members:
   
   .. attribute:: title
      
      ``CharField(max_length 255)`` A headline or short descriptive sentence. Used in creating the slug field.

   .. attribute:: slug

      ``SlugField`` A variation of the title attribute that can be used in URLs. They must be unique.

      ``unique=True``

   .. attribute:: title

      *CharField* A headline or short descriptive sentence. Used in creating the slug field.

      ``max_length=255``


.. autoclass:: massmedia.models.PublicMediaManager
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Image
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Video
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Audio
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Flash
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Document
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.Collection
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.CollectionRelation
   :members:
   :undoc-members:

.. autoclass:: massmedia.models.MediaTemplate
   :members:
   :undoc-members:
