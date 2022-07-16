from flask import Flask, request, render_template

from pass24_api_client.api_client import create_pass, get_vehicle_models

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index_get():
    vehicle_models = get_vehicle_models()
    return render_template('index.html', vehicle_models=vehicle_models)


@app.route("/", methods=['POST'])
def create_pass_post():
    v = request.form
    response = create_pass(**v)
    return render_template('response.html', response=response)


if __name__ == '__main__':
    app.run()
