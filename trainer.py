import re
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

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

mobility_df = parse_tcl_file('simulation_data/tcl/mobility.tcl')

aggregated_data = mobility_df.groupby('timestamp').agg({
    'speed': ['mean', 'std', 'max', 'min'],
    'node_id': 'count'
})

aggregated_data.columns = ['_'.join(col).strip() for col in aggregated_data.columns.values]
aggregated_data.rename(columns={'node_id_count': 'vehicle_count'}, inplace=True)
aggregated_data['speed_std'].fillna(0, inplace=True)

print(aggregated_data.head())

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(aggregated_data)

scaled_df = pd.DataFrame(scaled_data, columns=aggregated_data.columns, index=aggregated_data.index)

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])
    return np.array(X), np.array(y)

seq_length = 10
X, y = create_sequences(scaled_data, seq_length)

X = X.reshape((X.shape[0], seq_length, X.shape[2]))

model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(seq_length, X.shape[2])))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

history = model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

loss = model.evaluate(X, y)
print(f'Model loss: {loss}')

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()

predicted_speed = model.predict(X[-1].reshape(1, seq_length, X.shape[2]))
predicted_speed = scaler.inverse_transform(np.concatenate((predicted_speed, np.zeros((predicted_speed.shape[0], X.shape[2] - 1))), axis=1))[:, 0]

print(f'Predicted Speed: {predicted_speed[0]}')

model.save('models/traffic_model.h5')
