import joblib
import pandas as pd

model = joblib.load('models/traffic_model.h5')

scenario_data = pd.read_csv('scenario_data.csv')

X_scenario = scenario_data[features]

predictions = model.predict(X_scenario)

scenario_data['predicted_impact'] = predictions
print(scenario_data)
