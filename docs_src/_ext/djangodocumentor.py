from sphinx.ext import autodoc
import sphinx
from django.db import models
import pprint

DJANGO_FIELDS = (
    models.fields.Field,
    models.fields.related.RelatedField,
    models.fields.related.ForeignRelatedObjectsDescriptor,
    models.fields.related.ReverseManyRelatedObjectsDescriptor,
    models.fields.related.ReverseSingleRelatedObjectDescriptor,
)
class DjangoModelDocumenter(autodoc.ClassDocumenter):
    """
    Specialized Documenter subclass for Django models.
    """
    objtype = 'djangomodel'
    directivetype = 'class'
    
    def get_object_members(self, want_all):
        (members_check_module, members) = super(DjangoModelDocumenter, self).get_object_members(want_all)
        new_members = []
        for name, cls in members:
            print "+++++++++++++++++++++", name
            if name == '_meta':
                for field in cls.fields:
                    print '-----------------------', field.name
                    new_members.append((field.name, field))
            elif cls is not None:
                new_members.append((name, cls))
        return (members_check_module, new_members)
    
class DjangoFieldDocumenter(autodoc.ClassLevelDocumenter):
    objtype = 'djangofield'
    directivetype = 'attribute'
    
    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, DJANGO_FIELDS)

def setup(app):
    app.add_autodocumenter(DjangoModelDocumenter)
    app.add_autodocumenter(DjangoFieldDocumenter)
    #app.connect('autodoc-skip-member', DjangoModelDocumenter.filter_callback)