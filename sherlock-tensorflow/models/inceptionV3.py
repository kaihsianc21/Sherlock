#
# * InceptionV3
# * Inference, TransferLearner, Retrainer
#


import os
import glob
import json
import numpy as np

# Keras
import keras
from keras.models import Model, load_model
from keras.optimizers import SGD
from keras.models import load_model
from keras.applications import imagenet_utils
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator



class infernecer:
    def __init__(self):
        # pre-load some models here on start
        self.loaded_models = {}
        self.loaded_labels = {}

    def load_model(self, model_path, model_name):
        """
        :type model_path: str
        :type model_name: str
        :rtype: bool
        """
        status = None
        try:
            if model_name not in self.loaded_models.keys():
                self.loaded_models[model_name] = load_model(model_path)
            status = True
        except Exception as e:
            print('[Inference Server] Model Loading Error: {}'.format(e))
        return status
    
    def load_label(self, label_path, model_name):
        """
        :type label_path: str
        :type label_name: str
        :rtype: bool
        """

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
        """
        :type model_path: str
        :type batch_images: List[]
        :type num_return: int
        :rtype: List[]
        """

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
        


class retrainer:
    def __init__(self, model_name, model_path):
        self.model_name = model_name
        self.this_model = load_model(model_path)
           
    def retrain_model(self, train_dir, val_dir, epochs, batch_size):
        """
        #
        # Retrain the model
        #
        :type train_dir: str
        :type val_dir: List[]
        :type epochs: int
        :type batch_size: int
        :rtype: List[]
        """
        
        # set up parameters
        nb_train_samples = self.__get_nb_files(train_dir)
        nb_classes = len(glob.glob(train_dir + "/*"))
        nb_val_samples = self.__get_nb_files(val_dir)
        epochs = int(epochs)
        batch_size = int(batch_size)
        

        # set up image data
        train_datagen =  ImageDataGenerator(preprocessing_function=preprocess_input)
        val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        
        # generator
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(299, 299),
            batch_size=batch_size)
        
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(299, 299),
            batch_size=batch_size,
            )
        
        # retrain the model
        retrain_history = self.this_model.fit_generator(
            train_generator,
            epochs=epochs,
            steps_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            validation_steps=nb_val_samples//batch_size,
            class_weight='auto',
            verbose=2)

        return retrain_history
        
    def __get_nb_files(self, directory):
        """Get number of files by searching local dir recursively"""
        if not os.path.exists(directory):
            return 0
        cnt = 0
        for r, dirs, files in os.walk(directory):
            for dr in dirs:
                cnt += len(glob.glob(os.path.join(r, dr + "/*")))
        return cnt

    def save_model(self, model_path):
        self.this_model.save(model_path)



class transferLeaner:
    def __init__(self, model_name, topless_model_path):
        self.model_name = model_name
        self.new_model = None
        self.new_label = None 

        # Load topless model from local, otherwise from Keras
        try:
            print("* Transfer: Loading Topless Model...")
            self.topless_model = load_model(topless_model_path)
        except IOError:
            print("* Transfer: Loading Topless Model from Keras...")
            self.topless_model = InceptionV3(include_top=False, weights='imagenet', input_shape=(299, 299, 3))

    def transfer_model(self, train_dir, val_dir, epochs, batch_size, fc_size=1024):
        """
        # 
        # Transfer the topless InceptionV3 model to classify new classes
        #
        :type train_dir: str
        :type val_dir: List[]
        :type epochs: int
        :type batch_size: int
        :type fc_size: int
        :rtype: List[]
        """
        
        # set up parameters
        nb_train_samples = self.__get_nb_files(train_dir)
        nb_classes = len(glob.glob(train_dir + "/*"))
        nb_val_samples = self.__get_nb_files(val_dir)
        epochs = int(epochs)
        batch_size = int(batch_size)
        

        # data prep
        train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)


        # generator
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(299, 299),
            batch_size=batch_size)
        
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(299, 299),
            batch_size=batch_size)

        
        # get the class and label name, reverse key and value pair
        self.new_label = train_generator.class_indices
        self.new_label = {v: k for k, v in self.new_label.items()}
        

        # add a new top layer base on the user data
        self.new_model = self.__add_new_last_layer(self.topless_model, nb_classes, fc_size) 
        

        # set up transfer learning model
        self.__setup_to_transfer_learn(
            model=self.new_model, 
            base_model=self.topless_model)

        
        print("* Transfer: Added a New Last Layer... Starting Transfer Learning...")
        # train the new model for few epoch
        history_tl = self.new_model.fit_generator(
            train_generator,
            epochs=epochs,
            steps_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            validation_steps=nb_val_samples//batch_size,
            class_weight='auto',
            verbose=2)
        

        # set up fine-tuning model
        self.__setup_to_finetune(self.new_model, nb_layer_to_freeze=10)
        

        print("* Transfer: Starting Fine-Tuning...")
        # train the new model again to fine-tune it
        history_ft = self.new_model.fit_generator(
            train_generator,
            epochs=epochs,
            steps_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            validation_steps=nb_val_samples//batch_size,
            class_weight='auto',
            verbose=2)

        return history_ft

    def save_model(self, model_path):
        self.new_model.save(model_path)

    def save_label(self, label_path):
        with open(label_path, 'w') as fp:
            json.dump(self.new_label, fp)
    
    def __setup_to_finetune(self, model, nb_layer_to_freeze):
        """
        Freeze the bottom NB_IV3_LAYERS and retrain the remaining top layers.
        note: NB_IV3_LAYERS corresponds to the top 2 inception blocks in the inceptionv3 arch
        Args:
        model: keras model
        """
        for layer in model.layers[:nb_layer_to_freeze]:
            layer.trainable = False
        for layer in model.layers[nb_layer_to_freeze:]:
            layer.trainable = True
        model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])

    def __setup_to_transfer_learn(self, model, base_model):
        """Freeze all layers and compile the model"""
        for layer in base_model.layers:
            layer.trainable = False
        model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
        
    def __add_new_last_layer(self, topless_model, nb_classes, fc_size):
        """
        add the last layer to the topless model
        """
        x = topless_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(fc_size, activation='relu')(x) #new FC layer, random init
        predictions = Dense(nb_classes, activation='softmax')(x) #new softmax layer
        model = Model(inputs=[topless_model.input], outputs=predictions)
        return model
        
    def __get_nb_files(self, directory):
        """Get number of files by searching local dir recursively"""
        if not os.path.exists(directory):
            return 0
        cnt = 0
        for r, dirs, files in os.walk(directory):
            for dr in dirs:
                cnt += len(glob.glob(os.path.join(r, dr + "/*")))
        return cnt


