
import datetime
from uuid import UUID

from dotenv import load_dotenv

from flaskapp import create_app
from flaskapp.extensions import db
from flaskapp.models.blog_post import BlogPost
from flaskapp.models.group import Group
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.user import User
from flaskapp.models.user_wrong_question import UserWrongQuestion

load_dotenv('../.env.local')


def reset_db():
    """A helper function to drop the database and re-initialise it."""
    app = create_app(None)

    admin_user = User(
        username='admin1',
        password='Admin1!',
        firstname='Admin',
        lastname='User',
        date_of_birth=datetime.datetime(1990, 1, 1),
        email='admin@user.com',
        role='admin'
    )

    # These objects are used to ensure all tables are created (they are not added to the database)
    _ = QuizQuestion('Q1', 'Answer', 'O1', 'O2', 'O3')
    _ = BlogPost('Title', 'Content', admin_user.id)
    _ = LeaderboardEntry(admin_user.id, 0, 0)
    _ = Group('Title', 'Description', 'Location', datetime.datetime(2024, 1, 1, 12, 0), admin_user.id)
    _ = UserWrongQuestion(admin_user.id, UUID('00000000-0000-0000-0000-000000000000'))

    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(admin_user)
        db.session.commit()

        # Add admin user leaderboard entry
        admin_leaderboard = LeaderboardEntry(admin_user.id, 0, 0)
        db.session.add(admin_leaderboard)
        db.session.commit()

        print('Database reset complete')


if __name__ == '__main__':
    reset_db()
