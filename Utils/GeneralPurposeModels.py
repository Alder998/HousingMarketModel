# Model to do miscellaneous stuff

import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import pickle

class generalPurposeModels:
    def __init__(self, city):
        self.city = city
        pass

    # Area from coordinates functions
    def trainModelForAreaPrediction (self, data, test_size, coord_filters):

        # clean as much as possible, removing the areas that has few number of Observation
        counts = data['Area'].value_counts()
        data = data[data['Area'].isin(counts[counts >= 10].index)].reset_index(drop=True)
        # Filter for city Coordinates
        data = data[((data['Latitude'] > coord_filters[0]) &
                                   (data['Latitude'] < coord_filters[1])) & ((data['Longitude'] > coord_filters[2]) &
                                   (data['Longitude'] < coord_filters[3]))].reset_index(drop=True)

        # Encode Areas for numeric Values, provide decodification
        # A little bit of stats
        print('Dataset Size:', len(data['Address']))
        print('Number of Labels:', len(data['Area'].unique()))
        encodeData = []
        for i, singleArea in enumerate(data['Area'].unique()):
            df = pd.DataFrame(
                pd.concat([pd.Series(singleArea), pd.Series(i)], axis=1).set_axis(['Area', 'code'], axis=1))
            encodeData.append(df)
        encodeData = pd.concat([sdf for sdf in encodeData]).reset_index(drop=True)
        # Translate codes
        for ar in range(len(encodeData['Area'])):
            data.loc[data['Area'] == encodeData['Area'][ar], 'Area_enc'] = encodeData['code'][ar]

        # Splitting our data
        X = data[['Latitude', 'Longitude']]
        y = data['Area']
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1893)

        # Model Part
        clf = SVC(kernel='rbf')
        clf.fit(x_train, y_train)
        predictions = clf.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        print('Accuracy: ', round(accuracy*100, 4), '%')

        # Store Model for Future Purposes, if it does not Exist
        path = "AreaPredictionModel_" + self.city + ".pkl"
        if not os.path.exists(path):
            with open(path, "wb") as f:
                pickle.dump(clf, f)
            print('Model ' + path + ' Correctly Saved!')
        else:
            print("Using Stored Model " + path + " ...")

        return accuracy

    def predictAreaFromCoordinates (self, coordinates):



        return 0

