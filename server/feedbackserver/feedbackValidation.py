from django.forms import ModelForm
from tastypie.bundle import Bundle
from django.forms.models import modelform_factory
from django.forms.models import ModelChoiceField
from tastypie.validation import FormValidation
import logging

"""
Solved FormValidation with URIs converted to PKs for ModelForms (needed for ToOneFields
and ToManyFields). Posted by fabiambuechler and shibz related to django-tastypie/issues/152.
"""

class ModelFormValidation(FormValidation):
    """
    Override tastypie's standard ``FormValidation`` since this does not care
    about URI to PK conversion for ``ToOneField`` or ``ToManyField``.
    """

    def uri_to_pk(self, uri):
        """
        Returns the integer PK part of a URI.

        Assumes ``/api/v1/resource/123/`` format. If conversion fails, this just
        returns the URI unmodified.

        Also handles lists of URIs
        """

        if uri is None:
            return None

        # convert everything to lists
        multiple = not isinstance(uri, basestring)
        uris = uri if multiple else [uri]

        # handle all passed URIs
        converted = []
        for one_uri in uris:
            logging.info(one_uri)
            try:
                # hopefully /api/v1/<resource_name>/<pk>/
                converted.append(int(one_uri.split('/')[-2]))
            except (IndexError, ValueError):
                raise ValueError(
                    "URI %s could not be converted to PK integer." % one_uri)

        # convert back to original format
        return converted if multiple else converted[0]


    def is_valid(self, bundle, request=None):
        data = bundle.data

        # Ensure we get a bound Form, regardless of the state of the bundle.
        if data is None:
            data = {}
        # copy data, so we don't modify the bundle
        data = data.copy()

        # convert URIs to PK integers for all relation fields
        relation_fields = [name for name, field in
                        self.form_class.base_fields.items()
                        if issubclass(field.__class__, ModelChoiceField)]



        includeFields = set(name for name, field in
                        self.form_class.base_fields.items())
        for field in relation_fields:
            if field in data :
                if (isinstance(data[field], dict) or (isinstance(data[field], Bundle))):
                    includeFields.remove(field)
                elif (isinstance(data[field], list)) and (len(data[field]) > 0) and ((isinstance(data[field][0], dict)) or
                (isinstance(data[field][0], Bundle))):
                    includeFields.remove(field)
                else:
                    data[field] = self.uri_to_pk(data[field])

        ExcludedModelForm = modelform_factory(bundle.obj.__class__, form=self.form_class, fields=includeFields)
        # validate and return messages on error
        if request.method == 'POST':
            form = ExcludedModelForm(data)
        elif request.method == 'PUT':
            form = ExcludedModelForm(data, instance=bundle.obj)
        if form.is_valid():
            return {}
        return {"element": bundle.obj.__class__.__name__ , "errors":form.errors}




