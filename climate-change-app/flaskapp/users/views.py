
# IMPORTS
import logging

from flask import Blueprint, render_template, flash, redirect, url_for, session, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from markupsafe import Markup

from flaskapp.extensions import db
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.user import User, hash_user_password
from flaskapp.models.user_wrong_question import UserWrongQuestion
from flaskapp.users.forms import RegisterForm, LoginForm, ChangePasswordForm, CreateAdminForm
from flaskapp.models.group import Group

bp = Blueprint('users', __name__, template_folder='templates')


# view registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is logged in before accessing the page
    if not current_user.is_anonymous:
        flash('You are already logged in')
        print('user logged in already')
        return render_template('users/account.html'), 400

    form = RegisterForm()

    # if request method is GET or form not valid re-render signup page
    if not form.validate_on_submit():
        # 200 if this is initial page load, 400 if form is invalid
        status_code = 200 if request.method == 'GET' else 400
        return render_template('users/register.html', form=form), status_code

    username_exists = User.query.filter_by(username=form.username.data).first()
    email_exists = User.query.filter_by(email=form.email.data).first()

    if username_exists:
        flash('Username already exists')
        return render_template('users/register.html', form=form), 400

    if email_exists:
        flash('Email already exists')
        return render_template('users/register.html', form=form), 400

    # create a new user with the form data
    new_user = User(
        email=form.email.data,
        username=form.username.data,
        password=form.password.data,
        firstname=form.firstname.data,
        lastname=form.lastname.data,
        date_of_birth=form.date_of_birth.data,
        role="user"
    )
    db.session.add(new_user)
    db.session.commit()

    # add user to leaderboard
    leaderboard_entry = LeaderboardEntry(new_user.id, 0, 0)
    db.session.add(leaderboard_entry)
    db.session.commit()

    logging.warning('SECURITY - User registration [%s, %s]',
                    new_user.username,
                    request.remote_addr
                    )

    session['username'] = new_user.username
    # sends user to 2fa setup
    return redirect(url_for('users.setup_2fa'))


@bp.route('/setup_2fa')
def setup_2fa():
    if 'username' not in session:
        return redirect(url_for('home.index'))

    # get the user from the database
    user = User.query.filter_by(username=session['username']).first()

    if not user:
        return redirect(url_for('home.index'))

    del session['username']

    return render_template('users/setup_2fa.html', pin=user.otp_key, email=user.email, uri=user.get_2fa_uri()), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


# view user login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is logged in before accessing the page
    if not current_user.is_anonymous:
        flash('You are already logged in')
        return render_template('users/account.html'), 400

    form = LoginForm()

    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    if not form.validate_on_submit():
        # 200 if this is initial page load, 400 if form is invalid
        status_code = 200 if request.method == 'GET' else 400
        return render_template('users/login.html', loginForm=form), status_code

    user = User.query.filter_by(username=form.username.data).first()
    success = user and user.verify_password(form.password.data) and user.verify_otp(form.pin.data)

    if not success:
        session['authentication_attempts'] += 1
        if session.get('authentication_attempts') >= 3:
            flash(Markup('Number of incorrect login attempts exceeded. '
                         'Please click <a href="/reset">here</a> to reset.'))
            return render_template('users/login.html'), 400
        logging.warning('SECURITY - Invalid Log In Attempt [%s, %s]', form.username.data, request.remote_addr)
        flash('Please check your login details and try again, '
              '{} login attempts remaining'.format(3 - session.get('authentication_attempts')))

        return render_template('users/login.html', loginForm=form), 400

    login_user(user)
    session['authentication_attempts'] = 0
    db.session.commit()

    logging.warning('SECURITY - Log in [%s, %s, %s]',
                    current_user.id,
                    current_user.username,
                    request.remote_addr)

    return redirect(url_for('users.account'))


# view user account
@bp.route('/account')
@login_required
def account():
    return render_template('users/account.html')


