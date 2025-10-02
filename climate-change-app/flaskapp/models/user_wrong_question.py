from sqlalchemy.dialects.postgresql import UUID

from flaskapp.extensions import db


class UserWrongQuestion(db.Model):
    __tablename__ = 'user_wrong_questions'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('quiz_questions.id'), primary_key=True)

    def __init__(self, user_id, question_id):
        self.user_id = user_id
        self.question_id = question_id

    def __repr__(self):
        return f'UserWrongQuestion({self.user_id}, {self.question_id})'
