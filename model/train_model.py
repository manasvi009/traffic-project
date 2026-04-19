import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# Load data
features = pd.read_csv("../data/delhi_traffic_features.csv")
target = pd.read_csv("../data/delhi_traffic_target.csv")

# Merge
df = features.merge(target, on="Trip_ID")

# Drop ID
df.drop("Trip_ID", axis=1, inplace=True)

# One-hot encoding
df = pd.get_dummies(df, drop_first=True)

# Split
X = df.drop("travel_time_minutes", axis=1)
y = df["travel_time_minutes"]

# Save column names ✅ IMPORTANT
joblib.dump(X.columns.tolist(), "columns.pkl")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = XGBRegressor()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "traffic_model.pkl")

print("✅ Model + columns saved!")