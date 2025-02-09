# Class to process data to compute how dangerous a street is
import pickle

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from datetime import datetime
from Utils import Database as d
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
import areaDangerDataProcessing as dp
from transformers import BertTokenizer, BertModel
import torch
import tensorflow as tf
import gensim
from gensim.models import Word2Vec

class areaDangerModel:
    def __init__(self):
        pass

    # Utils-like method for Word2Vec
    def text_to_embedding(self, text, model, vector_size=100):
        words = text.lower().split()
        vectors = [model.wv[word] for word in words if word in model.wv]

        if len(vectors) == 0:
            return np.zeros(vector_size)  # If empty, return a 0 array

        # Get the mean vectors
        return np.mean(vectors, axis=0)

    def encodeTextVariablesInDataset (self, dataset, model="bert-base-uncased", returnType='cls', predict=False):

        sentencesWithOutput = {"Embedding": [], 'Output': []}
        if model != 'Word2Vec':
            # Load the Model, that in our case is a BERT-uncased
            model_name = model  # Pre-trained BERT model
            tokenizer = BertTokenizer.from_pretrained(model_name)
            model = BertModel.from_pretrained(model_name)

            # Define the base of the sequence Array
            sentences = list(dataset['Article'])
            outputs = list(dataset['Crime'])

            for i, (singleSentence, output) in enumerate(zip(sentences, outputs)):

                # Logging
                print('Applying LLM sentence processing...', round(i/len(list(dataset['Article'])) * 100, 2), '%')

                # Step 3: Tokenize the sentences and convert them to input tensors
                tokenized_inputs = tokenizer(singleSentence, padding=True, truncation=True, return_tensors="pt")

                # Generate the Embedding for BERT
                with torch.no_grad():
                    embeddedSentence = model(**tokenized_inputs)

                sentenceEmbedding = np.full([1, 768], 0)
                if returnType == 'cls':
                    sentenceEmbedding = embeddedSentence.last_hidden_state[:, 0, :]
                if returnType == 'mean':
                    # Alternative - Use the mean of the tokens as token itself
                    sentenceEmbedding = embeddedSentence.last_hidden_state.mean(dim=1)
                sentencesWithOutput['Embedding'].append(sentenceEmbedding)
                sentencesWithOutput['Output'].append(outputs[i])

            # Save the dictionary
            if predict == False:
                torch.save(sentencesWithOutput, "embeddings_sentences_" + returnType.lower() + ".pt")

            # Verify some results
            print(f"Number of Elements 'Embedding': {len(sentencesWithOutput['Embedding'])}")
            print(f"Number of Elements in 'Output': {len(sentencesWithOutput['Output'])}")
            print(f"Shape of the First Embedding: {sentencesWithOutput['Embedding'][0].shape}")  # should be torch.Size([768])

        else:
            # Implement a simple Word2Vec Model
            # Tokeninze the data
            dataset['tokenized'] = dataset['Article'].apply(lambda x: x.lower().split())
            # Train the Word2Vec
            word2vec_model = Word2Vec(sentences=dataset['tokenized'], vector_size=100, window=5, min_count=1, workers=4)

            dataset['embedding'] = dataset['Article'].apply(lambda x: self.text_to_embedding(x, word2vec_model))

            # Get the embedding in the same shape as we did for BERT
            sentencesWithOutput['Embedding'].append(dataset['embedding'].values)
            sentencesWithOutput['Output'].append(dataset['Crime'].values)
            # Save the Embedding
            with open("word2vec_embeddings.pkl", "wb") as f:
                pickle.dump(sentencesWithOutput, f)

        return sentencesWithOutput

    # NN Model Itself, very simple one

    def trainAndStoreNNModelForNews (self, data, trainingEpochs, structure={'FF':[500, 500, 500], 'LSM':[]}, returnType = 'cls',
                                     modelName="bert-base-uncased"):

        # returns: x_train, x_test, y_train, y_test
        if modelName == "Word2Vec":
            x_train = np.vstack(data[0])
            x_test = np.vstack(data[1])
        else:
            x_train = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in data[0]])
            x_test = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in data[1]])
        y_train = np.array(data[2])
        y_test = np.array(data[3])

        # Convert Numbers
        x_train = x_train.astype(np.float32)

        print("Shape of X_train:", x_train.shape)

        # Define the Model with custom Structure
        model = tf.keras.Sequential()
        # Add the LSM layer, if present in structure
        if len(structure['LSM']) > 0:
            # Expand dimensions to add timestamp
            model.add(tf.keras.layers.Reshape((1, x_train.shape[1]), input_shape=(x_train.shape[1],)))
            for l in range(len(structure['LSM'])):
                units = structure['LSM'][l]
                if l == 0:
                    # Input_shape required on the first layer
                    layer = tf.keras.layers.LSTM(units, activation='tanh', return_sequences=True, input_shape=(None, x_train.shape[1]))
                else:
                    # For others, no issues
                    # Remove the timestamp param if the layer is the last one of the LSM Structure
                    if l == len(structure['LSM']) - 1:
                        layer = tf.keras.layers.LSTM(units, activation='tanh', return_sequences=False)
                    else:
                        layer = tf.keras.layers.LSTM(units, activation='tanh', return_sequences=True)
                model.add(layer)
        # then, add the FF layer
        for l in range(len(structure['FF'])):
            unitsFF = structure['FF'][l]
            layerFF = tf.keras.layers.Dense(unitsFF, activation='relu')
            model.add(layerFF)
        model.add(tf.keras.layers.Dense(2))

        # Compile
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        # Now, Train the Model
        model.fit(x_train, y_train, epochs=trainingEpochs)

        # Evaluate on Test set
        test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
        print('Test accuracy:', test_acc)
        # Get The probabilities adding a SoftMax layer
        probability_model = tf.keras.Sequential([model,tf.keras.layers.Softmax()])

        # Save in H5 Format
        if modelName.lower() != 'word2vec':
            model_name = 'CrimeModel_' + modelName + '_' + returnType + '.h5'
            probability_model.save(model_name)
        else:
            model_name = 'CrimeModel_W2V.h5'
            probability_model.save(model_name)
        print('Model saved Correctly with the name of ' + model_name)

        return probability_model



















