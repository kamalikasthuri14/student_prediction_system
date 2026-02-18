import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# Create sample dataset
data = {
    "attendance": [90, 85, 40, 60, 75, 50, 95, 30, 70, 88],
    "internal": [85, 80, 35, 55, 70, 45, 92, 25, 65, 84],
    "assignment": [88, 78, 30, 50, 72, 40, 94, 28, 68, 86],
    "final": [90, 82, 33, 58, 74, 48, 96, 29, 69, 89],
    "result": [1, 1, 0, 0, 1, 0, 1, 0, 1, 1]
}

df = pd.DataFrame(data)

X = df[["attendance", "internal", "assignment", "final"]]
y = df["result"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved successfully!")