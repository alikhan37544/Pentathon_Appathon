from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE='database.db',
    )

    from . import routes
    app.register_blueprint(routes.main_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)