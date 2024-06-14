from flask import Flask


def create_app():
    my_app = Flask(__name__)

    from main import main as main_blueprint
    my_app.register_blueprint(main_blueprint)

    return my_app


app = create_app()
