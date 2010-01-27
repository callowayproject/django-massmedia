
from django.db import models

#try:
#    from cPickle import dumps, loads
#except ImportError:
#    from pickle import dumps, loads
    
from django.utils.simplejson import dumps, loads    

# class SerializedObject(str):
#     """A subclass of string so it can be told whether a string is
#        a pickled object or not (if the object is an instance of this class
#        then it must [well, should] be a pickled one)."""
#     pass

class SerializedObjectField(models.TextField):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        # if isinstance(value, SerializedObject):
        #     # If the value is a definite pickle; and an error is raised in de-pickling
        #     # it should be allowed to propogate.
        #     return loads(str(value))
        # else:
        try:
            return loads(str(value))
        except:
                # If an error was raised, just return the plain value
            return value

    def get_db_prep_save(self, value):
            if value is not None:# and not isinstance(value, SerializedObject):
                value = dumps(value)
            return str(value)
    
    def get_internal_type(self): 
            return 'TextField'
    
    def get_db_prep_lookup(self, lookup_type, value):
            if lookup_type == 'exact':
                value = self.get_db_prep_save(value)
                return super(SerializedObjectField, self).get_db_prep_lookup(lookup_type, value)
            elif lookup_type == 'in':
                value = [self.get_db_prep_save(v) for v in value]
                return super(SerializedObjectField, self).get_db_prep_lookup(lookup_type, value)
            else:
                raise TypeError('Lookup type %s is not supported.' % lookup_type)

