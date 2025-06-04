from flask import Flask

from .routes.main_routes import main_bp
from .routes.sentences_routes import sentences_bp
from .routes.irregular_verbs_routes import irregular_verbs_bp
from .routes.phrasal_verbs_routes import phrasal_verbs_bp

def create_app():
    app = Flask(__name__, template_folder='templates')

    #Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(sentences_bp)
    app.register_blueprint(irregular_verbs_bp)
    app.register_blueprint(phrasal_verbs_bp)

    return app