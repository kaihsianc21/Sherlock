import os
from celery import Celery, current_task

from utils import s3_utils, img_utils

import time
import json

from models import inceptionV3

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

IMAGE_DIR = './storage/images'
MODEL_DIR = './storage/models'
LABEL_DIR = './storage/labels'

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

if not os.path.exists(LABEL_DIR):
    os.makedirs(LABEL_DIR)

IV3_inferencer = inceptionV3.infernecer()

@celery.task(name='tasks.label')
def label(action, bucket_name, bucket_prefix, model_name):
    cur_step = 0
    steps = ['Downloading Images', 'Loading Images', 'Loading Model', 'Loading Label', 'Labeling Images']


    # Destination for temporary storing images
    dest_path = os.path.join(IMAGE_DIR, bucket_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)


    # Download the directory from s3 bucket
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    imgs_dir = s3_utils.download_dir(bucket_name=bucket_name, bucket_prefix=bucket_prefix, dest_path=dest_path)
    if imgs_dir is None: raise Exception({'error': 'Image Downloading Error'})   
    cur_step = cur_step + 1
  

    # Load images to memory from local storage
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    batch_images = img_utils.load_images(imgs_dir)
    cur_step = cur_step + 1


    # Load model to inference service
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    model_path = os.path.join(MODEL_DIR, model_name+'.h5')
    status = IV3_inferencer.load_model(model_path, model_name)
    if status is None: raise Exception({'error': 'Model Loading Error'})
    cur_step = cur_step + 1


    # Load label to inference service
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    label_path = os.path.join(LABEL_DIR, model_name+'.json')
    status = IV3_inferencer.load_label(label_path, model_name)
    if status is None: raise Exception({'error': 'Label Loading Error'})
    cur_step = cur_step + 1


    # Labeling images
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    results = IV3_inferencer.predict_images(model_name, batch_images, num_return=3)
    cur_step = cur_step + 1

    return results



@celery.task(name='tasks.transfer')
def transfer(action, bucket_name, bucket_prefix, model_name, epochs=3, batch_size=2):
    cur_step = 0
    steps = ['Downloading Images', 'Training Model', 'Saving Model', 'Saving Label']


    # Destination for temporary storing images
    dest_path = os.path.join(IMAGE_DIR, bucket_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    print('[Transfer]: Destination for temporary storing images: {}'.format(dest_path))
    


    # Download the directory from s3 bucket
    print('[Transfer]: Downloading directory from s3 bucket')
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    imgs_dir = s3_utils.download_dir(bucket_name=bucket_name, bucket_prefix=bucket_prefix, dest_path=dest_path)
    if imgs_dir is None: raise Exception({'error': 'Image Downloading Error'})   
    cur_step = cur_step + 1
    

    # Start Training
    topless_model_path = os.path.join(MODEL_DIR, 'topless.h5')

    train_dir = os.path.join(imgs_dir, 'train')
    val_dir = os.path.join(imgs_dir, 'val')

    new_model_path = os.path.join(MODEL_DIR, model_name+'.h5')
    new_label_path = os.path.join(LABEL_DIR, model_name+'.json')


    # Init the transfer learning manager
    print('[Transfer]: Start Transfer learning: {}'.format(model_name))
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    IV3_transfer = inceptionV3.transferLeaner(model_name, topless_model_path)
    history = IV3_transfer.transfer_model(
            train_dir = train_dir, val_dir = val_dir, 
            epochs = epochs, batch_size = batch_size)
    cur_step = cur_step + 1
    

    # Save the model .h5 file 
    print('[Transfer]: Save model to {}'.format(new_model_path))
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    IV3_transfer.save_model(new_model_path)
    cur_step = cur_step + 1

    # save the label .json file
    print('[Transfer]: Save label to {}'.format(new_label_path))
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    IV3_transfer.save_label(new_label_path)
    cur_step = cur_step + 1

    # Return the train and val acc:
    final_trn_acc = history.history['acc'][-1]
    final_val_acc = history.history['val_acc'][-1]

    result = {
        'train_acc': final_trn_acc, 
        'val_acc': final_val_acc
    }
    print('[Transfer]: Result: {}'.format(result))

    return result



@celery.task(name='tasks.retrain')
def retrain(action, bucket_name, bucket_prefix, model_name, epochs=3, batch_size=2):
    cur_step = 0
    steps = ['Downloading Images', 'Retraining Model', 'Saving Model']
    

    # Destination for temporary storing images
    dest_path = os.path.join(IMAGE_DIR, bucket_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    print('[Retrain]: Destination for temporary storing images: {}'.format(dest_path))
    

    # Download the directory from s3 bucket
    print('[Retrain]: Downloading directory from s3 bucket')
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    imgs_dir = s3_utils.download_dir(bucket_name=bucket_name, bucket_prefix=bucket_prefix, dest_path=dest_path)
    if imgs_dir is None: raise Exception({'error': 'Image Downloading Error'})   
    cur_step = cur_step + 1


    # Start retraining
    model_path = os.path.join(MODEL_DIR, model_name+'.h5')

    train_dir = os.path.join(imgs_dir, 'train')
    val_dir = os.path.join(imgs_dir, 'val')
    
    # Init the transfer learning manager
    print('[Retrain]: Start Transfer learning: {}'.format(model_name))
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    IV3_retrainer = inceptionV3.retrainer(model_name, model_path)
    history = IV3_retrainer.retrain_model(
            train_dir = train_dir, val_dir = val_dir, 
            epochs = epochs, batch_size = batch_size)
    cur_step = cur_step + 1    


    # Save the model .h5 file 
    print('[Retrain]: Save model to {}'.format(model_path))
    current_task.update_state(state=steps[cur_step], meta={'Step': '{}/{}'.format(cur_step+1, len(steps))})
    IV3_retrainer.save_model(model_path)
    cur_step = cur_step + 1


    # Return the train and val acc:
    final_trn_acc = history.history['acc'][-1]
    final_val_acc = history.history['val_acc'][-1]

    result = {
        'train_acc': final_trn_acc, 
        'val_acc': final_val_acc
    }
    print('[Retrain]: Result: {}'.format(result))

    return result



