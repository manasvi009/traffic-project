from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load model + columns
model = joblib.load("../model/traffic_model.pkl")
columns = joblib.load("../model/columns.pkl")

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
    app.run(host="0.0.0.0", port=5000)