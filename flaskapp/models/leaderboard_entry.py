"""'
Contains model for leaderboard entry
"""

from sqlalchemy.dialects.postgresql import UUID

from flaskapp.extensions import db


class LeaderboardEntry(db.Model):
    __tablename__ = 'leaderboard_entries'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    game_highscore = db.Column(db.Integer, nullable=False)

    last_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, user_id, score, game_highscore):
        self.user_id = user_id
        self.score = score
        self.game_highscore = game_highscore

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score
