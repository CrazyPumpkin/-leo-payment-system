import six
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from import_export import fields, widgets
from import_export.resources import ModelResource, ModelDeclarativeMetaclass


class CustomModelResourceMetaclass(ModelDeclarativeMetaclass):
    def __new__(cls, *args, **kwargs):
        new_class = super(CustomModelResourceMetaclass, cls).__new__(cls, *args, **kwargs)
        CustomModelResource = globals().get("CustomModelResource", None)
        if CustomModelResource and issubclass(new_class, CustomModelResource):
            opts = new_class._meta

            # Setup choice fields
            for field_name in opts.choice_fields:
                new_class.fields[field_name] = fields.Field(
                    attribute='get_%s_display' % field_name,
                    column_name=field_name
                )

            # Setup str fields
            for field_name in opts.str_fields:
                new_class.fields[field_name].widget = widgets.CharWidget()
        return new_class


class CustomModelResource(six.with_metaclass(CustomModelResourceMetaclass, ModelResource)):
    """
    Add new meta-options:

    :parameter choice_fields: list of fields that should be interpreted as ChoiceField
    :parameter str_field: list of fields that should be interpreted as string (usually is used for relation fields)
    :parameter summary_filter: filter row before aggregate
    :parameter summary_fields: sum field values and add them into to summary row
    """

    class Meta:
        model = None
        choice_fields = ()
        str_fields = ()
        summary_fields = ()

    def get_export_headers(self):
        headers = []
        # Replace headers to verbose names
        for field in self.get_fields():
            header = ''
            try:
                header = self.Meta.model._meta.get_field(field.column_name).verbose_name
            except FieldDoesNotExist:
                attr = getattr(self.Meta.model, field.column_name, None)
                if attr is not None:
                    if isinstance(attr, property):
                        header = getattr(attr.fget, 'short_description', '')
                    else:
                        header = getattr(attr, 'short_description', '')
            finally:
                headers.append(header or field.column_name)
        return headers

    def after_export(self, queryset, data, *args, **kwargs):
        export_fields = self.get_export_fields()[1:]
        sum_fields = self._meta.summary_fields
        sum_filter = self._meta.summary_filter or (lambda qs: qs)
        if sum_fields:
            # Add summary row
            sums = sum_filter(queryset).aggregate(**{field: Sum(field) for field in sum_fields})
            row = [_("Итого:")] + [sums.get(field.column_name, '') for field in export_fields]
            data.append(row)
        return data
