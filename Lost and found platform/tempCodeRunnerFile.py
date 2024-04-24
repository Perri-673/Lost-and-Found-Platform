# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def create_app():
    from routes import bp_home, bp_login, bp_logout, bp_register, bp_profile, bp_report_lost_item, bp_report_found_item

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost_and_found.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(bp_home)
    app.register_blueprint(bp_login, url_prefix='/login')
    app.register_blueprint(bp_logout, url_prefix='/logout')
    app.register_blueprint(bp_register, url_prefix='/register')
    app.register_blueprint(bp_profile, url_prefix='/profile')
    app.register_blueprint(bp_report_lost_item, url_prefix='/report_lost_item')
    app.register_blueprint(bp_report_found_item, url_prefix='/report_found_item')

    with app.app_context():
        from models import User, LostItem, FoundItem
        db.create_all()

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
