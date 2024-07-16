import re
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
#Parses the tcl files and returns a DataFrame with the extracted data.

def parse_tcl_file(tcl_file):
    with open(tcl_file, 'r') as file:
        lines = file.readlines()

    data = []
    for line in lines:
        match = re.match(r'\$ns_ at (\d+.\d+) "\$node_\((\d+)\) setdest (\d+.\d+) (\d+.\d+) (\d+.\d+)"', line)
        if match:
            timestamp, node_id, x, y, speed = match.groups()
            data.append([float(timestamp), int(node_id), float(x), float(y), float(speed)])

    df = pd.DataFrame(data, columns=['timestamp', 'node_id', 'x', 'y', 'speed'])
    return df

# Parse the mobility.tcl file
mobility_df = parse_tcl_file('simulation_data/tcl/mobility.tcl')

aggregated_data = mobility_df.groupby('timestamp').agg({
    'speed': ['mean', 'std', 'max', 'min'],
    'node_id': 'count'
})

# Flatten the column hierarchy
aggregated_data.columns = ['_'.join(col).strip() for col in aggregated_data.columns.values]
aggregated_data.rename(columns={'node_id_count': 'vehicle_count'}, inplace=True)
aggregated_data['speed_std'].fillna(0, inplace=True)

print(aggregated_data.head())

#Preprocessing and Normalizations

from sklearn.preprocessing import MinMaxScaler

# Normalize the data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(aggregated_data)

# Convert to DataFrame
scaled_df = pd.DataFrame(scaled_data, columns=aggregated_data.columns, index=aggregated_data.index)

# Create sequences
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predict the mean speed
    return np.array(X), np.array(y)

seq_length = 10  # Example sequence length
X, y = create_sequences(scaled_data, seq_length)

# Reshape for LSTM (samples, timesteps, features)
X = X.reshape((X.shape[0], seq_length, X.shape[2]))

# Defined the LSTM model
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(seq_length, X.shape[2])))
model.add(Dense(1))  # Predicting a single value (mean speed)
model.compile(optimizer='adam', loss='mse')

# Training
history = model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# Evaluation
loss = model.evaluate(X, y)
print(f"Model Loss: {loss}")

# Predictions
predictions = model.predict(X)

# Inverse transform predictions to get them back to original scale
predictions_inverse = scaler.inverse_transform(
    np.concatenate([predictions, np.zeros((predictions.shape[0], scaled_data.shape[1] - 1))], axis=1)
)[:, 0]

# Comparing predictions with actual data

plt.plot(scaled_df.index[seq_length:], predictions_inverse, label='Predicted')
plt.plot(scaled_df.index[seq_length:], scaler.inverse_transform(scaled_data[seq_length:])[:, 0], label='Actual')
plt.title('Predicted vs. Actual Mean Speed')
plt.savefig('predicted_vs_actual.png')
plt.legend()
plt.show()