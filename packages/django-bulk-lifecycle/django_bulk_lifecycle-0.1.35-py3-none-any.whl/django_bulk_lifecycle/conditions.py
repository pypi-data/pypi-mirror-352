import logging

logger = logging.getLogger(__name__)


class HookCondition:
    def check(self, instance, original_instance=None):
        raise NotImplementedError

    def __call__(self, instance, original_instance=None):
        return self.check(instance, original_instance)

    def __and__(self, other):
        return AndCondition(self, other)

    def __or__(self, other):
        return OrCondition(self, other)

    def __invert__(self):
        return NotCondition(self)


class WhenFieldValueIsNot(HookCondition):
    def __init__(self, field, unexpected_value, only_on_change=False):
        self.field = field
        self.unexpected_value = unexpected_value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        current = getattr(instance, self.field)
        logger.debug("%s current=%r, original=%r",
                     self.field,
                     current,
                     getattr(original_instance, self.field, None))
        if self.only_on_change:
            if original_instance is None:
                return False
            previous = getattr(original_instance, self.field)
            return previous == self.unexpected_value and current != self.unexpected_value
        else:
            return current != self.unexpected_value


class WhenFieldValueIs(HookCondition):
    def __init__(self, field, expected_value, only_on_change=False):
        self.field = field
        self.expected_value = expected_value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        current = getattr(instance, self.field)
        logger.debug("%s current=%r, original=%r",
                     self.field,
                     current,
                     getattr(original_instance, self.field, None))
        if self.only_on_change:
            if original_instance is None:
                return False
            previous = getattr(original_instance, self.field)
            return previous != self.expected_value and current == self.expected_value
        else:
            return current == self.expected_value


class WhenFieldHasChanged(HookCondition):
    def __init__(self, field, has_changed=True):
        self.field = field
        self.has_changed = has_changed

    def check(self, instance, original_instance=None):
        if not original_instance:
            return False
        return (getattr(instance, self.field) != getattr(original_instance, self.field)) == self.has_changed


class WhenFieldValueWas(HookCondition):
    def __init__(self, field, expected_value, only_on_change=False):
        """
        Check if a field's original value was `expected_value`.
        If only_on_change is True, only return True when the field has changed away from that value.
        """
        self.field = field
        self.expected_value = expected_value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        if original_instance is None:
            return False
        previous = getattr(original_instance, self.field)
        if self.only_on_change:
            current = getattr(instance, self.field)
            return previous == self.expected_value and current != self.expected_value
        else:
            return previous == self.expected_value


class WhenFieldValueChangesTo(HookCondition):
    def __init__(self, field, expected_value):
        """
        Check if a field's value has changed to `expected_value`.
        Only returns True when original value != expected_value and current value == expected_value.
        """
        self.field = field
        self.expected_value = expected_value

    def check(self, instance, original_instance=None):
        if original_instance is None:
            return False
        previous = getattr(original_instance, self.field)
        current = getattr(instance, self.field)
        return previous != self.expected_value and current == self.expected_value


class AndCondition(HookCondition):
    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def check(self, instance, original_instance=None):
        return self.cond1.check(instance, original_instance) and self.cond2.check(instance, original_instance)


class OrCondition(HookCondition):
    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def check(self, instance, original_instance=None):
        return self.cond1.check(instance, original_instance) or self.cond2.check(instance, original_instance)


class NotCondition(HookCondition):
    def __init__(self, cond):
        self.cond = cond

    def check(self, instance, original_instance=None):
        return not self.cond.check(instance, original_instance)
