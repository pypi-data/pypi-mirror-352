from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe

import nh3


def get_nh3_default_options():
    nh3_args = {}
    nh3_settings = {
        "NH3_ALLOWED_TAGS": "tags",
        "NH3_ALLOWED_ATTRIBUTES": "attributes",
        "NH3_STRIP_COMMENTS": "strip_comments",
        "NH3_URL_SCHEMES": "url_schemes",
        "NH3_ATTRIBUTE_FILTER": "attribute_filter",
        "NH3_LINK_REL": "link_rel",
        "NH3_GENERIC_ATTRIBUTE_PREFIXES": "generic_attribute_prefixes",
        "NH3_TAG_ATTRIBUTE_VALUES": "tag_attribute_values",
        "NH3_SET_TAG_ATTRIBUTE_VALUES": "set_tag_attribute_values",
    }

    for setting, kwarg in nh3_settings.items():
        if hasattr(settings, setting):
            attr = getattr(settings, setting)
            nh3_args[kwarg] = attr

    return nh3_args


class NH3Field(models.TextField):
    def __init__(
        self,
        allowed_tags=None,
        allowed_attributes=None,
        url_schemes=None,
        strip_comments=None,
        attribute_filter=None,
        link_rel=None,
        generic_attribute_prefixes=None,
        tag_attribute_values=None,
        set_tag_attribute_values=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.nh3_kwargs = get_nh3_default_options()

        if allowed_tags:
            self.nh3_kwargs["tags"] = allowed_tags
        if allowed_attributes:
            self.nh3_kwargs["attributes"] = allowed_attributes
        if url_schemes:
            self.nh3_kwargs["url_schemes"] = url_schemes
        if strip_comments:
            self.nh3_kwargs["strip_comments"] = strip_comments
        if attribute_filter:
            self.nh3_kwargs["attribute_filter"] = attribute_filter
        if link_rel:
            self.nh3_kwargs["link_rel"] = link_rel
        if generic_attribute_prefixes:
            self.nh3_kwargs["generic_attribute_prefixes"] = (
                generic_attribute_prefixes)
        if tag_attribute_values:
            self.nh3_kwargs["tag_attribute_values"] = tag_attribute_values
        if set_tag_attribute_values:
            self.nh3_kwargs["set_tag_attribute_values"] = (
                set_tag_attribute_values)

    def pre_save(self, model_instance, add):
        data = getattr(model_instance, self.attname)
        if data is None:
            return data
        clean_value = nh3.clean(data, **self.nh3_kwargs) if data else ""
        setattr(model_instance, self.attname, mark_safe(clean_value))
        return clean_value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Values are sanitised before saving, so any value returned from the DB
        # is safe to render unescaped.
        return mark_safe(value)