@bp.route('/leaderboard')
@login_required
def leaderboard():
    game_scores = db.session.query(LeaderboardEntry).all()

    # make first 3 empty, in the case of not enough users
    game_first, combined_first = None, None
    game_second, combined_second = None, None
    game_third, combined_third = None, None

    # create a list with the username and that users' highest score
    game_custom_list = []
    combined_custom_list = []
    for entry in game_scores:
        user: User = User.query.filter_by(id=entry.user_id).first()
        game_custom_list.append((user.username, entry.game_highscore))
        combined_custom_list.append((user.username, entry.score))

    # sort them in descending order to get the highest scores at the top
    game_sorted_scores = sorted(game_custom_list, key=lambda score: score[1], reverse=True)
    combined_sorted_scores = sorted(combined_custom_list, key=lambda score: score[1], reverse=True)

    # add them separately for when there are less than 3 users
    if game_sorted_scores:
        game_first = game_sorted_scores[0]
    if len(game_sorted_scores) > 1:
        game_second = game_sorted_scores[1]
    if len(game_sorted_scores) > 2:
        game_third = game_sorted_scores[2]
    if combined_sorted_scores:
        combined_first = combined_sorted_scores[0]
    if len(combined_sorted_scores) > 1:
        combined_second = combined_sorted_scores[1]
    if len(combined_sorted_scores) > 2:
        combined_third = combined_sorted_scores[2]

        # The rest of the scores, if there are more than three entries
    game_the_rest = game_sorted_scores[3:] if len(game_sorted_scores) > 3 else []
    combined_the_rest = combined_sorted_scores[3:] if len(combined_sorted_scores) > 3 else []

    return render_template('users/leaderboard.html', game_first=game_first, game_second=game_second,
                           game_third=game_third, game_the_rest=game_the_rest, combined_first=combined_first,
                           combined_second=combined_second, combined_third=combined_third,
                           combined_the_rest=combined_the_rest)


# view game dashboard
@bp.route('/game_dashboard')
@login_required
def game_dashboard():
    return render_template('users/game_dashboard.html')


@bp.route('/game')
@login_required
def game():
    return render_template('users/game.html')


def try_change_password(form) -> bool:
    """Attempts to change the user's password. Returns True if successful, False otherwise."""

    user: User = User.query.filter_by(id=current_user.id).first()

    if not user.verify_password(form.current_password.data):
        flash('Incorrect password')
        return False

    if user.verify_password(form.new_password.data):
        flash('New password must be different from old password')
        return False

    # hash password and save changes
    user.password = hash_user_password(form.new_password.data)
    db.session.commit()

    logging.info(f'[SECURITY] User password changed '
                 f'(id={user.id}, email={user.email}, role={user.role}, ip={request.remote_addr})')

    return True


def try_add_admin(form) -> bool:
    """ Attempts to add administrator by checking if username and email entered belong to a user
    . Returns True if successful, False otherwise."""
    if not current_user.is_admin():
        flash("You are not authorised to perform this action")
        return False

    user: User = User.query.filter_by(username=form.username.data, email=form.email.data).first()

    if not user:
        flash('Incorrect information provided or user does not exist')
        return False

    user.role = 'admin'
    db.session.commit()

    logging.info(f'[SECURITY] New Admin Added by'
                 f'(id={current_user.id}, email={current_user.email}, role={current_user.role}, ip={request.remote_addr}, '
                 f'New Admin: id={user.id}, email={user.email})')

    return True


@bp.route('/account/delete')
@login_required
def delete_account():
    # get current users leaderboard entry
    leaderboard_entry: LeaderboardEntry = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()

    groups = Group.query.all()
    for group in groups:
        group.remove_current_user()

    db.session.delete(leaderboard_entry)
    db.session.delete(current_user)
    db.session.commit()

    return redirect(url_for('home.index'))


@bp.route('/settings/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    success = False

    if form.validate_on_submit():
        if try_change_password(form):
            flash('Password changed successfully')
            success = True

    if not success:
        flash('Failed to change password')

    return redirect(url_for('users.settings'))


@bp.route('/settings/create_admin', methods=['POST'])
@login_required
def create_admin():
    form = CreateAdminForm()
    success = False

    if form.validate_on_submit():
        if try_add_admin(form):
            flash('New administrator added successfully')
            success = True

    if not success:
        flash('Failed to add new administrator')

    return redirect(url_for('users.settings'))


@bp.route('/settings')
@login_required
def settings():
    return render_template('users/settings.html', passwordForm=ChangePasswordForm(), adminForm=CreateAdminForm(), users=User.query.all())


@bp.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log Out [%s, %s, %s]',
                    current_user.id,
                    current_user.username,
                    request.remote_addr)
    logout_user()
    return redirect(url_for('home.index'))


@bp.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


@bp.route('/update-highscore', methods=['POST'])
@login_required
def update_highscore():
    data = request.get_json()
    new_score = data.get('score', 0)

    leaderboard_entry = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()

    if leaderboard_entry:
        if new_score > leaderboard_entry.game_highscore:
            leaderboard_entry.game_highscore = new_score
            db.session.commit()
        high_score = leaderboard_entry.game_highscore
    else:
        # If no leaderboard entry exists, create one
        leaderboard_entry = LeaderboardEntry(user_id=current_user.id, score=0, game_highscore=new_score)
        db.session.add(leaderboard_entry)
        db.session.commit()
        high_score = new_score

    return jsonify({'high_score': high_score})
