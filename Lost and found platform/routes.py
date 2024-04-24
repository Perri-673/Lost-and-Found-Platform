# routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from models import User, Item, Notification
from forms import RegistrationForm, ItemForm, LoginForm, ClaimForm

bp_home = Blueprint('home', __name__)
bp_login = Blueprint('login', __name__)
bp_logout = Blueprint('logout', __name__)
bp_register = Blueprint('register', __name__)
bp_profile = Blueprint('profile', __name__)
bp_post_item = Blueprint('post_item', __name__)
bp_dashboard = Blueprint('dashboard', __name__)


@bp_home.route('/')
def home():
    return render_template('home.html')

@bp_login.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html', form=form)
@bp_logout.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home.home'))

@bp_dashboard.route('/dashboard')
@login_required
def dashboard():
    all_items = Item.query.all()
    return render_template('dashboard.html', all_items=all_items, user=current_user)

@bp_register.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login.login'))

    return render_template('register.html', form=form)

@bp_profile.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@bp_post_item.route('/report_item', methods=['GET', 'POST'])
@login_required
def post_item():
    form = ItemForm()  # You can use the same form for reporting items

    if form.validate_on_submit():
        description = form.description.data
        location = form.location.data

        new_item = Item(description=description, location=location, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()

        flash('Item reported successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('post_item.html', form=form)

@bp_dashboard.route('/claim_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ClaimForm()

    if item.claimed=="Yes":
        flash('This item has already been claimed.', 'info')
        return redirect(url_for('dashboard.dashboard'))

    if form.validate_on_submit():
        claim_description = form.claim_description.data
        item.claim_description = claim_description
        item.claimed = "Pending"

        # Notify the user who posted the item about the claim
        notification_message = f'Your item "{item.description}" has been claimed. Review the claim.'
        notification = Notification(user_id=item.user_id, message=notification_message)
        db.session.add(notification)

        db.session.commit()
        flash('Claim submitted successfully. The item owner will review your claim.', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('claim_item.html', form=form, item=item)

@bp_dashboard.route('/approve_claim/<int:item_id>', methods=['POST'])
@login_required
def approve_claim(item_id):
    item = Item.query.get_or_404(item_id)

    if current_user.id != item.user.id:
        flash('You do not have permission to approve this claim.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    item.approved = True
    item.claimed = "Yes"
    db.session.commit()

    flash('Claim approved successfully.', 'success')
    return redirect(url_for('dashboard.dashboard'))

@bp_dashboard.route('/reject_claim/<int:item_id>', methods=['POST'])
@login_required
def reject_claim(item_id):
    item = Item.query.get_or_404(item_id)

    if current_user.id != item.user.id:
        flash('You do not have permission to reject this claim.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    item.approved = False
    item.claimed = None
    db.session.commit()

    flash('Claim rejected successfully.', 'success')
    return redirect(url_for('dashboard.dashboard'))