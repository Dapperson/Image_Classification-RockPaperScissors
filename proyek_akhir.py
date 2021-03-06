# -*- coding: utf-8 -*-
"""Proyek_Akhir.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/130uN0LHIbIure7aAZPUBvKbEc_sJ4RVv

Nama : Roni Merdiansah

Kelas : Belajar Machine Learnng Untuk Pemula

---

Import Library Yang Dibutuhkan
"""

import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import zipfile,os,shutil

"""

---


Mengunduh Dataset Dengan URL"""

!wget --no-check-certificate \
  https://github.com/dicodingacademy/assets/releases/download/release/rockpaperscissors.zip \
  -O /tmp/rockpaperscissors.zip

"""

---


Mengekstrak Dataset Yang Telah Diunduh"""

local_zip = '/tmp/rockpaperscissors.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/tmp')
zip_ref.close()

"""

---
Split Dataset
"""

#Split data image dilakukan menggunaka nama direktorinya
base_dir = '/tmp/rockpaperscissors'
train_dir = os.path.join(base_dir,'train')
validation_dir = os.path.join(base_dir, 'val')
rock_dir = os.path.join(base_dir,'rock')
paper_dir = os.path.join(base_dir, 'paper')
scissors_dir = os.path.join(base_dir, 'scissors')

train_rock = os.path.join(train_dir, 'rock')
train_paper = os.path.join(train_dir, 'paper')
train_scissors = os.path.join(train_dir, 'scissors')
validation_rock = os.path.join(validation_dir, 'rock')
validation_paper = os.path.join(validation_dir, 'paper')
validation_scissors = os.path.join(validation_dir, 'scissors')

"""

---
Membuat Direktori
"""

#membuat direktori baru menggunakan os.mkdir
os.mkdir(train_dir)
os.mkdir(validation_dir)
os.mkdir(train_rock)
os.mkdir(train_paper)
os.mkdir(train_scissors)
os.mkdir(validation_rock)
os.mkdir(validation_paper)
os.mkdir(validation_scissors)

"""

---


Train & Test Split (OPSI)"""

#memecah setiap direktori menjadi data train dan data validasi(validation 40% of dataset)
train_rock_dir, validation_rock_dir = train_test_split(os.listdir(rock_dir), test_size = 0.40)
train_paper_dir, validation_paper_dir = train_test_split(os.listdir(paper_dir), test_size = 0.40)
train_scissors_dir, validation_scissors_dir = train_test_split(os.listdir(scissors_dir), test_size = 0.40)

for file in train_rock_dir:
  shutil.copy(os.path.join(rock_dir, file), os.path.join(train_rock, file))
for file in train_paper_dir:
  shutil.copy(os.path.join(paper_dir,file), os.path.join(train_paper,file))
for file in train_scissors_dir:
  shutil.copy(os.path.join(scissors_dir,file), os.path.join(train_scissors,file))
for file in validation_rock_dir:
  shutil.copy(os.path.join(rock_dir, file), os.path.join(validation_rock,file))
for file in validation_paper_dir:
  shutil.copy(os.path.join(paper_dir,file), os.path.join(validation_paper,file))
for file in validation_scissors_dir:
  shutil.copy(os.path.join(scissors_dir,file), os.path.join(validation_scissors,file))

"""

---


Augmentation & Generate Image Data"""

train_datagen = ImageDataGenerator(
    rescale = 1./255,
    rotation_range = 20,
    horizontal_flip = True,
    shear_range = 0.2,
    validation_split = 0.4,
    fill_mode = 'nearest',
)
test_datagen = ImageDataGenerator(
    rescale = 1./225,
    rotation_range = 20,
    horizontal_flip = True,
    vertical_flip = True,
    shear_range = 0.2,
    validation_split = 0.4,
    fill_mode = 'nearest'
)

#OPSI menggunakan direktori Split Folder (Hasil Training & Validation TIDAK sesuai ketentuan)
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150,150),
    batch_size= 32,
    class_mode='categorical'
)

validation_generator = test_datagen.flow_from_directory(
    validation_dir,
    target_size = (150,150),
    batch_size = 32,
    class_mode = 'categorical'
)

#OPSI menggunakan direktori 'rps-cv-images' (Hasil Training & Validation sesuai ketentuan)
base_dir2 = '/tmp/rockpaperscissors/rps-cv-images'

train_generator = train_datagen.flow_from_directory(
    base_dir2,
    target_size=(150,150),
    batch_size= 32,
    subset = 'training',
    class_mode='categorical'
)

validation_generator = test_datagen.flow_from_directory(
    base_dir2,
    target_size = (150,150),
    batch_size = 32,
    subset = 'validation',
    class_mode = 'categorical'
)

#Menggunakan model CNN & Layer Max Pooling
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv2D(32, (3,3), activation = 'relu', input_shape= (150,150,3)),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(64,(3,3), activation= 'relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(128,(3,3), activation= 'relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(256,(3,3), activation= 'relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dropout(0.5),
  tf.keras.layers.Dense(512, activation= 'relu'),
  tf.keras.layers.Dense(3, activation= 'softmax')
])

model.summary()
model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.Adam(),
              metrics=['accuracy'])

"""

---


Callback Untuk Menghindari Overfitting"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.95): #artinya berhenti bila nilai lebih dari 95%
      print("\nAkurasi di atas 95%, hentikan training!")
      self.model.stop_training = True

callbacks = myCallback()

history = model.fit(
    train_generator,
    steps_per_epoch = 41, # 1312 images = batch_size(32) * steps(41)
    epochs = 20,
    validation_data = validation_generator,
    validation_steps = 27, # 876 images = batch_size(32) * steps(27)
    verbose =2,
      callbacks=[callbacks]
)

# Commented out IPython magic to ensure Python compatibility.
#main driver
import numpy as np
from google.colab import files
from keras.preprocessing import image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline

uploaded = files.upload()

for fn in uploaded.keys():

  path = fn 
  img = image.load_img(path, target_size =(150,150))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)

  print(fn)
  if classes[0,0]!=0:
    print('paper')
  elif classes[0,1]!=0:
    print('rock')
  else:
    print('scissors')