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
    Decorator that reloads `new_records` with select_related() before handler runs.
    Supports instance methods (skips 'self') and normal functions.
    """

    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if "new_records" not in bound.arguments:
                raise TypeError(
                    "@select_related requires a 'new_records' named argument"
                )

            new_records = bound.arguments["new_records"]

            if not isinstance(new_records, list):
                raise TypeError(
                    f"@select_related expects a list of model instances for `new_records`, got {type(new_records)}"
                )

            if not new_records:
                return func(*args, **kwargs)

            model_cls = new_records[0].__class__
            ids = [obj.pk for obj in new_records]
            reloaded = list(
                model_cls.objects.select_related(*related_fields).filter(pk__in=ids)
            )

            # Replace new_records
            bound.arguments["new_records"] = reloaded
            return func(*bound.args, **bound.kwargs)

        return wrapper

    return decorator
