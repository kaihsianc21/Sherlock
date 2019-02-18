'''
Created on Jun 11, 2018

@author: runshengsong
'''
import os
import json
import numpy as np

# Keras
import keras
from keras.models import load_model
from keras.preprocessing import image
from keras.applications import imagenet_utils


class inceptionV3Infernecer:
    def __init__(self):
        # pre-load some models here on start
        self.loaded_models = {}
        self.loaded_labels = {}

    def load_model(self, model_path, model_name):
        status = None
        try:
            if model_name not in self.loaded_models.keys():
                self.loaded_models[model_name] = load_model(model_path)
            status = True
        except Exception as e:
            print('[Inference Server] Model Loading Error: {}'.format(e))
        return status
    
    def load_label(self, label_path, model_name):
        status = None
        try:
            if model_name not in self.loaded_labels:
                with open(label_path, 'r') as fp:
                    labels = json.load(fp)
                self.loaded_labels[model_name] = {int(k): str(v) for k, v in labels.items()}
            status = True
        except Exception as e:
            print('[Inference Server] Label Loading Error: {}'.format(e))
        return status
    

    def predict_images(self, model_name, batch_images, num_return=3):
        model = self.loaded_models[model_name]
        label = self.loaded_labels[model_name]

        # start predicting
        batch_preds = model.predict(batch_images)

        # Decode prediction to get the class label
        results = self.__decode_pred_to_label(batch_preds, label, num_return)

        return results
        
    def __decode_pred_to_label(self, batch_preds, labels, num_return):
        batch_result = []

        num_label = len(labels)
        # sort the prob from high to low
        for pred in batch_preds:
            result = []
            # get the index base on the prob from high to low
            classes = np.argsort(pred)[::-1]
            probs = np.sort(pred)[::-1]
            
            # trim the list
            if num_return < num_label:
                classes = classes[:num_return]
                probs = probs[:num_return]

            # map classes number to label
            class_labels = [labels.get(x) for x in classes]

            for i in range(len(class_labels)):
                result.append({
                    'label': class_labels[i],
                    'prob': float(probs[i])
                })
            
            # append the results of this image back to batch results
            batch_result.append(result)
        
        return batch_result

if __name__ == "__main__":
    this_server = inceptionV3Infernecer

    
            