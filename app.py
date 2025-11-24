from flask import Flask

from controllers.hepatitis_controller import hepatic_bp


def create_mi_app() -> Flask:
    """Mi factory personal que conecta controladores y vistas."""
    app = Flask(__name__, template_folder="Templates")
    app.register_blueprint(hepatic_bp)
    return app


app = create_mi_app()


if __name__ == "__main__":
    app.run(port=5001)
