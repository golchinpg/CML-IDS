#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 16:44:22 2023

@author: pegah
"""

import pandas as pd
import numpy as np
import logging
import time
import datetime
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from keras.models import Sequential
from keras.layers import Input, Dense, Dropout
from keras.layers import Dense
from keras.layers import BatchNormalization
from keras.layers import LeakyReLU, ReLU, ELU
from sklearn.metrics import precision_recall_fscore_support
from keras.callbacks import ReduceLROnPlateau
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
from xgboost import XGBClassifier


class CPIDSBuilder:
    """Build CP-IDS ML models.
    """
    def __init__(self):
        logging_path = '../../logs/cp_ids_ml_training.log'
        logging.basicConfig(
            filename=logging_path, filemode='a', level=logging.INFO)


    def train_nn(self, X_train, y_train, X_val, y_val, checkpoint_path, fig_save_path):
        """Train NN model.

        Parameters
        ----------
        X_train: DataFrame (pandas)
            Training dataset.
        y_train: DataFrame (pandas)
            Label of training dataset.
        X_val: DataFrame (pandas)
            Validation dataset.
        y_val: DataFrame (pandas)
            Label of validation dataset.
        check_point_path: str
            Check point path for NN training.
        fig_save_path: str
            Figure save path for NN training.

        Returns
        -------
        model: 
            Trained model of NN.
        """
        # start timestamp of training
        start_timestamp = time.time()

        lr_scheduler = ReduceLROnPlateau(
            monitor='val_loss', factor=0.1, patience=10, min_lr=0.0000001)
        checkpoint = ModelCheckpoint(
            filepath=checkpoint_path, monitor='val_accuracy', save_best_only=True)
        early_stopping = EarlyStopping(monitor='loss',
                                       min_delta=0,
                                       patience=30,
                                       mode='decrease')
        callbacks = [lr_scheduler, checkpoint, early_stopping]
        # callbacks = [lr_scheduler, checkpoint]
        #reduce_lr = ReduceLROnPlateau(monitor = 'val_loss', factor = 0.2, patience= 5)
        elu_alpha = 0.1

        training_dim = X_train.shape[1]
 
        model = Sequential()
        model.add(Dense(10, activation='relu',
                        kernel_initializer='he_uniform', input_dim=training_dim))
        # model.add(BatchNormalization())
        model.add(Dense(20))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(40))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(50))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(70))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(100))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())

        model.add(Dense(100))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dense(70))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dense(50))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(40))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(20))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(10))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())
        model.add(Dense(5))
        model.add(LeakyReLU(alpha=0.2))  # (alpha=0.2))
        model.add(BatchNormalization())

        model.add(Dense(1, activation='sigmoid'))
        model.summary()

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=[
            'accuracy', 'Precision', 'Recall'])
        # model training
        history = model.fit(X_train, y_train, batch_size=256, epochs=120,
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

        Parameters
        ----------
        X_train: DataFrame (pandas)
            Training dataset.
        y_train: DataFrame (pandas)
            Label of training dataset.
        X_val: DataFrame (pandas)
            Validation dataset.
        y_val: DataFrame (pandas)
            Label of validation dataset.

        Returns
        -------
        model: 
            Trained model of RF.
        """
        # start timestamp of training
        start_timestamp = time.time()

        model = RandomForestClassifier(
            n_estimators=500, min_samples_leaf=5, max_depth=10)
        model.fit(X_train, y_train)
        # logging
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
        """Train XGB model.

        Parameters
        ----------
        X_train: DataFrame (pandas) 
            Training dataset.
        y_train: DataFrame (pandas) 
            Label of training dataset.
        X_val: DataFrame (pandas) 
            Validation dataset.
        y_val: DataFrame (pandas) 
            Label of validation dataset.

        Returns
        -------
        model: 
            Trained model of XGB.
        """
        # start timestamp of training
        start_timestamp = time.time()

        model = XGBClassifier(max_depth=25, tree_method='approx',
                              scale_pos_weight=40)
        model.fit(X_train, y_train)
        # logging
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

        Paramters
        ---------
        X_train: DataFrame (pandas)  
            Training dataset.
        y_train: DataFrame (pandas)  
            Label of training dataset.
        X_val: DataFrame (pandas)  
            Validation dataset.
        y_val: DataFrame (pandas)  
            Label of validation dataset.
        check_point_path: str 
            Check point path for NN training.
        fig_save_path: str 
            Figure save path for NN training.
        save_models: bool, default=False
            Flag of saving models.
        nn_dir: str, default: None
            NN model saving directory
        rf_path: str, default: None
            RF model saving path
        xgb_path: str, default: None
            XGB model saving path

        Returns
        -------
        model_nn: 
            Trained model of NN.
        model_rf: 
            Trained model of RF.
        model_xgb: 
            Trained model of XGB.
        """
        # logging
        start_timestamp = time.time()
        logging.info('Start training all models')
        logging.info(f'{time.asctime(time.localtime(time.time()))}')

        model_nn = self.train_nn(
            X_train, y_train, X_val, y_val, check_point_path, fig_save_path)
        model_rf = self.train_rf(X_train, y_train, X_val, y_val)
        model_xgb = self.train_xgb(X_train, y_train, X_val, y_val)
        # logging
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
                    "Path to save RF model does not exist.")
            if xgb_path:
                model_xgb.save_model(xgb_path)
            else:
                raise FileExistsError(
                    "Path to save XGB model does not exist.")

        return model_nn, model_rf, model_xgb

    def predict(self, X, model_nn, model_rf, model_xgb, model_weights):
        """Predict flow entry.

        Parameters
        ----------
        model_nn: 
            Model of NN classifier.
        model_rf: 
            Model of RF classifier.
        model_xgb: 
            Model of XGB classifier.
        model_weights: list
            Weights for each model.

        Returns
        -------
        predict_classes: array
            Predicted classes for the given datasets.
        """
        y_predict_nn = np.array(
            list(map(lambda x: [1 - x[0], x[0]], model_nn.predict(X))))
        y_predict_rf = model_rf.predict_proba(X)
        y_predict_xgb = model_xgb.predict_proba(X)

        # compute the final predicted label from each trained model
        avg_probability = np.average(np.array(
            [y_predict_rf, y_predict_xgb, y_predict_nn]), axis=0, weights=model_weights)
        predict_classes = np.argmax(avg_probability, axis=1)
        return predict_classes

    def test(self, X_test, y_test, model_nn, model_rf, model_xgb, model_weights):
        """Test the trained models.

        Parameters
        ----------
        X_test: DataFrame (pandas)
            Test dataset.
        X_test: DataFrame (pandas)
            Test labels.
        model_nn: 
            Model of NN classifier.
        model_rf: 
            Model of RF classifier.
        model_xgb: 
            Model of XGB classifier.
        model_weights: list
            Weights for each model.
        """

        y_predict = self.predict(
            X_test, model_nn, model_rf, model_xgb, model_weights)
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
