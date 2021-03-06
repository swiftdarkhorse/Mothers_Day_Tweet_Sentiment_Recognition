# -*- coding: utf-8 -*-
"""Movie_Rating_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PeKEKWy_-s0kcR2mRijEJ9aEApZXD6uX
"""

import pandas as pd
import numpy as np
import tensorflow as tf

train_data = pd.read_csv(r'C:\Users\admin\Downloads\dataset\train.csv')
test_data = pd.read_csv(r'C:\Users\admin\Downloads\dataset\test.csv')

train_data.head()

test_data.head()

train = np.array(train_data.drop(["id","lang","retweet_count","original_author"], axis = 1))
test = np.array(test_data.drop(["id","lang","retweet_count","original_author"], axis = 1))
#print(train)
#print(test)

train_sentences = []
train_labels = []
test_sentences = []
test_labels = []

for i in range(train.shape[0]):
  train_sentences.append(train[i, 0])
  train_labels.append(train[i, 1])
train_sentences_final = np.array(train_sentences)
train_labels_final = np.array(train_labels)
x = train_labels_final
for i in range(x.shape[0]):
    if (x[i] == -1):
       x[i] = 0
    elif (x[i] == 0):
       x[i] = 1
    else:
       x[i] = 2
train_labels_final = x

for j in range(test.shape[0]):
  test_sentences.append(test[j, 0])
test_sentences_final = np.array(test_sentences)

vocab_size = 10000
embedding_dim = 16
max_length = 120
trunc_type='post'
oov_tok = "<OOV>"


from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(train_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(train_sentences)
padded = pad_sequences(sequences,maxlen=max_length, truncating=trunc_type)

testing_sequences = tokenizer.texts_to_sequences(test_sentences)
testing_padded = pad_sequences(testing_sequences,maxlen=max_length)

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_review(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

print(decode_review(padded[100]))
print(train_sentences[100])

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='tanh'),
    tf.keras.layers.Dense(256, activation='tanh'),
    tf.keras.layers.Dense(128, activation='tanh'),
    tf.keras.layers.Dense(64, activation='tanh'),
    tf.keras.layers.Dense(32, activation='tanh'),
    tf.keras.layers.Dense(16, activation='tanh'),
    tf.keras.layers.Dense(3, activation='softmax')
])
model.compile(loss='sparse_categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()

num_epochs = 10
model.fit(padded, train_labels_final, epochs=num_epochs)
x = np.array(model.predict(testing_padded))
x = np.around(x)

a = np.transpose(np.array([-1,0,1]))
i = 0 
predicted_label = np.zeros((x.shape[0],1))
for i in range(x.shape[0]):
    predicted_label[i] = np.sum(np.dot(a, x[i]))
print(predicted_label)
test_dataset = np.array(test_data.drop(["lang","retweet_count","original_author","original_text"], axis = 1))
test_dataset = np.concatenate((test_dataset,predicted_label), axis=1)
dataset = pd.DataFrame({'id': test_dataset[:, 0], 'sentiment_class': test_dataset[:, 1]})
dataset.to_csv('predictions.csv', index=False, encoding='utf-8')