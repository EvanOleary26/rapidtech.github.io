from flask import Flask, render_template, request, jsonify
from utils import calculate_railway_metrics
import os


app = Flask(__name__)

@app.route("/get-api-key")
def get_api_key():
    return jsonify({"apiKey": os.getenv("GOOGLE_MAPS_API_KEY")})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    origin = request.form.get('origin')
    destination = request.form.get('destination')

    metrics = calculate_railway_metrics(origin, destination)

    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True)
