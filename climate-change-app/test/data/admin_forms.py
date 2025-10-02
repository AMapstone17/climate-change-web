"""
This file contains dataclasses for the forms used in the admin panel.
"""

from dataclasses import dataclass
from uuid import UUID

from test.data.base_form import BaseFormData


@dataclass
class AdminQuizQuestionFormData(BaseFormData):
    question: str = 'This is a question?'
    answer: str = 'Yes'
    option1: str = 'No1'
    option2: str = 'No2'
    option3: str = 'No3'

    # Used only when editing or deleting a question
    id: UUID = None
    edit: bool = None
    delete: bool = None
