from django.core.exceptions import FieldDoesNotExist

from django_bulk_lifecycle.enums import DEFAULT_PRIORITY


def hook(event, *, model, condition=None, priority=DEFAULT_PRIORITY):
    """
    Decorator to annotate a method with multiple lifecycle hook registrations.
    If no priority is provided, uses Priority.NORMAL (50).
    """

    def decorator(fn):
        if not hasattr(fn, "lifecycle_hooks"):
            fn.lifecycle_hooks = []
        fn.lifecycle_hooks.append((model, event, condition, priority))
        return fn

    return decorator


def preload_related(instances, *related_fields):
    """
    Preloads the specified `related_fields` onto the given list of model instances
    using select_related(), without replacing the original objects.

    This populates the related fields in-place via the internal Django cache,
    so accessing them later does not trigger additional queries.

    :param instances: List of model instances to preload fields on
    :param related_fields: Related field names to preload (dot-notation not supported)
    """
    if not instances:
        return

    if not isinstance(instances, list):
        raise TypeError(f"Expected a list of model instances, got {type(instances)}")

    model_cls = instances[0].__class__
    ids = [obj.pk for obj in instances if obj.pk is not None]

    if not ids:
        return

    # Fetch with select_related
    preloaded_qs = model_cls.objects.select_related(*related_fields).in_bulk(ids)

    for obj in instances:
        preloaded = preloaded_qs.get(obj.pk)
        if not preloaded:
            continue

        for field in related_fields:
            # Only preload simple (non-nested) relations
            if "." in field:
                raise ValueError(
                    f"Nested select_related fields not supported: '{field}'"
                )

            try:
                # Validate it's a related field
                rel_field = model_cls._meta.get_field(field)
                if not (
                    rel_field.is_relation
                    and not rel_field.many_to_many
                    and not rel_field.one_to_many
                ):
                    continue  # skip non-foreign key or reverse relationships
            except FieldDoesNotExist:
                continue

            try:
                related_obj = getattr(preloaded, field)
                setattr(obj, field, related_obj)
                obj._state.fields_cache[field] = related_obj
            except AttributeError:
                pass
