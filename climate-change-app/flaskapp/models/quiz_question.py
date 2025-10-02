"""
Contains model and function for quiz question
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID

from flaskapp.extensions import db


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)

    def __init__(self, question, answer, option1, option2, option3):
        self.question = question
        self.answer = answer
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3

    def check_answer(self, answer):
        return self.answer == answer

    def __str__(self):
        return f'{self.question} - {self.answer} [{self.option1}, {self.option2}, {self.option3}]'

    def __repr__(self):
        return f'QuizQuestion({self.id}, {self.question}, {self.answer}, {self.option1}, {self.option2}, {self.option3})'

    def to_json(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "option1": self.option1,
            "option2": self.option2,
            "option3": self.option3
        }

    def from_json(self, json_dict):
        return QuizQuestion(**json_dict)
