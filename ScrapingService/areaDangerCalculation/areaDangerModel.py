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

class areaDangerModel:
    def __init__(self, city):
        self.city = city
        pass

    def encodeTextVariablesInDataset (self, dataset, returnType='CLS'):

        # Load the Model, that in our case is a BERT-uncased
        model_name = "bert-base-uncased"  # Pre-trained BERT model
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)

        # Define the base of the sequence Array
        sentences = list(dataset['Article'])
        outputs = list(dataset['Crime'])

        sentencesWithOutput = {"Embedding": [], 'Output': []}
        for singleSentence, output in zip(sentences, outputs):

            # Logging
            print('Applying LLM sentence processing...', round((dataset.index[dataset['Article'] == singleSentence][0]
                                                                /len(list(dataset['Article']))) * 100, 2), '%')

            # Step 3: Tokenize the sentences and convert them to input tensors
            tokenized_inputs = tokenizer(singleSentence, padding=True, truncation=True, return_tensors="pt")

            # Generate the Embedding for BERT
            with torch.no_grad():
                embeddedSentence = model(**tokenized_inputs)

            sentenceEmbedding = np.full([1, 768], 0)
            if returnType == 'CLS':
                sentenceEmbedding = embeddedSentence.last_hidden_state[:, 0, :]
            if returnType == 'mean':
                # Alternative - Use the mean of the tokens as token itself
                sentenceEmbedding = embeddedSentence.last_hidden_state.mean(dim=1)
            sentencesWithOutput['Embedding'].append(sentenceEmbedding)
            sentencesWithOutput['Output'].append(outputs)

        # Save the dictionary
        torch.save(sentencesWithOutput, "embeddings_sentences_" + returnType.lower() + ".pt")

        # Verify some results
        print(f"Number of Elements 'Embedding': {len(sentencesWithOutput['Embedding'])}")
        print(f"Number of Elements in 'Output': {len(sentencesWithOutput['Output'])}")
        print(f"Shape of the First Embedding: {sentencesWithOutput['Embedding'][0].shape}")  # should be torch.Size([768])

        return sentencesWithOutput








