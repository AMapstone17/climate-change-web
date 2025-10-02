"""
Contains routes for home page and internal testing.
"""

from flask import Blueprint, render_template

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/internal/test')
def test():
    return 'Internal test endpoint reached.'
