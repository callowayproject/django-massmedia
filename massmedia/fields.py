from django.db import models
from django.utils.simplejson import dumps, loads
from django.utils import simplejson

import datetime, time, re

class SerializedObjectField(models.TextField):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        self.decoder = kwargs.pop('decoder', None)
        self.encoder = kwargs.pop('encoder', None)
        super(SerializedObjectField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        try:
            if self.decoder:
                return loads(str(value), cls=self.decoder)
            else:
                return loads(str(value))
        except Exception, e:
            # If an error was raised, just return the plain value
            return value
    
    def get_db_prep_save(self, value, *args, **kwargs):
        if value is not None:# and not isinstance(value, SerializedObject):
            if self.encoder:
                try:
                    value = self.encoder().encode(value)
                except UnicodeDecodeError:
                    return '{}'
            else:
                value = dumps(value)
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

class Metadata():
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
        return self._data.has_key(key)
    
    def __contains__(self, value):
        return value in self._data
    
    def items(self):
        return self._data.items()
    
    def as_json(self):
        result = {}
        for key, value in self._data.items():
            if isinstance(value, datetime.datetime):
                result[key] =  'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))'%(value.year, value.month, value.day,value.hour,value.minute,value.second)
            elif isinstance(value, datetime.date):
                result[key] = 'new Date(Date.UTC(%d,%d,%d))'%(value.year, value.month, value.day)
            elif isinstance(value, time.struct_time):
                result[key] =  'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))'%(value.tm_year, value.tm_mon, value.tm_mday, value.tm_hour, value.tm_min, value.tm_sec)
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
                    result[key] = datetime.datetime(*(simplejson.loads('[%s]'%m.group(1))))
                if n:
                    vals = n.group(1).split(':')
                    result[key] = datetime.timedelta(hours=int(vals[0]),minutes=int(vals[1]),seconds=float(vals[2]))
                
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
            return 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))'%(value.year, value.month, value.day,value.hour,value.minute,value.second)
        elif isinstance(value, datetime.date):
            return 'new Date(Date.UTC(%d,%d,%d))'%(value.year, value.month, value.day)
        elif isinstance(value, time.struct_time):
            return 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d))'%(value.tm_year, value.tm_mon, value.tm_mday, value.tm_hour, value.tm_min, value.tm_sec)
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

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^massmedia\.fields\.SerializedObjectField"])
except ImportError:
    pass
    