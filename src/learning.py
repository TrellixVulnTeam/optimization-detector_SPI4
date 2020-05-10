from __future__ import print_function

import os
import time

import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Embedding, LSTM
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
from tensorflow.python import confusion_matrix
from tensorflow_core.python.keras.callbacks import EarlyStopping

from src.binaryds import BinaryDs


def run_train(model_dir: str, seed: int):
    if seed == 0:
        seed = int(time.time())
    assert os.path.exists(model_dir), "Model directory does not exists!"
    train_bin = os.path.join(model_dir, "train.bin")
    validate_bin = os.path.join(model_dir, "validate.bin")
    assert os.path.exists(train_bin), "Train dataset does not exists!"
    assert os.path.exists(validate_bin), "Validation dataset does not exists!"
    train = BinaryDs(train_bin)
    validate = BinaryDs(validate_bin)
    model_path = os.path.join(model_dir, "model.h5")
    if os.path.exists(model_path):
        model = load_model(model_path)
        print("Loading previous model")
    elif train.get_categories() <= 2:
        model = binary_convolutional_LSTM(train.features)
    else:
        model = multiclass_convolutional_LSTM(train.get_categories(),
                                              train.features)
    print(model.summary())
    np.random.seed(seed)
    x_train, y_train = generate_sequences(train)
    x_val, y_val = generate_sequences(validate)
    x_train = sequence.pad_sequences(x_train, maxlen=train.features)
    x_val = sequence.pad_sequences(x_val, maxlen=validate.features)

    checkpoint = ModelCheckpoint(filepath=model_path,
                                 verbose=1,
                                 save_best_only=True)

    tensorboard_logs = os.path.join(model_dir, 'logs')
    os.makedirs(tensorboard_logs, exist_ok=True)
    tensorboad = TensorBoard(log_dir=tensorboard_logs,
                             histogram_freq=1,
                             write_graph=True,
                             write_images=True,
                             update_freq=100,
                             embeddings_freq=1)
    early_stopper = EarlyStopping(monitor="val_loss",
                                  min_delta=0.001,
                                  patience=0,
                                  mode="auto")

    model.fit(x_train, y_train, epochs=10, batch_size=256,
              validation_data=(x_val, y_val),
              callbacks=[tensorboad, checkpoint, early_stopper])


def generate_sequences(data: BinaryDs) -> (np.array, np.array):
    x = []
    y = []  # using lists since I don't know the final size beforehand
    for i in range(0, data.get_categories()):
        samples = data.get(i)
        if samples:
            expected = [0.0] * data.get_categories()
            expected[i] = 1.0
            expected = expected * len(samples)
            y.extend(expected)
            x.extend(samples)
    x = np.array(x)
    y = np.array(y)
    assert len(x) == len(y), "Something went wrong... different X and y len"
    indices = np.arange(x.shape[0])
    np.random.shuffle(indices)
    x = x[indices]
    y = y[indices]
    return x, y


def binary_convolutional_LSTM(pad_length: int):
    embedding_size = 256
    embedding_length = 64
    model = Sequential()
    model.add(Embedding(embedding_size, embedding_length,
                        input_length=pad_length))
    model.add(Conv1D(filters=32, kernel_size=3, padding='same',
                     activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(LSTM(256))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def multiclass_convolutional_LSTM(classes: int, pad_length: int):
    embedding_size = 256
    embedding_length = 64
    model = Sequential()
    model.add(Embedding(embedding_size, embedding_length,
                        input_length=pad_length))
    model.add(Conv1D(filters=32, kernel_size=3, padding='same',
                     activation='relu'))
    model.add(MaxPooling1D(pool_size=2, padding="valid"))
    model.add(LSTM(256))
    model.add(Dense(classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def multiclass_dense_model(classes: int, pad_length: int):
    embedding_size = 256
    embedding_length = 64
    model = Sequential()
    model.add(Embedding(embedding_size, embedding_length,
                        input_length=pad_length))
    model.add(Dense(200, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(100, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(50, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(25, activation="relu"))
    model.add(Dense(classes, activation="softmax"))
    model.compile(loss="categorical_crossentropy",
                  optimizer="adam",
                  metrics=["accuracy"])
    return model


def evaluate_nn(model_path, X_test, y_test, pad_length):
    model = load_model(model_path)
    yhat_classes = model.predict_classes(
        sequence.pad_sequences(X_test, maxlen=pad_length), verbose=1)
    yhat_classes = yhat_classes[:, 0]
    matrix = confusion_matrix(y_test, yhat_classes)
    print(matrix)
    return matrix
