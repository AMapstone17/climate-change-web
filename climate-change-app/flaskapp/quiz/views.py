"""
This file contains functions and routes related to the quiz
"""

import random

from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from flaskapp.extensions import db
from flaskapp.models.leaderboard_entry import LeaderboardEntry
from flaskapp.models.quiz_question import QuizQuestion
from flaskapp.models.user_wrong_question import UserWrongQuestion
from flaskapp.quiz.forms import QuizForm

bp = Blueprint('quiz', __name__, template_folder='templates')


def fetch_questions():
    """
    Fetches all questions from the database

    :return:
        list: A list of all questions in DB

    """
    print("FETCHNG questions...")
    q = QuizQuestion.query.all()
    questions = []
    for question in q:
        questions.append(question)
        print(questions)
    return questions


def generate_quiz():
    """
    Generates a set of quiz questions for the quiz session.

    This function fetches a pool of available questions, randomly selects 10 questions from it,
    and returns them as the quiz questions.

    :returns
        list: A list of 10 randomly selected quiz questions.
    """
    questions = fetch_questions()
    print("FETCHED Questions, generating quiz...")
    quiz_questions = []

    # Iterate ten times adding a random question each iteration adn add it to new list
    for i in range(0, 10):
        quiz_questions.append(random.choice(questions))

    return quiz_questions


def add_to_leaderboard(score):
    """
    Updates user score

    Fetches current user's leaderboard score and adds the given amount if the record exists. If not
    an error message is provided and returns false
    :param score: score to be added to user score
    :return: bool: False if user doesns't exist.
    """
    # Fetch user and their score
    record = LeaderboardEntry.query.get_by_id(current_user.id)

    # Update score if score is in session or return error
    if record:
        record.score += score
        db.session.commit()
    else:
        print("NO USER FOUND")
        return False


@bp.route('/quiz')
@login_required
def quiz():
    """
        Checks if the user is admin, this will change what buttons/links are rendered.
        Then renders the quiz home page

        :returns
            render_template: Renders the quiz home page with the users name with differences in functionality depending on
            whether the user is admin


    """
    is_admin = current_user.is_admin()
    return render_template('quiz/quiz.html', name=current_user.firstname, admin=is_admin)


@bp.route('/quiz-start')
@login_required
def startQuiz():
    """
        Initializes and starts a new quiz session.

        This function generates a new set of quiz questions, initializes the score and index,
        and stores the questions and score in the session. It then redirects to the first
        question of the quiz.

        :returns
            redirect: Redirects to the quiz play page with the first question.
    """
    quiz_questions = generate_quiz()
    # Set score to 0 and store in session
    index = 0
    score = 0
    session['quiz_questions'] = [q.to_json() for q in quiz_questions]
    session['score'] = score

    print("Quiz start")
    # Set page index to index + 1 as python index starts at 0.
    page_index = index + 1
    return redirect(url_for('quiz.playQuiz', index=index, page_index=page_index))


@bp.route('/quiz-result')
@login_required
def quizResult():
    """
        Displays the quiz result page and updates the leaderboard.

        This function checks if the 'score' is present in the session. If not, it redirects
        to the quiz starting page. If the score is present, it updates the leaderboard with
        the current score and renders the result page.

        :returns
            redirect: Redirects to the quiz starting page if 'score' is not in the session.
            render_template: Renders the quiz result page with the final score.
        """
    # Ensure score is in session
    if "score" not in session:
        return redirect(url_for('quiz.quiz'))
    # Fetch score and use add_to_leaderboard to update user score
    score = session['score']
    add_to_leaderboard(score)
    return render_template('quiz/quiz-result.html', score=score)


@bp.route('/quiz-play/<index>', methods=['GET', 'POST'])
@login_required
def playQuiz(index):
    """
      Handles the quiz gameplay logic for each question.

      This function manages the display and handling of quiz questions, updates the score,
      and redirects to the result page if the quiz is completed. It uses the `QuizForm` to
      capture user answers and validates the form upon submission.

      Args:
          index (int): The current question index in the quiz.

      :returns:
          redirect: Redirects to the result page if the quiz is completed.
          render_template: Renders the quiz page with the current question and options if the form is invalid or not submitted yet.
      """

    index = int(index)
    page_index = index + 1  # Add 1 to index as it starts at 0, "Question 0" would look odd to the user
    form = QuizForm()
    score = session['score']
    json_questions = session['quiz_questions']

    # Loop through all questions
    if index > 9:
        return redirect(url_for('quiz.quizResult', score=score))

    # Get current question using current index
    question = json_questions[index]
    question = QuizQuestion.query.get(question["id"])

    # Pass options of current question into form and validate form on submission
    options = [(1, question.answer), (2, question.option1), (3, question.option2), (4, question.option3)]
    random.shuffle(options)
    form.option.choices = options
    if form.validate_on_submit():
        index += 1
        userAns = 0

        # Fetch User Answer
        for option_number, answer in options:
            if str(option_number) == request.form["option"]:
                userAns = answer
                break

        print(userAns)

        # Check answer and handle score accordingly
        checkAns = question.check_answer(userAns)
        if checkAns:
            # if wrong answer exists, delete it
            wrong_answer = UserWrongQuestion.query.filter_by(user_id=current_user.id, question_id=question.id).first()
            if wrong_answer:
                db.session.delete(wrong_answer)
                db.session.commit()

            score += 1
            session['score'] = score
            print("SCORE: ", score)
        else:
            try:
                wrong_answer = UserWrongQuestion(current_user.id, question.id)
                db.session.add(wrong_answer)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print("Integrity Error")
            print("SCORE: ", score)

        return redirect(url_for('quiz.playQuiz', index=index, page_index=page_index))

    print("FORM INVALID", form.errors)
    return render_template('quiz/quiz-play.html', form=form, question=question, index=index, page_index=page_index)
