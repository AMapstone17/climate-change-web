"""
Contains a dataclass that can be used to test forms in the application.
"""

from dataclasses import dataclass


@dataclass
class BaseFormData:
    """
    A base dataclass for form data. This class should be inherited by other form dataclasses.
    """
    expected: bool
    submit: bool = True

    def to_data(self, strip_fields=None):
        """Convert the dataclass to a dictionary to be used in form validation."""
        if strip_fields is None:
            strip_fields = []
        return {
            k: v for k, v in self.__dict__.items()
            if k != 'expected' and not k.startswith('_') and k not in strip_fields
        }
