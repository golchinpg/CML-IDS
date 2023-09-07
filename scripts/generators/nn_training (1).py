#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 16:44:22 2023

@author: pegah
"""

import pandas as pd
import numpy as np
import glob
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import joblib
from sklearn.metrics import classification_report, confusion_matrix
from keras import models, activationsm, Model
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Input, Dense, Dropout
from keras.layers import Dense
from keras.layers import GaussianNoise
from keras.layers import BatchNormalization
from keras.layers import LeakyReLU, ReLU, ELU
from sklearn.metrics import precision_recall_fscore_support
from keras.callbacks import LearningRateScheduler
from keras.callbacks import ReduceLROnPlateau
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn import preprocessing
from xgboost import XGBClassifier

# %%


class Neural_Network_training:
    def __init__(self):
        self.save_model_path = '/home/pegah/collaborative-nids-chengbozhou-code/'
        self.df = pd.read_csv(
            self.save_model_path+'preprocessed_balanced_wo_time_equal_8_merged.csv', sep=',', header=0)
        print('dataframe shape:', self.df.shape)
        print('columns:', self.df.columns)
        self.input_dim = self.df.shape[1]-1

    def split_dataset(self):
        # minmax normalization
        scaler = preprocessing.MinMaxScaler()
        d = scaler.fit_transform(self.df)
        scaled_df = pd.DataFrame(d, columns=self.df.columns)
        # print(scaled_df.head())
        X_tot, X_test, y_tot, y_test = train_test_split(
            self.df.iloc[:, :-1], self.df['Label'], test_size=0.2, random_state=42, stratify=self.df['Label'])
        X_train, X_val, y_train, y_val = train_test_split(
            self.df.iloc[:, :-1], self.df['Label'], test_size=0.1, random_state=42, stratify=self.df['Label'])
        #X_tot, X_test, y_tot, y_test = train_test_split(scaled_df.iloc[:,:-1], scaled_df['Label'], test_size=0.2, random_state=42, stratify=scaled_df['Label'])
        #X_train, X_val, y_train, y_val = train_test_split(scaled_df.iloc[:,:-1], scaled_df['Label'], test_size=0.1, random_state=42, stratify=scaled_df['Label'])
        return (X_train, X_test, y_train, y_test, X_val, y_val)

    def training(self, X_train, y_train, X_val, y_val, model_name):
        """
        def lr_scheduler(epoch, lr):
            decay_rate = 0.85
            decay_step = 30
            if epoch % decay_step == 0 and epoch:
                return lr * pow(decay_rate, np.floor(epoch / decay_step))
            return lr
        """
        lr_scheduler = ReduceLROnPlateau(
            monitor='val_loss', factor=0.1, patience=10, min_lr=0.0000001)
        checkpoint = ModelCheckpoint(
            '/home/pegah/collaborative-nids-chengbozhou-code/model6.h5', monitor='val_accuracy', save_best_only=True)
        early_stopping = EarlyStopping(monitor='train_loss',
                                       min_delta=0,
                                       patience=30,
                                       mode='decrease')
        callbacks = [lr_scheduler, checkpoint, early_stopping]
        #reduce_lr = ReduceLROnPlateau(monitor = 'val_loss', factor = 0.2, patience= 5)
        elu_alpha = 0.1
        if 'NN' in model_name:
            model = Sequential()
            model.add(Dense(60, activation='relu',
                      kernel_initializer='he_uniform', input_dim=self.input_dim))
            # model.add(BatchNormalization())
            model.add(Dense(70))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())
            # model.add(LeakyReLU(alpha=0.2))#(alpha=0.2))
            #model.add(ELU(alpha = elu_alpha))
            model.add(Dropout(0.1))
            # model.add(BatchNormalization())
            model.add(Dense(90))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())
            # model.add(LeakyReLU(alpha=0.2))#(alpha=0.2))
            #model.add(ELU(alpha = elu_alpha))
            model.add(Dense(100))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())
            model.add(Dropout(0.2))

            model.add(Dense(90))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())

            model.add(Dense(60))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())
            # model.add(ReLU())#(alpha=0.2))
            #model.add(ELU(alpha = elu_alpha))
            model.add(Dropout(0.2))
            model.add(Dense(30))
            model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
            model.add(BatchNormalization())
            # model.add(LeakyReLU(alpha=0.2))#(alpha=0.2))
            #model.add(ELU(alpha = elu_alpha))
            # model.add(Dropout(0.1))
            # model.add(BatchNormalization())
            model.add(Dense(15))
            model.add(LeakyReLU(alpha=0.2))
            model.add(BatchNormalization())
            # model.add(LeakyReLU(alpha=0.2))
            #model.add(ELU(alpha = elu_alpha))
            # model.add(Dropout(0.2))
            model.add(Dense(1, activation='sigmoid'))
            model.summary()

            model.compile(loss='binary_crossentropy', optimizer='adam', metrics=[
                          'accuracy', 'Precision', 'Recall'])
            # model training
            history = model.fit(X_train, y_train, batch_size=1024, epochs=200,
                                callbacks=callbacks, shuffle=True, validation_data=(X_val, y_val))
            plt.plot(history.history['accuracy'], label='Training Accuracy')
            plt.plot(history.history['val_accuracy'],
                     label='Validation Accuracy')
            plt.title('training / validation accuracy values')
            plt.ylabel('Accuracy')
            plt.xlabel('Epoch')
            plt.legend(loc="best")
            plt.show()
            plt.plot(history.history['loss'], label='Training loss')
            plt.plot(history.history['val_loss'], label='Validation loss')
            plt.title('training / validation loss values')
            plt.ylabel('Loss value')
            plt.xlabel('Epoch')
            plt.legend(loc="best")
            plt.show()
            model_nn = model

        if 'xgb' in model_name:
            print("##################################")
            print('\n')
            print('####### Training XGBoost##########')
            print('\n')
            print("##################################")

            model = XGBClassifier()
            model.fit(X_train, y_train)
            y_predict = model.predict(X_val)
            print("=== Confusion Matrix for validation set ===")
            print(confusion_matrix(y_val, y_predict))
            print('\n')
            print("=== Classification Report for validation set ===")
            print(classification_report(y_val, y_predict))
            print('\n')
            model_xgb = model

        if 'rf' in model_name:
            print("##################################")
            print('\n')
            print('#### Training RandomForest #######')
            print('\n')
            print("##################################")
            model = RandomForestClassifier(n_estimators=500)
            model.fit(X_train, y_train)
            y_predict = model.predict(X_val)

            print("=== Confusion Matrix for validation set ===")
            print(confusion_matrix(y_val, y_predict))
            print('\n')
            print("=== Classification Report for validation set ===")
            print(classification_report(y_val, y_predict))
            print('\n')
            model_rf = model
        return (model_nn, model_xgb, model_rf)

    def load_model(self, model_path):
        model = load_model(model_path)
        return (model)

    def test_set(self, model_name, model_nn, model_rf, model_xgb, X_test, y_test):
        #y_predict = (model.predict(X_test) > 0.5).astype(int)
        if "rf" in model_name:
            y_predict_rf = model_rf.predict_proba(X_test)
            # print('rf:')
            # print(y_predict_rf)
            # print(type(y_predict_rf))
            # print(len(y_predict_rf))
            # print(y_predict_rf.shape)
        if "xgb" in model_name:
            y_predict_xgb = model_xgb.predict_proba(X_test)
            # print('xgb:')
            # print(y_predict_xgb)
        if "NN" in model_name:
            def predict_prob(number):
                return [1-number[0], number[0]]
            y_predict_nn = np.array(
                list(map(predict_prob, model_nn.predict(X_test))))
            #y_predict_nn = model_nn.predict(X_test[0:50])
            # print('nn:')
            # print(y_predict_nn)
            # print(type(y_predict_nn))
            # print(len(y_predict_nn))
            # print(y_predict_nn.shape)
        avg_probability = np.mean(
            np.array([y_predict_rf, y_predict_xgb, y_predict_nn]), axis=0)
        predict_classes = np.argmax(avg_probability, axis=1)
        # print(predict_classes)

        print("=== Confusion Matrix for the test set ===")
        print(confusion_matrix(y_test, predict_classes))
        print('\n')
        print("=== Classification Report for the test set ===")
        print(classification_report(y_test, predict_classes))
        print(precision_recall_fscore_support(
            y_test, predict_classes, average='macro', labels=[0, 1]))


testing = Neural_Network_training()
X_train, X_test, y_train, y_test, X_val, y_val = testing.split_dataset()
model_nn, model_xgb, model_rf = testing.training(
    X_train,  y_train, X_val, y_val,  ['NN', 'rf', 'xgb'])
#model = testing.load_model('/home/pegah/collaborative-nids-chengbozhou-code/model5.h5')
testing.test_set(['NN', 'rf', 'xgb'], model_nn,
                 model_rf, model_xgb, X_test, y_test)
