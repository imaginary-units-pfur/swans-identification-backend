from flask import Flask, request

from main import process_files
import time
import os

app = Flask("swans-identification-backend")
app.config["IMAGES_TO_PROCESS"] = "images/to_process/"
app.config["SAVED_IMAGES"] = "images/saved/"


@app.route("/analyze", methods=["POST"])
def analyze():
    time.sleep(5)  # for testing purposes

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


@app.route("/")
def index():
    return """
    <form method=POST action="/analyze" enctype="multipart/form-data">
    <input type="file" name="f[]">
    <input type="file" name="f[]">
    <input type="file" name="f[]">
    <input type="file" name="f[]">
    <input type=submit>
    </form>
    """


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
