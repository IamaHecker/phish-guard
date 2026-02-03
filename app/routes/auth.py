from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    try:
        if form.validate_on_submit():
            print(f"--> LOGIN DEBUG: Attempting login for user: {form.username.data}")
            user = User.query.filter_by(username=form.username.data).first()
            
            if user is None:
                print("--> LOGIN DEBUG: User not found in DB")
            elif not user.check_password(form.password.data):
                print("--> LOGIN DEBUG: Password check failed")
            
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            
            print("--> LOGIN DEBUG: User validated. attempting login_user...")
            login_user(user, remember=form.remember_me.data)
            print("--> LOGIN DEBUG: login_user successful.")
            
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
    except Exception as e:
        import traceback
        print(f"--> LOGIN ERROR: {str(e)}")
        traceback.print_exc()
        flash(f"Login Error: {str(e)}")
        
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
