"""
This file contains functions and routes related to the admin functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from flaskapp.admin.forms import QuizQuestionForm
from flaskapp.extensions import db, roles_required
from flaskapp.models.quiz_question import QuizQuestion

bp = Blueprint('admin', __name__, template_folder='templates')


@bp.route('/admin/edit_questions', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_questions():
    """
    Manages the quiz questions through an admin interface.

    This function handles the form submission for editing or deleting quiz questions.
    If the form is valid and a question ID is provided, it updates or deletes the
    question in the database based on the action specified in the form. It then retrieves
    all questions and renders the admin page for editing questions.

    :returns
        render_template: Renders the admin page for editing quiz questions.
    """
    # Fetch form
    form = QuizQuestionForm()

    # Validate form
    if form.validate_on_submit():
        question = QuizQuestion.query.get_by_id(request.form['id'])
        # Handle which function user selects
        if question:
            if 'edit' in request.form:
                question.question = form.question.data
                question.answer = form.answer.data
                question.option1 = form.option1.data
                question.option2 = form.option2.data
                question.option3 = form.option3.data
                db.session.commit()
            elif 'delete' in request.form:
                db.session.delete(question)
                db.session.commit()

    # Get list of all questions
    questions = QuizQuestion.query.all()
    return render_template('admin/edit_questions.html', questions=questions, form=form)


@bp.route('/admin/new_question', methods=['POST'])
@login_required
@roles_required('admin')
def new_question():
    """
    Handles the creation of a new quiz question.

    This function processes the form submission for adding a new quiz question.
    If the form is valid, it creates a new `QuizQuestion` object with the data from
    the form, adds it to the database session, and commits the session to save the new
    question. If the form is invalid, it prints an error message. Finally, it redirects
    to the admin page for editing questions.

    :returns:
        redirect: Redirects to the admin page for editing quiz questions.
    """
    # Fetch form from forms file
    form = QuizQuestionForm()
    # Validate form
    if form.validate_on_submit():
        question = QuizQuestion(
            question=form.question.data,
            answer=form.answer.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data
        )
        db.session.add(question)
        db.session.commit()
        print('New question added')
    else:
        print('Invalid form')
    return redirect(url_for('admin.edit_questions'))


@bp.route('/internal/reset_db')
def reset_db():
    """
    Resets the database to its initial state.

    This function calls an internal function `reset_db` from the Flask application,
    which performs the actual database reset operation. After resetting the database,
    it returns a message indicating the successful reset.

    Returns:
        str: A message indicating the successful reset of the database.
    """
    from flaskapp.reset import reset_db as internal_reset_db
    internal_reset_db()
    return 'Database successfully reset.'


@bp.route('/internal/build_samples')
def build_samples():
    """
    Loads sample data into database

    :return:
        str: A message indicating successful adding od data
    """
    from flaskapp.build_samples import build_samples as internal_build_samples
    internal_build_samples()
    return 'Database samples successfully added.'
