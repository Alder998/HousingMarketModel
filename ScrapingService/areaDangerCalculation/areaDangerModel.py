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

    def encodeTextVariablesInDataset (self):

        dataset = dp.areaDangerProcessing(self.city).createBinaryCrimeDataset()

        # Step 1: Import a pre-trained BERT model and tokenizer
        model_name = "bert-base-uncased"  # Pre-trained BERT model
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)

        # Step 2: Define an array of sentences
        sentences = list(dataset['Article'][0:500])

        # Step 3: Tokenize the sentences and convert them to input tensors
        tokenized_inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

        # Genera gli embedding con il modello BERT
        with torch.no_grad():
            outputs = model(**tokenized_inputs)

        # CLS Token for every sentence
        cls_embeddings = outputs.last_hidden_state[:, 0, :]  # Vettori [CLS]

        # Alternative - Use the mean of the tokens as token itself
        mean_embeddings = outputs.last_hidden_state.mean(dim=1)

        # Stampare o salvare le features per usarle in una rete neurale
        print(cls_embeddings)
        print(mean_embeddings)

        return tokenized_inputs







