from django.contrib.admin.views.main import ALL_VAR, EMPTY_CHANGELIST_VALUE
from django.contrib.admin.views.main import ORDER_VAR, ORDER_TYPE_VAR, PAGE_VAR, SEARCH_VAR
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import dateformat
from django.utils.html import escape, conditional_escape
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.formats import get_format
from django.utils.encoding import smart_unicode, smart_str, force_unicode
from django.template import Library
import datetime

register = Library()

quo_esc = lambda x: x.replace("'", r"\'")

def thumbnails_for_result(cl, result, form):
    """
    Basically does the same thing as django's items_for_result, but makes all the
    items fit in one <td> element instead of separate elements for each field
    """
    
    first = True
    pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_class = ''
        try:
            f = cl.lookup_opts.get_field(field_name)
        except models.FieldDoesNotExist:
            # For non-field list_display values, the value is either a method,
            # property or returned via a callable.
            try:
                if callable(field_name):
                    attr = field_name
                    value = attr(result)
                elif hasattr(cl.model_admin, field_name) and \
                   not field_name == '__str__' and not field_name == '__unicode__':
                    attr = getattr(cl.model_admin, field_name)
                    value = attr(result)
                else:
                    attr = getattr(result, field_name)
                    if callable(attr):
                        value = attr()
                    else:
                        value = attr
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = smart_unicode(value)
            except (AttributeError, ObjectDoesNotExist):
                result_repr = EMPTY_CHANGELIST_VALUE
            else:
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if not allow_tags:
                    result_repr = escape(result_repr)
                else:
                    result_repr = mark_safe(result_repr)
        else:
            field_val = getattr(result, f.attname)

            if isinstance(f.rel, models.ManyToOneRel):
                if field_val is not None:
                    result_repr = escape(getattr(result, f.name))
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
            # Dates and times are special: They're formatted in a certain way.
            elif isinstance(f, models.DateField) or isinstance(f, models.TimeField):
                if field_val:
                    if isinstance(f, models.DateTimeField):
                        result_repr = capfirst(dateformat.format(field_val, get_format('DATETIME_FORMAT')))
                    elif isinstance(f, models.TimeField):
                        result_repr = capfirst(dateformat.time_format(field_val, get_format('TIME_FORMAT')))
                    else:
                        result_repr = capfirst(dateformat.format(field_val, get_format('DATE_FORMAT')))
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
                row_class = ' class="nowrap"'
            # Booleans are special: We use images.
            elif isinstance(f, models.BooleanField) or isinstance(f, models.NullBooleanField):
                result_repr = _boolean_icon(field_val)
            # DecimalFields are special: Zero-pad the decimals.
            elif isinstance(f, models.DecimalField):
                if field_val is not None:
                    result_repr = ('%%.%sf' % f.decimal_places) % field_val
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
            # Fields with choices are special: Use the representation
            # of the choice.
            elif f.flatchoices:
                result_repr = dict(f.flatchoices).get(field_val, EMPTY_CHANGELIST_VALUE)
            else:
                result_repr = escape(field_val)
        if force_unicode(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        # If list_display_links not defined, add the link tag to the first field
        if (first and not cl.list_display_links) or field_name in cl.list_display_links:
            table_tag = {True:'th', False:'td'}[first]
            first = False
            url = cl.url_for_result(result)
            # Convert the pk to something that can be used in Javascript.
            # Problem cases are long ints (23L) and non-ASCII strings.
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = pk
            value = result.serializable_value(attr)
            result_id = repr(force_unicode(value))[1:]
            if cl.is_popup and cl.params['pop'] == u'2':
                yield mark_safe(u'<a href="%s"%s>%s</a>' % \
                ('#', (cl.is_popup and ' onclick="FileBrowserDialogue.fileSubmit(\'%s\', \'%s\', \'%s\'); return false;"' % (result.media_url or '', quo_esc(result.caption) or '', result.get_absolute_url())), conditional_escape(result_repr)))
                #(url, (cl.is_popup and ' onclick="FileBrowserDialogue.fileSubmit(\'%s\'); return false;"' % result.get_absolute_url() or ''), conditional_escape(result_repr)))
            else:
                yield mark_safe(u'<a href="%s"%s>%s</a>' % \
                (url, (cl.is_popup and ' onclick="opener.dismissRelatedLookupPopup(window, %s); return false;"' % result_id or ''), conditional_escape(result_repr)))
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if form and field_name in form.fields:
                bf = form[field_name]
                result_repr = mark_safe(force_unicode(bf.errors) + force_unicode(bf))
            else:
                result_repr = conditional_escape(result_repr)
            yield mark_safe(u'%s' % (result_repr))
    if form:
        yield mark_safe(force_unicode(form[cl.model._meta.pk.name]))
    

def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield list(thumbnails_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield list(thumbnails_for_result(cl, res, None))

def thumbnail_result_list(context, cl):
    if context.has_key('STATIC_URL'):
        static_url = 'STATIC_URL'
    else:
        static_url = 'MEDIA_URL'
    result_list = list(results(cl))
    if len(result_list) % 4:
        empty_spaces = range(4 - (len(result_list) % 4))
    else:
        empty_spaces = []
    return {'cl': cl,
            'results': result_list,
            'empty_spaces': empty_spaces,
            'STATIC_URL': context[static_url]}
thumbnail_result_list = register.inclusion_tag("admin/massmedia/change_list_results.html", takes_context=True)(thumbnail_result_list)
