"""
Contains model class for blogposts
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID

from flaskapp.extensions import db


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, author_id, title, content):
        self.author_id = author_id
        self.title = title
        self.content = content
