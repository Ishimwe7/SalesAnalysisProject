from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from .models import User
from app import db

UPLOAD_FOLDER = 'app/static/images/profile'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('routes.home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        names = request.form.get('names')
        profile_image = request.files.get('profile-image')

        if password != request.form.get('confirm-password'):
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists', 'error')
            return render_template('signup.html')
        
        filename = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            profile_image.save(os.path.join(UPLOAD_FOLDER, filename))

        user = User(email=email)
        user.setNames(names)
        user.set_password(password)
        if filename:
            user.profile_image = filename 
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Welcome aboard!', 'success')
            return render_template('signup.html')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('signup.html')
    return render_template('signup.html')



@auth.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')

@auth.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    names = request.form.get('names')
    email = request.form.get('email')

    current_user.names = names
    current_user.email = email
    
    profile_image = request.files.get('profile_image')
    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        profile_image.save(os.path.join(UPLOAD_FOLDER, filename))
        current_user.profile_image = filename
    
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')

    return redirect(url_for('auth.profile'))