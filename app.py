from flask import Flask, request, send_from_directory

from main import process_files
from flask_cors import CORS
import db
import os
import uuid
import fnmatch

from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask("swans-identification-backend")
CORS(app)
app.config["IMAGES_TO_PROCESS"] = "images/to_process/"
app.config["SAVED_IMAGES"] = "images/saved/"


@app.route("/analyze", methods=["POST"])
def analyze():
    paths = []
    app.logger.info(f"Got files {[x.filename for x in request.files.getlist('f[]')]}")
    for file in request.files.getlist("f[]"):
        if file and file.filename:
            file_name_stored = os.path.join(
                app.config["IMAGES_TO_PROCESS"], file.filename
            )
            file.save(file_name_stored)
            paths.append(file_name_stored)

    app.logger.info(f"Seinding paths to model {paths}")
    output = process_files(paths)
    formatted_output = {}
    for analysis in output:
        filename = analysis.pop("filename")
        formatted_output[filename] = {"overall_class": analysis}

    for path in paths:
        os.remove(path)

    return formatted_output


@app.route("/save", methods=["POST"])
def save():
    app.logger.info(f"Got files {[x.filename for x in request.files.getlist('f[]')]}")

    tags = request.files["tags"].read().trim().split(" ")
    app.logger.info(f"Got tags {tags}")

    for file in request.files.getlist("f[]"):
        if file and file.filename and file.filename != "tags":
            file_uuid = str(uuid.uuid4())
            ext = file.filename.split(".")[-1]
            file_name_stored = os.path.join(
                app.config["SAVED_IMAGES"], f"{file_uuid}.{ext}"
            )
            file.save(file_name_stored)
            db.add_image_with_tags(file_uuid, tags)

    resp = {"status": "success"}
    return resp, 200


@app.route("/image", methods=["GET"])
def get_image():
    tags = request.args["tags"].split(" ")
    app.logger.info(f"Got tags {tags}")

    img_uuids = db.get_by_tags(tags)

    imgs = []
    for img_uuid in img_uuids:
        imgs.append(find_saved_image(f"{img_uuid}.*"))

    return imgs


@app.route("/images/<path:path>", methods=["GET"])
def download_image(path):
    return send_from_directory(app.config["SAVED_IMAGES"], os.path.basename(path))


def find_saved_image(pattern):
    for root, _, files in os.walk(app.config["SAVED_IMAGES"]):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


@app.route("/")
def index():
    return """
    <form method=POST action="/save" enctype="multipart/form-data">
        <input type="file" name="f[]">
        <input type="file" name="f[]">
        <input type="text" name="tags">
        <input type=submit>
    </form>
    """


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
