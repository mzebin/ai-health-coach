#!/usr/bin/env python
"""
Train intent classifier using TF-IDF + Logistic Regression.
Saves model and vectorizer to models/ directory.
"""

import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def main():
    # Load training data
    data_path = os.path.join('data', 'intent_training.csv')
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} training examples.")
    print("Intent distribution:")
    print(df['intent'].value_counts())

    # Split features and labels
    X = df['query']
    y = df['intent']

    # Split into train/test for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        stop_words='english',
        lowercase=True
    )

    # Fit vectorizer on training queries
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train logistic regression
    classifier = LogisticRegression(max_iter=1000, random_state=42)
    classifier.fit(X_train_vec, y_train)

    # Evaluate
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and vectorizer
    os.makedirs('models', exist_ok=True)
    joblib.dump(vectorizer, os.path.join('models', 'vectorizer.pkl'))
    joblib.dump(classifier, os.path.join('models', 'intent_classifier.pkl'))
    print("\nModel and vectorizer saved to models/")


if __name__ == '__main__':
    main()
