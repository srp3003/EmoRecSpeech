import sys
import os
import scipy.io.wavfile as wavfile
import numpy as np
from energy import getTopEnergySegmentsIndices
from featureExtraction import extractFeatures, getSegmentFeaturesUsingIndices
from sklearn.externals import joblib
import pandas as pd

def main():
    # load file for csv dataset
    CSV_DATASET = os.path.dirname(os.path.realpath(__file__)) + "/datasetForELM.csv"
    # CSV_DATASET = os.path.dirname(os.path.realpath(__file__)) + "datasetForELM_test.csv"
    csv_dataset = open(CSV_DATASET, "w+")

    # load scaler
    scaler = joblib.load("scalerParameters.sav")
    print("Scaler loaded...")
    
    # load dnn
    dnn = joblib.load("dnnParameters.sav")
    print("DNN loaded...")

    # get the dataset ready
    df = pd.read_csv("datasetForDNN.csv", header=None)
    print("Dataset loaded into dataframe...")
    
 
    # Split into X and y
    utteranceNames = df.iloc[:,0] # get utteranceNames
    utteranceNamesList = []
    for utteranceName in utteranceNames:
        if utteranceName not in utteranceNamesList:
            utteranceNamesList.append(utteranceName)
    
    X = df.iloc[:, 1:-1].values # remove the utteranceName and target emotionLabelNum
    y = df.iloc[:, -1].values # get target emotionLabelNum
    print("X and y loaded....")
   
    # normalize the data
    X = scaler.transform(X)
    print("Data normalized...")
    
    # calculate probabilities for all samples
    probabilities = dnn.predict_proba(X)
    print("Probabilities calculated...")
   
    print("Generating utterance feature vectors...")
    # setup progressBar
    progressBarWidth = 50
    sys.stdout.write("[%s]" % (" " * progressBarWidth))
    sys.stdout.flush()
    sys.stdout.write("\b" * (progressBarWidth+1)) # return to start of line, after '['
    sys.stdout.flush()

    progressBarUpdatePerUtterance = int(len(utteranceNamesList)/progressBarWidth)
    utteranceCount = 0

    df = df.set_index(0) # sets the utteranceNames as index
    segmentIndex = 0
    for utteranceName in utteranceNamesList:
    # utteranceName = utteranceNames[0]
        utteranceEmotionLabelNum = df.loc[utteranceName].iloc[0,-1] # emotion for the first segment of the utterance
        numberOfSegmentsPerUtterance = len(df.loc[utteranceName])

        utteranceProbabilities = probabilities[segmentIndex:(segmentIndex+numberOfSegmentsPerUtterance),:]
        # create the feature vector for utterance
        feat1 = np.amax(utteranceProbabilities, axis=0)
        feat2 = np.amin(utteranceProbabilities, axis=0)
        feat3 = np.mean(utteranceProbabilities, axis=0)

        prob0 = utteranceProbabilities[:,0]
        prob1 = utteranceProbabilities[:,1]
        prob2 = utteranceProbabilities[:,2]
        prob3 = utteranceProbabilities[:,3]

        count0 = np.sum(prob0[prob0>0.2])/numberOfSegmentsPerUtterance
        count1 = np.sum(prob1[prob1>0.2])/numberOfSegmentsPerUtterance
        count2 = np.sum(prob1[prob2>0.2])/numberOfSegmentsPerUtterance
        count3 = np.sum(prob1[prob3>0.2])/numberOfSegmentsPerUtterance
        feat4 = np.array([count0, count1, count2, count3])

        featureVector = np.hstack([feat1, feat2, feat3, feat4])
        featureVectorString = ",".join(["%.8f" % num for num in featureVector])
        featureVectorString = utteranceName + "," + featureVectorString + "," + str(int(utteranceEmotionLabelNum))
        csv_dataset.write(featureVectorString + "\n")

        segmentIndex = numberOfSegmentsPerUtterance
        
        # update the progressBar
        utteranceCount += 1
        if (utteranceCount % progressBarUpdatePerUtterance == 0) and (int(utteranceCount/progressBarUpdatePerUtterance) <= 50): # won't let the progressbar #'s exceed 50 repetitions
            sys.stdout.write("#")
            sys.stdout.flush()

    sys.stdout.write("\n")
    csv_dataset.close()

if __name__ == '__main__':
    main()