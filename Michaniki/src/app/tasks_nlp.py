# coding=utf-8
from __future__ import absolute_import

from .celeryapp import michaniki_celery_app

import os
import time
import shutil
import logging


from app import app

from .apis.SentimentV1 import API_helpers_nlp
from .models.SentimentV1 import sentimentV1_transfer_retraining

CLIENT_SLEEP = app.config['CLIENT_SLEEP']
INV3_TRANSFER_NB_EPOCH = app.config['INV3_TRANSFER_NB_EPOCH']
INV3_TRANSFER_BATCH_SIZE = app.config['INV3_TRANSFER_BATCH_SIZE']
INCEPTIONV3_IMAGE_QUEUE = app.config['INCEPTIONV3_IMAGE_QUEUE']
INCEPTIONV3_TOPLESS_MODEL_PATH = app.config['INCEPTIONV3_TOPLESS_MODEL_PATH']

SENTIMENT_TEXT_QUEUE = app.config['SENTIMENT_TEXT_QUEUE']

TEMP_FOLDER = os.path.join('./tmp')

@michaniki_celery_app.task()
def async_train_bert(model_name,
                local_data_path,
                s3_bucket_name,
                nb_epoch,
                batch_size,
                id):
    """
    train a model using BERT pre-trained model
    """
    text_data_path = API_helpers_nlp.download_a_dir_from_s3(s3_bucket_name,
                                                        local_path = TEMP_FOLDER)

    logging.info('*Text Data Path:%s',text_data_path)
    try:
        bert_transfer = sentimentV1_transfer_retraining.BertTransferLeaner(model_name)
        new_model_eval_res = bert_transfer.traineval_model(text_data_path,nb_epoch,batch_size)
        logging.info("****Training and eval done, back in async task")
        print(new_model_eval_res)
        return str(new_model_eval_res['eval_accuracy']),str(new_model_eval_res['global_step'])
    except Exception as err:
        logging.info(err)
        #shutil.rmtree(text_data_path, ignore_errors=True)
        raise

@michaniki_celery_app.task()
def async_test_bert(model_name,
                local_data_path,
                s3_bucket_name,
                nb_epoch,
                batch_size,
                id):
    """
    train a model using BERT pre-trained model
    """
    text_data_path = API_helpers_nlp.download_test_file_from_s3(s3_bucket_name,
                                                     local_path = TEMP_FOLDER)

    logging.info('*Text Data Path:%s',text_data_path)
    try:
        bert_transfer = sentimentV1_transfer_retraining.BertTransferLeaner(model_name)
        new_model_eval_res = bert_transfer.test_model(text_data_path,nb_epoch,batch_size,s3_bucket_name)
        logging.info("****Test done, file saved in S3")
        print(new_model_eval_res)
        return str(1),str(1)
    except Exception as err:
        logging.info(err)
        #shutil.rmtree(text_data_path, ignore_errors=True)
        raise
