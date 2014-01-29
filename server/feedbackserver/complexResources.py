from django.core.exceptions import ObjectDoesNotExist
from tastypie.resources import ModelResource
from tastypie.bundle import Bundle
import logging
class ComplexModelResource(ModelResource):


    def save_related(self, bundle):
        """
        Handles the saving of related non-M2M data.

        Calling assigning ``child.parent = parent`` & then calling
        ``Child.save`` isn't good enough to make sure the ``parent``
        is saved.

        To get around this, we go through all our related fields &
        call ``save`` on them if they have related, non-M2M data.
        M2M data is handled by the ``ModelResource.save_m2m`` method.
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_related', False):
                continue

            if getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.blank:
                continue

            # Get the object.
            try:
                related_obj = getattr(bundle.obj, field_object.attribute)
            except ObjectDoesNotExist:
                related_obj = None

            resource = field_object.to_class()
            # Because sometimes it's ``None`` & that's OK.
            if related_obj:
                related_data = bundle.data.get(field_object.attribute, None)

                if not hasattr(related_data, 'get'):
                    # We only care about data that is dict-like
                    related_data = None
                if related_data:
                    related_bundle = Bundle(obj=related_obj, request=bundle.request, data=related_data)
                    # Need a failing test for this line
                    resource.save_related(related_bundle)
                    resource.is_valid(related_bundle, bundle.request)
                related_obj.save()
                setattr(bundle.obj, field_object.attribute, related_obj)
                if related_data:
                    #Not everything is fully hydrated in one go. Do it again.
                    related_bundle = resource.full_hydrate(related_bundle)
                    m2m_bundle = resource.hydrate_m2m(related_bundle)
                    resource.save_m2m(m2m_bundle)

    def save_m2m(self, bundle):
        """
        Handles the saving of related M2M data.

        Due to the way Django works, the M2M data must be handled after the
        main instance, which is why this isn't a part of the main ``save`` bits.

        Currently slightly inefficient in that it will clear out the whole
        relation and recreate the related data as needed.
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.readonly:
                continue

            # Get the manager.
            related_mngr = getattr(bundle.obj, field_object.attribute)

            if hasattr(related_mngr, 'clear'):
                # Clear it out, just to be safe.
                related_mngr.clear()

            resource = field_object.to_class()

            related_objs = []
            for related_bundle in bundle.data[field_name]:
                resource.save_related(related_bundle)
                resource.is_valid(related_bundle, bundle.request)
                related_bundle.obj.save()
                m2m_bundle = resource.hydrate_m2m(related_bundle)
                resource.save_m2m(m2m_bundle)
                related_objs.append(related_bundle.obj)

            related_mngr.add(*related_objs)