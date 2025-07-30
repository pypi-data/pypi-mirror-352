import inspect
from functools import wraps

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
    Decorator for lifecycle hook functions that operate on lists of model instances.
    Automatically re-fetches those instances with select_related applied.
    """

    def decorator(func):
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        if "new_records" not in param_names:
            raise ValueError(
                "@select_related expects a `new_records` argument in the handler signature"
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()

            new_records = bound_args.arguments.get("new_records")
            if not isinstance(new_records, list):
                raise TypeError(
                    f"@select_related expects a list of model instances for `new_records`, got {type(new_records)}"
                )

            if not new_records:
                return func(*args, **kwargs)

            model = new_records[0].__class__
            ids = [obj.pk for obj in new_records]
            preloaded = list(
                model.objects.select_related(*related_fields).filter(pk__in=ids)
            )

            # Replace the new_records arg
            bound_args.arguments["new_records"] = preloaded
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator
