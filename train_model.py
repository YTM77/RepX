# train_model.py
# Step 2 of training. Trains the exercise classifier on exercise_data.csv.
# 1 in every 5 videos is kept apart for testing, so the test is on videos the model never saw.
# We try 3 classification techniques, print how accurate each one is and save the best.

import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from exercise_detector import MODEL_FILE

# Load the data
data = pd.read_csv("exercise_data.csv")
print("Rows:", len(data), "  videos:", data["video"].nunique())
print(data["exercise"].value_counts().to_string())

# Split by video
videos = sorted(data["video"].unique())
test_videos = videos[::5]
train = data[~data["video"].isin(test_videos)]
test = data[data["video"].isin(test_videos)]

X_train = train.drop(columns=["exercise", "video"]).to_numpy()
y_train = train["exercise"].to_numpy()
X_test = test.drop(columns=["exercise", "video"]).to_numpy()
y_test = test["exercise"].to_numpy()

# Try 3 classifiers
models = {
    "K-Nearest Neighbours": KNeighborsClassifier(n_neighbors=5),
    "Decision Tree": DecisionTreeClassifier(random_state=0),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=0),
}

best_name, best_accuracy = None, 0
for name, model in models.items():
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(name, "accuracy:", round(accuracy * 100, 1), "%")
    if accuracy >= best_accuracy:
        best_name, best_accuracy = name, accuracy

# Results of the best model
best = models[best_name]
print("\nBest:", best_name)
labels = list(best.classes_)
table = confusion_matrix(y_test, best.predict(X_test), labels=labels)
print(pd.DataFrame(table, index=labels, columns=labels).to_string())

# Save the model
with open(MODEL_FILE, "wb") as f:
    pickle.dump(best, f)
print("Saved", MODEL_FILE)
