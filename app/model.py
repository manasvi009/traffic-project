import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Sample dataset
data = {
    "distance": [5, 10, 15, 20, 8, 12],
    "speed": [40, 50, 60, 45, 35, 55],
    "time_of_day": [8, 10, 18, 20, 9, 17],
    "traffic": [1, 2, 3, 2, 1, 3],
    "weather": [0, 0, 1, 1, 0, 1],
    "road": [1, 2, 1, 2, 3, 1],
    "travel_time": [10, 15, 25, 30, 12, 22]
}

df = pd.DataFrame(data)

X = df.drop("travel_time", axis=1)
y = df["travel_time"]

model = LinearRegression()
model.fit(X, y)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model created successfully!")