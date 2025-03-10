from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib
import os

class IntentClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', MultinomialNB())
        ])

    def train(self, data_file):
        data = pd.read_csv(data_file)
        X = data['text']
        y = data['intent']
        self.pipeline.fit(X, y)

    def predict(self, text):
        return self.pipeline.predict([text])[0]

    def save_model(self, model_path):
        joblib.dump(self.pipeline, model_path)

    def load_model(self, model_path):
        self.pipeline = joblib.load(model_path)

def train():
    model_dir = 'd:/Trolyaodocbaoweb/trolyaodocbao/myapp/models'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    classifier = IntentClassifier()
    classifier.train('d:/Trolyaodocbaoweb/trolyaodocbao/myapp/data/intent_data.csv')
    classifier.save_model(os.path.join(model_dir, 'intent_model.joblib'))
    print("Model trained and saved successfully!")

if __name__ == "__main__":
    train()