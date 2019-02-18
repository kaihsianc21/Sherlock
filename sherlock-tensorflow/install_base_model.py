import os
from keras.applications.inception_v3 import InceptionV3

BASE_MODEL_PATH = os.path.join("storage", "models", "base.h5")
TOPLESS_MODEL_PATH = os.path.join("storage", "models", "topless.h5")

# loading base model
if os.path.exists(BASE_MODEL_PATH):
    print("* Starting: Found Base Model.")
else:
    print("* Starting: No Base Model Found. Loading...")
    base_model = InceptionV3(include_top=True, weights='imagenet',input_shape=(299, 299, 3))
    base_model.save(BASE_MODEL_PATH)
    print("* Starting: Base Model Saved!")
    
# loading topless model
if os.path.exists(TOPLESS_MODEL_PATH):
    print("* Starting: Found Topless Model.")
else:
    print("* Starting: No Topless Model Found. Loading...")
    topless_model = InceptionV3(include_top=False, weights='imagenet', input_shape=(299, 299, 3))
    topless_model.save(TOPLESS_MODEL_PATH)
    print("* Starting: Topless Model Saved!")
    