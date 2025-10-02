"""
Contains model and functions for group and user-group association table
"""

import uuid

from flask_login import current_user
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from flaskapp.extensions import db
from flaskapp.models.user import User

# association table for many-to-many relationship of members-groups
association_table = db.Table('association', db.Model.metadata,
                             db.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), nullable=False),
                             db.Column('group_id', UUID(as_uuid=True), ForeignKey('groups.id'), nullable=False),
                             db.Column('attending', db.Boolean, nullable=False, default=False)
                             )


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)

    owner = db.Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

    members = relationship('User', secondary=association_table)

    def __init__(self, title, description, location, event_date, owner):
        self.title = title
        self.description = description
        self.location = location
        self.event_date = event_date
        self.owner = owner

    def get_number_of_members(self):
        return len(self.members)

    def get_datetime_string(self):
        """
            Function to return formatted string of event datetime
            e.g. if a group's datetime is:
                datetime.datetime(2024, 5, 19, 13, 0)
            the function returns:
                "Sunday, 19th May 2024 @ 13:00"
        """

        # get suffix of the date i.e. th/st/nd/rd
        def get_suffix(n):
            if 10 <= n % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
            return f"{n}{suffix}"

        # get day, month, year, & time of group datetime
        day = self.event_date.strftime("%A")
        month = self.event_date.strftime("%B")
        year = self.event_date.year
        time = self.event_date.strftime("%H:%M")
        day_suffix = get_suffix(self.event_date.day)
        # return formatted datetime
        return f"{day} {day_suffix} {month} {year} @ {time}"

    def get_datetime_form_string(self):
        """
            Function to return formatted string of event datetime for a form
            e.g. if a group's datetime is:
                datetime.datetime(2024, 5, 19, 13, 0)
            the function returns:
                "19-5-2024 13:00"
        """
        day = self.event_date.day
        month = self.event_date.month
        year = self.event_date.year
        time = self.event_date.strftime("%H:%M")
        return f"{day}-{month}-{year} {time}"

    def get_owner(self):
        """Returns username of group owner"""
        owner = User.query.filter_by(id=self.owner).first()
        return owner.username

    def current_user_is_owner(self):
        """Returns true if current user is group owner, false if not"""
        return current_user.id == self.owner

    def current_user_is_member(self):
        """Returns true if current user is group owner, false if not"""
        if current_user.is_authenticated:
            return current_user.id in [member.id for member in self.members]
        return False

    def get_members(self):
        """Returns array of User objects of group members"""
        return self.members

    def is_member(self, user):
        """Returns true if a user is a member of a group"""
        result = db.session.query(association_table.c.user_id).filter(
            association_table.c.group_id == self.id,
            association_table.c.user_id == user.id
        ).first()
        return result is not None

    def is_attending(self, user):
        """Returns true if a user is attending the group"""
        result = db.session.query(association_table.c.attending).filter(
            association_table.c.group_id == self.id,
            association_table.c.user_id == user.id
        ).first()
        return result is not None and result.attending

    def remove_current_user(self):
        """Remove the current_user from the group"""
        if current_user.is_authenticated:
            if self.current_user_is_member():
                self.members = [member for member in self.members if member.id != current_user.id]
                db.session.commit()
        return

    def add_current_user(self):
        """Add the current_user to the group"""
        if current_user.is_authenticated:
            if current_user not in self.members:
                self.members.append(current_user)
                db.session.commit()
        return
