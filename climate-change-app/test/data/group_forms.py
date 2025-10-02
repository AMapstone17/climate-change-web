"""
Contains data classes for group forms.
"""

from dataclasses import dataclass

from test.data.base_form import BaseFormData


@dataclass
class CreateGroupFormData(BaseFormData):
    title: str = 'Group Title'
    description: str = 'Group Description'
    location: str = 'Group Location'
    event_date: str = '01-01-2024 12:00'
