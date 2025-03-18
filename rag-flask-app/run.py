import os
from flask import Flask

def create_app():
    app = Flask(__name__, 
                instance_relative_config=True,
                template_folder='app/templates',
                static_folder='app/static')
    
    # Make paths absolute
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(base_dir, 'instance', 'database.db'),
        UPLOAD_FOLDER=os.path.join(base_dir, 'data'),
        ALLOWED_EXTENSIONS={'pdf', 'txt'},
        CHROMA_PATH=os.path.join(base_dir, 'chroma')
    )

    # Register blueprints
    from app.routes.main import main
    from app.routes.document import document_bp

    app.register_blueprint(main)
    app.register_blueprint(document_bp)
    
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CHROMA_PATH'], exist_ok=True)
    
    # Add context processor for year in templates
    @app.context_processor
    def inject_current_year():
        import datetime
        return {'current_year': datetime.datetime.now().year}
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)