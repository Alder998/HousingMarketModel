# This is the main Model (pricing Model) Module
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

class PricingModel:
    def __init__(self):
        pass

    # Utils-like Model for train and test split
    def trainTestSplit (self, data, predictors, outputCol, test_size):

        X_train, X_test, y_train, y_test = train_test_split(
            data[predictors].values, data[outputCol], test_size=test_size, random_state=1893)

        return X_train, X_test, y_train, y_test

    # It is gonna be a really simple Neural-Network regression
    def trainAndStorePricingModel (self, city, data, trainingEpochs, structure={'FF':[500, 500, 500]}, save = True):

        # Get the test data
        x_train = np.vstack(data[0])
        x_test = np.vstack(data[1])
        y_train = np.array(data[2])
        y_test = np.array(data[3])

        # Model
        model = tf.keras.Sequential()

        for l in range(len(structure['FF'])):
            unitsFF = structure['FF'][l]
            layerFF = tf.keras.layers.Dense(unitsFF, activation='relu')
            model.add(layerFF)
        model.add(tf.keras.layers.Dense(1))  # 1 neuron to achieve regression

        # Compile for regression
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.MeanSquaredError(),
                      metrics=['mae'])
        # Now, Train the Model
        print(x_train)
        print(y_train)

        model.fit(x_train, y_train, epochs=trainingEpochs)

        # Evaluate on Test set
        test_loss, test_mae = model.evaluate(x_test, y_test, verbose=2)
        print(f"Mean Absolute Error (MAE) on the test set: {test_mae}")

        # Save the model
        if save:
            model_name = 'PricingModel_' + city + '.h5'
            model.save(model_name)

        return test_mae

    def createOrUpdatePricingModel (self, city, data, predictors, outputCol, test_size, trainingEpochs, NNstructure, save):

        # Train-test Split
        dataForModel = self.trainTestSplit(data, predictors, outputCol, test_size)

        # Train, Test, Save the NN Model
        model = self.trainAndStorePricingModel(city, dataForModel, trainingEpochs, NNstructure, save)

        return model