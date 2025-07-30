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


def select_related(*related_fields):
    """
    Decorator to reload a list of model instances with related fields
    using select_related in a single query.
    """

    def decorator(handler_func):
        def wrapper(instances, *args, **kwargs):
            if not instances:
                return handler_func(instances, *args, **kwargs)

            if not isinstance(instances, list):
                raise TypeError(
                    f"@select_related expects a list of model instances, got {type(instances)}"
                )

            model = instances[0].__class__
            ids = [obj.pk for obj in instances]
            instances = list(
                model.objects.select_related(*related_fields).filter(pk__in=ids)
            )

            return handler_func(instances, *args, **kwargs)

        return wrapper

    return decorator
