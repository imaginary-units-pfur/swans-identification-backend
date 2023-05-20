from flask import Flask, request

from main import process_files
import db
import os
import uuid

app = Flask("swans-identification-backend")
app.config["IMAGES_TO_PROCESS"] = "images/to_process/"
app.config["SAVED_IMAGES"] = "images/saved/"


@app.route("/analyze", methods=["POST"])
def analyze():
    paths = []
    for file in request.files.getlist("f[]"):
        if file and file.filename:
            file_name_stored = os.path.join(
                app.config["IMAGES_TO_PROCESS"], file.filename
            )
            file.save(file_name_stored)
            paths.append(file_name_stored)

    output = process_files(paths)
    for path in paths:
        os.remove(path)

    return output


@app.route("/save", methods=["POST"])
def save():
    tags = request.form["tags"].split(" ")
    for file in request.files.getlist("f[]"):
        if file and file.filename:
            file_uuid = str(uuid.uuid4())
            ext = file.filename.split(".")[-1]
            file_name_stored = os.path.join(
                app.config["SAVED_IMAGES"], f"{file_uuid}.{ext}"
            )
            file.save(file_name_stored)
            db.add_image_with_tags(file_uuid, tags)

    resp = {"status": "success"}
    return resp, 200


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
