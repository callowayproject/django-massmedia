import datetime
import re
import time
import six

from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import SlugField

try:
    from django.utils.encoding import force_unicode  # NOQA
except ImportError:
    from django.utils.encoding import force_text as force_unicode  # NOQA

import simplejson


class SerializedObjectField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.decoder = kwargs.pop('decoder', None)
        self.encoder = kwargs.pop('encoder', None)
        super(SerializedObjectField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            if self.decoder:
                return simplejson.loads(str(value), cls=self.decoder)
            else:
                return simplejson.loads(str(value))
        except Exception:
            # If an error was raised, just return the plain value
            return value

    def get_db_prep_save(self, value, *args, **kwargs):
        if value is not None:  # and not isinstance(value, SerializedObject):
            if self.encoder:
                try:
                    value = self.encoder().encode(value)
                except UnicodeDecodeError:
                    return '{}'
            else:
                value = simplejson.dumps(value)
        return str(value)

    def get_internal_type(self):
        return 'TextField'

    def get_db_prep_lookup(self, lookup_type, value, *args, **kwargs):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(SerializedObjectField, self).get_db_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(SerializedObjectField, self).get_db_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)


class Metadata(object):
    _data = {}

    def __init__(self, initial={}, **kwargs):
        self._data = {}
        for key, value in initial.items():
            self._data[str(key)] = value

    def __getitem__(self, name):
        if name in self._data.keys():
            return self._data[str(name)]
        else:
            return None

    def __setitem__(self, name, value):
        if name == '_data':
            self._data = value.copy()
        else:
            self._data[str(name)] = value

    def iterkeys(self):
        return self._data.__iter__()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def has_key(self, key):
        return key in self._data

    def __contains__(self, value):
        return value in self._data

    def items(self):
        return self._data.items()

    def as_json(self):
        result = {}
        for key, value in self._data.items():
            if isinstance(value, datetime.datetime):
                result[key] = 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))' % (
                    value.year, value.month, value.day, value.hour,
                    value.minute, value.second)
            elif isinstance(value, datetime.date):
                result[key] = 'new Date(Date.UTC(%d,%d,%d))' % (
                    value.year, value.month, value.day)
            elif isinstance(value, time.struct_time):
                result[key] = 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))' % (
                    value.tm_year, value.tm_mon, value.tm_mday, value.tm_hour,
                    value.tm_min, value.tm_sec)
            elif isinstance(value, datetime.timedelta):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def from_json(self, json_str):
        result = simplejson.loads(json_str)
        dt_regex = re.compile(r'^new\sDate\(Date\.UTC\((.*?)\)\)')
        td_regex = re.compile(r'^(\d+:\d+:\d+\.\d+)$')
        for key, value in result.items():
            if isinstance(value, basestring):
                m = dt_regex.match(value)
                n = td_regex.match(value)
                if m:
                    result[key] = datetime.datetime(
                        *(simplejson.loads('[%s]' % m.group(1))))
                if n:
                    vals = n.group(1).split(':')
                    result[key] = datetime.timedelta(
                        hours=int(vals[0]), minutes=int(vals[1]),
                        seconds=float(vals[2]))

        self._data.update(result)

    def __str___(self):
        return str(self.as_json())

    def __unicode__(self):
        return unicode(self.as_json())

    def __repr__(self):
        return str(self.as_json())


class MetadataJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        value = obj
        if isinstance(value, datetime.datetime):
            return 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))' % (
                value.year, value.month, value.day, value.hour,
                value.minute, value.second)
        elif isinstance(value, datetime.date):
            return 'new Date(Date.UTC(%d,%d,%d))' % (
                value.year, value.month, value.day)
        elif isinstance(value, time.struct_time):
            return 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))' % (
                value.tm_year, value.tm_mon, value.tm_mday, value.tm_hour,
                value.tm_min, value.tm_sec)
        elif isinstance(value, datetime.timedelta):
            return str(value)
        elif isinstance(value, Metadata):
            return value.as_json()
        else:
            return super(MetadataJSONEncoder, self).default(value)


