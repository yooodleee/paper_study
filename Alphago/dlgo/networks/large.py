from keras import layers    # Dens, Activation, Flatten(core)
from keras import layers    # Conv2D, ZeroPadding2D(convolutional)


def layer(input_shape):
    return [
        layers.ZeroPadding2D((3, 3), input_shape=input_shape, data_format='channels_first'),
        layers.Conv2D(64, (7, 7), padding='valid', data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(64, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(64, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(48, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(48, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(32, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.ZeroPadding2D((2, 2), data_format='channels_first'),
        layers.Conv2D(32, (5, 5), data_format='channels_first'),
        layers.Activation('relu'),

        layers.Flatten(),
        layers.Dense(1024),
        layers.Activation('relu'),
    ]