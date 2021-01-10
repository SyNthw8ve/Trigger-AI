from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, InputLayer

class AutoEncoder(Model):

    def __init__(self):
        super(AutoEncoder, self).__init__()

        self.encoder = Sequential([
            Dense(768, activation='relu'),
            Dense(512, activation='relu')
        ])
        self.decoder = Sequential([
            Dense(768, activation='sigmoid'),
            Dense(1024, activation='sigmoid')
        ])

    def call(self, x):

        x_enc = self.encoder(x)
        x_dec = self.decoder(x_enc)

        return x_dec

