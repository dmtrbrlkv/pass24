import os

from flask import Flask, request, render_template

from pass24_api_client.api_client import create_pass, get_vehicle_models

OBJECT_ID = os.getenv('OBJECT_ID')
OBJECT_NAME = os.getenv('OBJECT_NAME')

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index_get():
    vehicle_models = get_vehicle_models()
    return render_template('index.html', vehicle_models=vehicle_models, object_name=OBJECT_NAME)


@app.route("/", methods=['POST'])
def create_pass_post():
    v = request.form
    response = create_pass(**v, object_id=OBJECT_ID)
    return render_template('response.html', response=response, object_name=OBJECT_NAME)


if __name__ == '__main__':
    app.run()
