from importlib.metadata import version
import traceback

from flask import Flask, request
from werkzeug.exceptions import HTTPException, NotFound, UnsupportedMediaType

from .invoke import invoke


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def route_index():
        return {
            "app": "Rippling Flux Server",
            "versions": {dep: version(dep) for dep in ["Flask", "rippling-flux-sdk", "rippling-flux-dev-tools"]}
        }

    @app.route("/invoke", methods=["POST"])
    def route_invoke():
        return invoke(request.get_json())

    @app.errorhandler(404)
    def page_not_found(err: NotFound):
        return err.description, err.code

    @app.errorhandler(415)
    def page_unsupported_media_type(err: UnsupportedMediaType):
        return err.description, err.code

    @app.errorhandler(HTTPException)
    def errorhandler_catch(err: HTTPException):
        return traceback.format_exc(), err.code

    return app