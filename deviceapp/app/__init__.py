from flask import Flask
from flask import Flask
from flask_cors import CORS
from .extensions import db,migrate
from flask_wtf.csrf import CSRFProtect



csrf_protect = CSRFProtect()


def create_app(extra_config_settings={}):
    """Create a Flask applicaction.
    """
   
    app = Flask(__name__, static_url_path='/static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    CORS(app, expose_headers=["content-disposition"])
    
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = "Yoursecretstring"
    app.config.from_object('app.settings')
    app.config.update(extra_config_settings)
    db.init_app(app)
    csrf_protect.init_app(app)
    migrate.init_app(app, db)



    # Register blueprints
    from app.blueprints import api_blueprint
    app.register_blueprint(api_blueprint)
    csrf_protect.exempt(api_blueprint)
    

    return app