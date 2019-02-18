import os
import glob

import json

import keras
from keras.models import Model
from keras.optimizers import SGD
from keras.models import load_model
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator


class InceptionRetrainer:
    def __init__(self, model_name, model_path):
        self.model_name = model_name
        self.this_model = load_model(model_path)
        
        
    def retrain_model(self, train_dir, val_dir, nb_epoch, batch_size):
        """
        retrain the model
        """
        
        # set up parameters
        nb_train_samples = self.__get_nb_files(train_dir)
        nb_classes = len(glob.glob(train_dir + "/*"))
        nb_val_samples = self.__get_nb_files(val_dir)
        nb_epoch = int(nb_epoch)
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
            nb_epoch=nb_epoch,
            samples_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            nb_val_samples=nb_val_samples//batch_size,
            class_weight='auto',
            verbose=1)

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


class InceptionTransferLeaner:
    def __init__(self, model_name, topless_model_path):
        self.model_name = model_name
        self.new_model = None
        self.new_label = None 

        # the creation of the model directory should be handled in the API
        # loading topless model from local, otherwise from Keras
        try:
            print("* Transfer: Loading Topless Model...")
            self.topless_model = load_model(topless_model_path)
        except IOError:
            print("* Transfer: Loading Topless Model from Keras...")
            self.topless_model = InceptionV3(include_top=False, weights='imagenet', input_shape=(299, 299, 3))

    def transfer_model(self, train_dir, val_dir, nb_epoch, batch_size, fc_size=1024):
        """
        transfer the topless InceptionV3 model
        to classify new classes
        """
        
        # set up parameters
        nb_train_samples = self.__get_nb_files(train_dir)
        nb_classes = len(glob.glob(train_dir + "/*"))
        nb_val_samples = self.__get_nb_files(val_dir)
        nb_epoch = int(nb_epoch)
        batch_size = int(batch_size)
        

        # data prep
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
            nb_epoch=nb_epoch,
            samples_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            nb_val_samples=nb_val_samples//batch_size,
            class_weight='auto',
            verbose=2)
        

        # set up fine-tuning model
        self.__setup_to_finetune(self.new_model, nb_layer_to_freeze=10)
        

        print("* Transfer: Starting Fine-Tuning...")
        # train the new model again to fine-tune it
        history_ft = self.new_model.fit_generator(
            train_generator,
            nb_epoch=nb_epoch,
            samples_per_epoch=nb_train_samples//batch_size,
            validation_data=validation_generator,
            nb_val_samples=nb_val_samples//batch_size,
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
        model = Model(input=topless_model.input, output=predictions)
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

