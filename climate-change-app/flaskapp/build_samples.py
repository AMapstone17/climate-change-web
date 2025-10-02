
import datetime
import os
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy.sql import insert

from flaskapp import create_app
from flaskapp.extensions import db
from flaskapp.models.blog_post import BlogPost
from flaskapp.models.group import Group, association_table
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.user import User

load_dotenv('../.env.local')


def build_samples():
    """A helper function to drop the database and re-initialise it with samples."""
    app = create_app(None)

    static_path = os.path.join(app.root_path, 'static')

    admin_user = User(
        username='admin1',
        password='Admin1!',
        firstname='Admin',
        lastname='User',
        date_of_birth=datetime.datetime(1990, 1, 1),
        email='admin@user.com',
        role='admin'
    )

    def build_users_and_leaderboard():
        with open(os.path.join(static_path, 'samples/user_samples.txt'), 'r') as user_file:
            i = 0
            for line in user_file:
                user_id_str, email, username, fname, lname, dob_str, password, role, score, game_highscore = line.strip().split(',')
                dob_array = [int(part) for part in dob_str.split('-')]
                dob = datetime.datetime(dob_array[0], dob_array[1], dob_array[2])
                user_id = UUID(user_id_str)
                user = User.with_custom_id(user_id, email, username, fname, lname, dob, password, role)
                db.session.add(user)
                db.session.commit()
                print(">>>>>>>STATUS UPDATE: User #" + str(i) + " successfully added.")
                # add leaderboard entry for user
                leaderboard_entry = LeaderboardEntry(user.id, score, game_highscore)
                db.session.add(leaderboard_entry)
                db.session.commit()
                print(">>>>>>>STATUS UPDATE: User #" + str(i) + " leaderboard successfully added.")
                i += 1

        print('>>>>>>>STATUS UPDATE: All users and leaderboard entries added.')

    def build_questions():
        with open(os.path.join(static_path, 'samples/question_samples.txt'), 'r') as question_file:
            i = 0
            for line in question_file:
                q, a, o1, o2, o3 = line.strip().split(',')
                question = QuizQuestion(q, a, o1, o2, o3)
                db.session.add(question)
                db.session.commit()
                print(">>>>>>>STATUS UPDATE: Question #" + str(i) + " successfully added.")
                i += 1

        print('>>>>>>>STATUS UPDATE: All questions added.')

    def build_blog_posts():
        for filename in os.listdir(os.path.join(static_path, 'samples/blog_post_samples')):
            i = 0
            if filename.endswith('.md'):
                sample_path = os.path.join(static_path, 'samples/blog_post_samples', filename)
                with open(sample_path, 'r') as blog_post_file:
                    id_str = blog_post_file.readline().strip()
                    title = blog_post_file.readline().strip()
                    author_id = UUID(id_str)
                    content_lines = blog_post_file.readlines()
                    content = ''.join(content_lines)
                    post = BlogPost(author_id, title, content)
                    db.session.add(post)
                    db.session.commit()
                    print(">>>>>>>STATUS UPDATE: Post #" + str(i) + " '" + title + "' successfully added.")
                i += 1

        print('>>>>>>>STATUS UPDATE: All posts added')

    def build_groups():
        with open(os.path.join(static_path, 'samples/group_samples.txt'), 'r') as group_file:
            i = 0
            for line in group_file:
                title, description, location, date_str, owner_id_str = line.strip().split(',')
                owner_id = UUID(owner_id_str)
                date_array = [int(part) for part in date_str.split('-')]
                date = datetime.datetime(date_array[0], date_array[1], date_array[2])
                group = Group(title, description, location, date, owner_id)
                db.session.add(group)
                db.session.commit()
                print(">>>>>>>STATUS UPDATE: Group #" + str(i) + " successfully added.")
                i += 1

        print(">>>>>>>STATUS UPDATE: All groups added.")

    def build_memberships():
        with open(os.path.join(static_path, 'samples/membership_samples.txt'), 'r') as memberships_file:
            i = 0
            for line in memberships_file:
                group_title, user_id_str, attending = line.strip().split(',')
                user_id = UUID(user_id_str)
                group = Group.query.filter_by(title=group_title).first()
                ins = insert(association_table).values(user_id=user_id, group_id=group.id, attending=bool(attending))
                db.session.execute(ins)
                db.session.commit()
                i += 1
                print(">>>>>>>STATUS UPDATE: Membership #" + str(i) + " successfully added.")

            print(">>>>>>>STATUS UPDATE: All memberships added.")

    with app.app_context():

        # build DB
        db.drop_all()
        db.create_all()

        # add admin
        db.session.add(admin_user)
        db.session.commit()
        # Add admin user leaderboard entry
        admin_leaderboard = LeaderboardEntry(admin_user.id, 0, 0)
        db.session.add(admin_leaderboard)
        db.session.commit()

        # build samples
        build_users_and_leaderboard()
        build_questions()
        build_blog_posts()
        build_groups()
        # add group memberships
        build_memberships()

        print('>>>>>>>STATUS UPDATE: Database sample setup complete')


if __name__ == '__main__':
    build_samples()
