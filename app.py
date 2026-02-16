import joblib
import numpy as np
from config.paths_config import MODEL_OUTPUT_PATH, ENCODER_PATH
from flask import Flask, render_template, request

app = Flask(__name__)

# Load the trained model and label encoders
model = joblib.load(MODEL_OUTPUT_PATH)
encoders = joblib.load(ENCODER_PATH)  # Dictionary of encoders by column

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Extract form data using simplified ids
            input_data = {
                'lead_time': float(request.form['lead_time']),
                'special_requests': float(request.form['special_requests']),
                'avg_price': float(request.form['avg_price']),
                'arrival_month': int(request.form['arrival_month']),
                'arrival_date': int(request.form['arrival_date']),
                'market_segment': request.form['market_segment'],
                'week_nights': int(request.form['week_nights']),
                'weekend_nights': int(request.form['weekend_nights']),
                'meal_plan': request.form['meal_plan'],
                'room_type': request.form['room_type'],
            }

            # Prepare data for prediction
            features = np.array([[
                input_data['lead_time'],
                input_data['special_requests'],
                input_data['avg_price'],
                input_data['arrival_month'],
                input_data['arrival_date'],
                encoders['market_segment_type'].transform([input_data['market_segment']])[0],
                input_data['week_nights'],
                input_data['weekend_nights'],
                encoders['type_of_meal_plan'].transform([input_data['meal_plan']])[0],
                encoders['room_type_reserved'].transform([input_data['room_type']])[0],
            ]])

            # Make prediction
            prediction = model.predict(features)
            prediction_label = "Person Will Not Cancel" if prediction[0] == 1 else "Person Will Cancel"

            return render_template('index.html', prediction_text=str(prediction_label))
        except Exception as e:
            return render_template('index.html', prediction_text=f"Error: {str(e)}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
