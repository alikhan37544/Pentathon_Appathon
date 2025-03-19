from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')

    # Register blueprints
    from .routes.main import main as main_blueprint
    from .routes.document import document as document_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(document_blueprint)

    return app