class MetadataJSONDecoder(simplejson.JSONDecoder):
    def decode(self, json_str):
        md = Metadata()
        md.from_json(json_str)
        return md


class AutoSlugField(SlugField):
    """ AutoSlugField

    By default, sets editable=False, blank=True.

    Required arguments:

    populate_from
        Specifies which field or list of fields the slug is populated from.

    Optional arguments:

    separator
        Defines the used separator (default: '-')

    overwrite
        If set to True, overwrites the slug on every save (default: False)

    Inspired by SmileyChris' Unique Slugify snippet:
    http://www.djangosnippets.org/snippets/690/
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        populate_from = kwargs.pop('populate_from', 'title')
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from
        self.separator = kwargs.pop('separator', six.u('-'))
        self.overwrite = kwargs.pop('overwrite', False)
        self.allow_duplicates = kwargs.pop('allow_duplicates', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def _slug_strip(self, value):
        """
        Cleans up a slug by removing slug separator characters that occur at
        the beginning or end of a slug.

        If an alternate separator is used, it will also replace any instances
        of the default '-' separator with the new separator.
        """
        re_sep = '(?:-|%s)' % re.escape(self.separator)
        value = re.sub('%s+' % re_sep, self.separator, value)
        return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)

    def get_queryset(self, model_cls, slug_field):
        for field, model in model_cls._meta.get_fields_with_model():
            if model and field == slug_field:
                return model._default_manager.all()
        return model_cls._default_manager.all()

    def slugify_func(self, content):
        if content:
            return slugify(content)
        return ''

    def create_slug(self, model_instance, add):
        # get fields to populate from and slug field to set
        if not isinstance(self._populate_from, (list, tuple)):
            self._populate_from = (self._populate_from, )
        slug_field = model_instance._meta.get_field(self.attname)

        if add or self.overwrite:
            # slugify the original field content and set next step to 2
            slug_for_field = lambda field: self.slugify_func(getattr(model_instance, field))
            slug = self.separator.join(map(slug_for_field, self._populate_from))
            next = 2
        else:
            # get slug from the current model instance
            slug = getattr(model_instance, self.attname)
            # model_instance is being modified, and overwrite is False,
            # so instead of doing anything, just return the current slug
            return slug

        # strip slug depending on max_length attribute of the slug field
        # and clean-up
        slug_len = slug_field.max_length
        if slug_len:
            slug = slug[:slug_len]
        slug = self._slug_strip(slug)
        original_slug = slug

        if self.allow_duplicates:
            return slug

        # exclude the current model instance from the queryset used in finding
        # the next valid slug
        queryset = self.get_queryset(model_instance.__class__, slug_field)
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to impliment any unique_together contraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)
        kwargs[self.attname] = slug

        # increases the number while searching for the next valid slug
        # depending on the given slug, clean-up
        while not slug or queryset.filter(**kwargs):
            slug = original_slug
            end = '%s%s' % (self.separator, next)
            end_len = len(end)
            if slug_len and len(slug) + end_len > slug_len:
                slug = slug[:slug_len - end_len]
                slug = self._slug_strip(slug)
            slug = '%s%s' % (slug, end)
            kwargs[self.attname] = slug
            next += 1
        return slug

    def pre_save(self, model_instance, add):
        value = force_unicode(self.create_slug(model_instance, add))
        setattr(model_instance, self.attname, value)
        return value

    def get_internal_type(self):
        return "SlugField"

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = '%s.AutoSlugField' % self.__module__
        args, kwargs = introspector(self)
        kwargs.update({
            'populate_from': repr(self._populate_from),
            'separator': repr(self.separator),
            'overwrite': repr(self.overwrite),
            'allow_duplicates': repr(self.allow_duplicates),
        })
        # That's our definition!
        return (field_class, args, kwargs)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^massmedia\.fields\.SerializedObjectField"])
except ImportError:
    pass
