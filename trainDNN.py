import os
import sys
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.metrics import classification_report, confusion_matrix

def main():
    DIR = os.path.dirname(os.path.realpath(__file__))

    # Get data into X and y
    df = pd.read_csv(DIR + "/datasetForDNN.csv", header=None)
    print("Dataset loaded into dataframe...")

    # Split into X and y
    utteranceNames = df.iloc[:,0] # get utteranceNames
    X = df.iloc[:, 1:-1].values # remove the utteranceName and target emotionLabelNum
    y = df.iloc[:, -1].values # get target emotionLabelNum
    print("X and y loaded....")
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    print("Training and testing sets created...")

    # Normalize data
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    print("X_train and X_test normalized...")

    # Save scaler parameters for normalizing test data
    scalerParametersDump = DIR  + "/scalerParameters.sav" 
    # scalerParametersDump = "scalerParameters_test.sav"
    joblib.dump(scaler, scalerParametersDump)

    
    dnn = MLPClassifier(hidden_layer_sizes=(500), activation='relu',
                        solver='adam', max_iter=100, verbose=True,
                        early_stopping=True, validation_fraction=0.1)

    # Train
    tStart = time.time()
    print("Training DNN...")
    dnn.fit(X_train, y_train)
    
    tEnd = time.time()
    print("DNN trained in " + str(tEnd-tStart) + " seconds ...")
    
    # Make the model persistent
    dnnParametersDump = DIR + "/dnnParameters.sav" # TODO add a dummy line here, for demo
    # dnnParametersDump = "dnnParameters_test.sav"
    joblib.dump(dnn, dnnParametersDump)
    # for loading -> dnn = joblib.load("dnnParameters.sav")

    # PRINTING TRAINING AND TESTING SCORES
    print("TRAINING SET SCORE : %f" % dnn.score(X_train, y_train))
    print("TESTING SET SCORE : %f" % dnn.score(X_test, y_test))

    # Classification report and confusion matrix on test data
    predictions = dnn.predict(X_test)
    print("CONFUSION MATRIX for testing data : ") 
    print(confusion_matrix(y_test, predictions))
    print("CLASSIFICATION REPORT for testing data :")
    print(classification_report(y_test, predictions))
   

if __name__ == '__main__':
    main()