# Model to do miscellaneous stuff

import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import pickle
from sklearn.neighbors import KNeighborsClassifier

class generalPurposeModels:
    def __init__(self, city):
        self.city = city
        pass

    # Area from coordinates functions
    def trainModelForAreaPrediction (self, data, test_size, coord_filters, model='SVC'):

        # Filter for city Coordinates
        data = data[((data['Latitude'] > coord_filters[0]) &
                                   (data['Latitude'] < coord_filters[1])) & ((data['Longitude'] > coord_filters[2]) &
                                   (data['Longitude'] < coord_filters[3]))].reset_index(drop=True)

        # clean as much as possible, removing the areas that has few number of Observation
        counts = data['Area'].value_counts()
        data = data[data['Area'].isin(counts[counts >= 5].index)].reset_index(drop=True)

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
        if model == 'SVC':
            mod = SVC(kernel='linear')
            mod.fit(x_train, y_train)
            predictions = mod.predict(x_test)
            accuracy = accuracy_score(y_test, predictions)
            print('Accuracy: ', round(accuracy*100, 4), '%')
        elif model == 'KNN':
            mod = KNeighborsClassifier(n_neighbors=len(data['Area'].unique()))
            mod.fit(x_train, y_train)
            predictions = mod.predict(x_test)
            accuracy = accuracy_score(y_test, predictions)
            print('Accuracy: ', round(accuracy*100, 4), '%')
        else:
            raise Exception("Model not specified!")

        # Store Model for Future Purposes, if it does not Exist
        path = "AreaPredictionModel_" + self.city + "_" + model + ".pkl"
        if not os.path.exists(path):
            with open(path, "wb") as f:
                pickle.dump(mod, f)
            print('Model ' + path + ' Correctly Saved!')
        else:
            print("Using Stored Model " + path + " ...")

        return accuracy

    def predictAreaFromCoordinates (self, dataToPredict, model='SVC'):

        path = "AreaPredictionModel_" + self.city + "_" + model + ".pkl"
        # Load model if stored, else raise Exception
        if not os.path.exists(path):
            raise Exception ('Model Not Existing!')

        # Load Model
        with open(path, "rb") as f:
            loaded_model = pickle.load(f)
        # Predict
        predictions = loaded_model.predict(dataToPredict)

        return predictions

