from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Correct path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, '../model/traffic_model.pkl'))
columns = joblib.load(os.path.join(BASE_DIR, '../model/columns.pkl'))

@app.route('/')
def home():
    return "🚦 Traffic Prediction API Running"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    input_df = pd.DataFrame([data])

    # Encode like training
    input_encoded = pd.get_dummies(input_df)

    for col in columns:
        if col not in input_encoded:
            input_encoded[col] = 0

    input_encoded = input_encoded[columns]

    prediction = model.predict(input_encoded)

    return jsonify({
        "travel_time": float(prediction[0])
    })

if __name__ == "__main__":
    # Use dynamic port for Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)