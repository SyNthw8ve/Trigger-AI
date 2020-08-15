
class Link:

    def __init__(self, v, u):

        self.age = 0
        self.v = v
        self.u = u

    def fade(self):

        self.age += 1

    def renew(self):

        self.age = 0