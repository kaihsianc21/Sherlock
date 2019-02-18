import glob
import numpy as np

from PIL import Image
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input


def load_images(path):
    imgs = []
    img_names = []
    for img_path in glob.glob("{}/*.*".format(path)):
        img = image.load_img(img_path, target_size=(299, 299))  # load image by Karas
        img = img_preprocess(img)  
        imgs.append(img)
        img_name = get_img_name(img_path)
        # img_names.append(img_name)

    # stack images
    batch_images = np.vstack(imgs)
    return batch_images


def get_img_name(path):
    image_name = path.split('/')[-1]
    return image_name

def img_preprocess(img):
    # preprocess image by Karas
    x = np.expand_dims(image.img_to_array(img), axis=0)
    x = preprocess_input(x)
    x = x.copy(order="C")
    return x

    