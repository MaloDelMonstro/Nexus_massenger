from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    return render_template('index.html')