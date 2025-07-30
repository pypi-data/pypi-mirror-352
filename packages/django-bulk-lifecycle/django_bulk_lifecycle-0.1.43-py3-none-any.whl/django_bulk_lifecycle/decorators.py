import inspect

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
    def decorator(handler_func):
        def wrapper(*args, **kwargs):
            # Determine whether it's a bound method
            sig = inspect.signature(handler_func)
            parameters = list(sig.parameters.keys())
            has_self = parameters[0] == "self"

            # Adjust index depending on presence of self
            instance_list_idx = 1 if has_self else 0

            if len(args) <= instance_list_idx:
                raise TypeError("@select_related requires a list of model instances as an argument")

            instances = args[instance_list_idx]

            if not isinstance(instances, list):
                raise TypeError(
                    f"@select_related expects a list of model instances, got {type(instances)}"
                )

            if not instances:
                return handler_func(*args, **kwargs)

            model = instances[0].__class__
            ids = [obj.pk for obj in instances]
            preloaded = list(
                model.objects.select_related(*related_fields).filter(pk__in=ids)
            )

            # Replace the instances list in args
            new_args = list(args)
            new_args[instance_list_idx] = preloaded
            return handler_func(*new_args, **kwargs)

        return wrapper
    return decorator