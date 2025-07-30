import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

def predict(X_train, X_test, y_train, k=3):
    predictions = []
    for test_point in X_test:
        # Calculate distances from the test point to all training points
        distances = np.linalg.norm(X_train - test_point, axis=1)
        # Get indices of k-nearest neighbors
        k_nearest_neighbors = np.argsort(distances)[:k]
        # Get the labels of the k-nearest neighbors
        k_nearest_labels = y_train[k_nearest_neighbors]
        # Predict the most common label among the neighbors
        most_common = Counter(k_nearest_labels).most_common(1)
        predictions.append(most_common[0][0])
    return np.array(predictions)

def weighted_predict(X_train, X_test, y_train, k=3):
    predictions = []
    for test_point in X_test:
        # Calculate distances from the test point to all training points
        distances = np.linalg.norm(X_train - test_point, axis=1)
        # Get indices of k-nearest neighbors
        k_nearest_neighbors = np.argsort(distances)[:k]
        # Get the labels and distances of the k-nearest neighbors
        k_nearest_labels = y_train[k_nearest_neighbors]
        k_nearest_distances = distances[k_nearest_neighbors]
        
        # Assign weights to each neighbor based on 1 / distance^2
        weights = 1 / (k_nearest_distances ** 2)
        
        # Calculate weighted votes for each class
        weighted_votes = Counter()
        for i, label in enumerate(k_nearest_labels):
            weighted_votes[label] += weights[i]
        
        # Predict the label with the highest weighted vote
        predictions.append(weighted_votes.most_common(1)[0][0])
    
    return np.array(predictions)

def evaluate_model(X_train, X_test, y_train, y_test, k_values, f1_score, accuracy_score):
    results = {}
    for k in k_values:
        # Regular k-NN
        y_pred_knn = predict(X_train, X_test, y_train, k)
        accuracy_knn = accuracy_score(y_test, y_pred_knn)
        f1_knn = f1_score(y_test, y_pred_knn, average='weighted')
        
        # Weighted k-NN
        y_pred_weighted_knn = weighted_predict(X_train, X_test, y_train, k)
        accuracy_weighted_knn = accuracy_score(y_test, y_pred_weighted_knn)
        f1_weighted_knn = f1_score(y_test, y_pred_weighted_knn, average='weighted')
        
        # Store results
        results[k] = {
            'Accuracy (k-NN)': accuracy_knn,
            'F1-score (k-NN)': f1_knn,
            'Accuracy (Weighted k-NN)': accuracy_weighted_knn,
            'F1-score (Weighted k-NN)': f1_weighted_knn
        }
    
    return results