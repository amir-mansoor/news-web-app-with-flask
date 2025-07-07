from flask import Flask
from flask_login import LoginManager
from app.models import init_db, load_user
from datetime import datetime

login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    from app.routes import main
    app.register_blueprint(main)

    from app.admin_routes import admin
    app.register_blueprint(admin)

    from app.user_routes import user
    app.register_blueprint(user)

    init_db(app)

    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)

    
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    return app
