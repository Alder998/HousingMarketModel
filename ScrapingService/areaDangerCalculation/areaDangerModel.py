# Class to process data to compute how dangerous a street is

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

class areaDangerModel:
    def __init__(self):
        pass

    def encodeTextVariablesInDataset (self, dataset, model="bert-base-uncased", returnType='cls', predict=False):

        # Load the Model, that in our case is a BERT-uncased
        model_name = model  # Pre-trained BERT model
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)

        # Define the base of the sequence Array
        sentences = list(dataset['Article'])
        outputs = list(dataset['Crime'])

        sentencesWithOutput = {"Embedding": [], 'Output': []}
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

        return sentencesWithOutput

    # NN Model Itself, very simple one

    def trainAndStoreNNModelForNews (self, data, trainingEpochs, structure=[500, 500, 500], returnType = 'cls'):

        # returns: x_train, x_test, y_train, y_test
        x_train = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in data[0]])
        x_test = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in data[1]])
        y_train = np.array(data[2])
        y_test = np.array(data[3])

        # Convert Numbers
        x_train = x_train.astype(np.float32)

        print("Shape of X_train:", x_train.shape)

        # Define the Model with custom Structure
        model = tf.keras.Sequential()
        for l in range(len(structure)):
            layer = tf.keras.layers.Dense(structure[l], activation='relu')
            model.add(layer)
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
        probability_model.save('CrimeModel_' + returnType + '.h5')
        print('Model saved Correctly')

        return probability_model



















