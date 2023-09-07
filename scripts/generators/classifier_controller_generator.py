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
import threading
import logging
import time
import datetime
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import joblib
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
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


class ClassifierControllerGenerator:
    def __init__(self):
        # set the logging
        logging_path = '../../logs/controller_ml_training_log.log'
        logging.basicConfig(
            filename=logging_path, filemode='a', level=logging.INFO)

    def load_dataset(self, dataset_path):
        self.df = pd.read_csv(dataset_path, sep=',', header=0)
        print('dataframe shape:', self.df.shape)
        print('columns:', self.df.columns)

    def split_dataset(self, dataset_path):
        df = pd.read_csv(dataset_path, sep=',', header=0)
        print('dataframe shape:', df.shape)
        print('columns:', df.columns)
        X_tot, X_test, y_tot, y_test = train_test_split(
            df.iloc[:, :-1], df['Label'], test_size=0.2, random_state=42, stratify=df['Label'])
        X_train, X_val, y_train, y_val = train_test_split(
            df.iloc[:, :-1], df['Label'], test_size=0.1, random_state=42, stratify=df['Label'])
        return (X_train, X_test, y_train, y_test, X_val, y_val)

    def train_nn(self, X_train, y_train, X_val, y_val, checkpoint_path, fig_save_path):
        """Train NN model.
        Args:
            X_train: Training dataset.
            y_train: Label of training dataset.
            X_val: Validation dataset.
            y_val: Label of validation dataset.
            check_point_path: Check point path for NN training.
            fig_save_path: Figure save path for NN training.

        Returns:
            model: Trained model of NN.
        """
        # start timestamp of training
        start_timestamp = time.time()

        lr_scheduler = ReduceLROnPlateau(
            monitor='val_loss', factor=0.2, patience=10, min_lr=0.0000001)
        checkpoint = ModelCheckpoint(
            filepath=checkpoint_path, monitor='val_accuracy', save_best_only=True)
        early_stopping = EarlyStopping(monitor='loss',
                                       min_delta=0,
                                       patience=30,
                                       mode='decrease')
        # callbacks = [lr_scheduler, checkpoint, early_stopping]
        callbacks = [lr_scheduler, checkpoint]
        #reduce_lr = ReduceLROnPlateau(monitor = 'val_loss', factor = 0.2, patience= 5)
        elu_alpha = 0.1

        training_dim = X_train.shape[1]

        model = Sequential()
        model.add(Dense(60, activation='relu',
                        kernel_initializer='he_uniform', input_dim=training_dim))
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

        end_timestamp = time.time()
        logging.info(
            f"NN training takes time: {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")

        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'],
                 label='Validation Accuracy')
        # plt.title('Training / Validation Accuracy Values')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(loc="best")
        plt.show()
        figure_path = fig_save_path + 'training_validation_accuracy_fig.png'
        plt.savefig(figure_path)

        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        # plt.title('Training / Validation Loss Values')
        plt.ylabel('Loss Value')
        plt.xlabel('Epoch')
        plt.legend(loc="best")
        plt.show()
        figure_path = fig_save_path + 'training_validation_loss_fig.png'
        plt.savefig(figure_path)

        return model

    def train_rf(self, X_train, y_train, X_val, y_val):
        """Train RF.

        Args:
            X_train: Training dataset.
            y_train: Label of training dataset.
            X_val: Validation dataset.
            y_val: Label of validation dataset.

        Returns:
            model: Trained model of RF.
        """
        # start timestamp of training
        start_timestamp = time.time()

        model = RandomForestClassifier(n_estimators=500)
        model.fit(X_train, y_train)

        end_timestamp = time.time()
        logging.info(
            f"RF training takes time: {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")

        y_predict = model.predict(X_val)

        print("=== Confusion Matrix for validation set (RF) ===")
        print(confusion_matrix(y_val, y_predict))
        print('\n')
        print("=== Classification Report for validation set (RF) ===")
        print(classification_report(y_val, y_predict))
        print('\n')
        return model

    def train_xgb(self, X_train, y_train, X_val, y_val):
        """Training XGB model.

        Args:
            X_train: Training dataset.
            y_train: Label of training dataset.
            X_val: Validation dataset.
            y_val: Label of validation dataset.

        Returns:
            model: Trained model of XGB.
        """
        # start timestamp of training
        start_timestamp = time.time()

        model = XGBClassifier()
        model.fit(X_train, y_train)

        end_timestamp = time.time()
        logging.info(
            f"XGB training takes time: {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")

        y_predict = model.predict(X_val)

        print("=== Confusion Matrix for validation set (XGB) ===")
        print(confusion_matrix(y_val, y_predict))
        print('\n')
        print("=== Classification Report for validation set (XGB) ===")
        print(classification_report(y_val, y_predict))
        print('\n')
        return model

    def train_all(self, X_train, y_train, X_val, y_val, check_point_path, fig_save_path, save_models=False, nn_dir=None, rf_path=None, xgb_path=None):
        """Train all models.

        Args:
            X_train: Training dataset.
            y_train: Label of training dataset.
            X_val: Validation dataset.
            y_val: Label of validation dataset.
            check_point_path: Check point path for NN training.
            fig_save_path: Figure save path for NN training.
            save_models: {True, Flase}, default=False
                Flag of saving models.
            nn_dir: NN model directory
            rf_path: RF model save path
            xgb_path: XGB model save path

        Returns:
            model_nn: Trained model of NN.
            model_rf: Trained model of RF.
            model_xgb: Trained model of XGB.
        """
        # thread_training_nn = threading.Thread(
        #     target=self.training_nn, args=(X_train, y_train, X_val, y_val, check_point_path, fig_save_path))
        # thread_training_rf = threading.Thread(
        #     target=self.training_rf, args=(X_train, y_train, X_val, y_val))
        # thread_training_xgb = threading.Thread(
        #     target=self.training_xgb, args=(X_train, y_train, X_val, y_val))
        # thread_training_nn.start()
        # thread_training_rf.start()
        # thread_training_xgb.start()

        start_timestamp = time.time()
        logging.info('Start training all models')
        logging.info(f'{time.asctime(time.localtime(time.time()))}')

        model_nn = self.train_nn(
            X_train, y_train, X_val, y_val, check_point_path, fig_save_path)
        model_rf = self.train_rf(X_train, y_train, X_val, y_val)
        model_xgb = self.train_xgb(X_train, y_train, X_val, y_val)

        end_timestamp = time.time()
        logging.info(
            f"All training takes time: {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}\n\n\n")

        # save trained models
        if save_models:
            if nn_dir:
                model_nn.save(nn_dir)
            else:
                raise FileExistsError(
                    "Directory to save NN model does not exist.")

            if rf_path:
                with open(rf_path, "wb") as f:
                    pickle.dump(model_rf, f)
            else:
                raise FileExistsError(
                    "Directory to save RF model does not exist.")

            if xgb_path:
                model_xgb.save_model(xgb_path)
            else:
                raise FileExistsError(
                    "Directory to save XGB model does not exist.")

        return model_nn, model_rf, model_xgb

    def test(self, X_test, y_test, model_nn, model_rf, model_xgb):
        """Run test for the trained models

        Args:
            model_nn: Trained model of NN.
            model_rf: Trained model of RF.
            model_xgb: Trained model of XGB.
            X_test: Test dataset.
            y_test: Label of test dataset.
        """
        # get the prediction probability of each model
        y_predict_nn = np.array(
            list(map(lambda x: [1 - x[0], x[0]], model_nn.predict(X_test))))
        y_predict_rf = model_rf.predict_proba(X_test)
        y_predict_xgb = model_xgb.predict_proba(X_test)

        # compute the final predicted label from each trained model
        y_predict = np.array([y_predict_nn, y_predict_rf, y_predict_xgb]).mean(
            axis=0).argmax(axis=1)

        # confusion matrix
        cm = confusion_matrix(y_test, y_predict)

        print("=== Confusion Matrix for the test set ===")
        print(cm)
        print('\n')
        print("=== Plot confusion matrix ===")
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                      display_labels=["Benign", "Attack"])
        disp.plot()
        print('\n')
        print("=== Classification Report for the test set ===")
        print(classification_report(y_test, y_predict))
        print(precision_recall_fscore_support(
            y_test, y_predict, average='macro', labels=[0, 1]))
