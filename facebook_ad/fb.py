import io
import json
import os
from flask import Blueprint, request
from utils import upload_to_database, Convert_extract_upload, create_setting, \
    image_to_text_data, save_image_to_dir
import pathlib

ads_library_blueprint = Blueprint('ads_library_blueprint', __name__, template_folder='templates')


@ads_library_blueprint.route('/har', methods=["POST"])
def facebook_ads_using_har():
    file = pathlib.Path(os.getcwd()+'/screenshots/')
    if not file.exists():
        os.mkdir(os.getcwd()+'/screenshots/')
    har_file = request.files['file']
    files = request.files.getlist('image_file')
    save_image_to_dir(files)
    image_data = image_to_text_data()
    file_stream = io.StringIO(har_file.stream.read().decode(), newline=None)
    contents = file_stream.read()
    har_txt = json.loads(contents)
    settings = create_setting(har_txt)
    result = Convert_extract_upload(har_txt, settings, image_data)
    upload_to_database(result)
    return "<center><h1>Successfully save ads into database.</h1></center>"


@ads_library_blueprint.route('/upload')
def upload_har_file():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Facebook Ads Upload:</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css"
              rel="stylesheet" integrity="sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD"
              crossorigin="anonymous">
    </head>
    <body>
    <div class="container my-4">
        <div class='col-md-8'>
        <h1>Update HAR into Database</h1>
            <form action="/ads/har" method="POST" enctype="multipart/form-data">
                <label class="form-text">Upload Har: </label>
                <input type="file" class="form-control my-2" name="file" required/>
                <label class="form-text">Upload Image: </label>
                    <input type="file" class="form-control my-2" name="image_file" multiple required/>
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-w76AqPfDkMBDXo30jS1Sgez6pr3x5MlQ1ZAGC+nuZB+EYdgRZgiwxhTBTkF7CXvN" crossorigin="anonymous">
    </script>
    </body>
    </html>
       '''
