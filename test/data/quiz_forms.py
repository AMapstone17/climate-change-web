"""
Contains data classes for quiz forms.
"""

from dataclasses import dataclass

from test.data.base_form import BaseFormData


@dataclass
class QuizFormData(BaseFormData):
    option: int = 0
