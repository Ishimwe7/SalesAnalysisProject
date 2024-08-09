# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy # type: ignore
# from flask_login import LoginManager
# from dotenv import load_dotenv

# db = SQLAlchemy()

# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'

# def create_app():
#     load_dotenv()

#     app = Flask(__name__)
#     basedir = os.path.abspath(os.path.dirname(__file__))
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sales.db'
#     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "sales.db")}'
#     db.init_app(app)
#     login_manager.init_app(app)

#     with app.app_context():
#         from . import routes, auth
#         db.create_all()

#     return app

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# def create_app():
#     load_dotenv()

#     app = Flask(__name__)
#     basedir = os.path.abspath(os.path.dirname(__file__))
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
#     database_path = os.path.join(basedir, 'instance', 'sales.db')
#     app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'

#     # Ensure the directory exists
#     if not os.path.exists(os.path.dirname(database_path)):
#         os.makedirs(os.path.dirname(database_path))

#     db.init_app(app)
#     login_manager.init_app(app)

#     with app.app_context():
#         from . import routes, auth
#         db.create_all()

#     return app
def create_app():
    load_dotenv()

    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    database_path = os.path.join(basedir, 'instance', 'sales.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'

    if not os.path.exists(os.path.dirname(database_path)):
        os.makedirs(os.path.dirname(database_path))

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from .routes import routes 
        app.register_blueprint(routes)  
        from .auth import auth  
        app.register_blueprint(auth)
        db.create_all()

    return app
