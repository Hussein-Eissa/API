import pandas as pd
import joblib

# Load the saved model and preprocessing objects
model = joblib.load('arrhythmia_risk_model.pkl')
scaler = joblib.load('scaler.pkl')
selector = joblib.load('selector.pkl')
encoder = joblib.load('encoder.pkl')

# Function to preprocess the input data
def preprocess_input(data):
    player_names = data['Name']
    # Drop unnecessary columns (if any)
    data.drop(columns=['Name','Unnamed: 0', 'VentricularRate (bpm).1'], inplace=True, errors='ignore')

    # Encode categorical variable 'Race'
    race_encoded = encoder.transform(data[['Race']])
    encoded_data = pd.DataFrame(race_encoded, columns=encoder.get_feature_names_out(['Race']))
    data = pd.concat([data, encoded_data], axis=1).drop(columns=['Race'])

    # Create new features
    data["BMI"] = data["Weight (Kg)"] / ((data["Height (cm)"] / 100) ** 2)
    data["Pulse Pressure"] = data["SysBP (mmHg)"] - data["DiaBP (mmHg)"]
    data["HRV"] = data["RRInterval (ms)"] - data["PPInterval (ms)"]

    # Feature selection
    X_selected = selector.transform(data)

    # Scale the data
    X_scaled = scaler.transform(X_selected)

    return X_scaled , player_names

# Function to make predictions
def predict_play_probability(file_path):
    # Load the Excel file
    data = pd.read_excel('/Data/DefualtData.xlsx', sheet_name='Sheet1')

    # Preprocess the input data
    X_processed, player_names = preprocess_input(data)

    # Make predictions
    probabilities = model.predict_proba(X_processed)[:, 0]  # Probability of class 1 (Arrhythmia Risk)
    Play_Probability = probabilities * 100  # Convert to percentage

    results = pd.DataFrame({
        'Name': player_names,
        'Play Probability (%)': Play_Probability
    })

    results = results.sort_values(by='Play Probability (%)', ascending=False)

    json_result = results.to_dict(orient='records')
    # json_result = results.sort_values(by='Play Probability (%)', ascending=False).to_json(orient='records')
    
    # Display the results
    # print("Json",json_result)  # Assuming 'Player Name' is a column in the Excel file
    # print("DataFrame",results)  # Assuming 'Player Name' is a column in the Excel file

    return json_result

# Example usage
# J_Res = predict_play_probability('/kaggle/input/dataset/LabelData - new -Copy.xlsx')