
class Stream:

    def __init__(self, window_size):

        self.instances = []
        self.window_size = window_size

    def add_instance(self, instance):

        self.instances.append(instance)

    def get_window(self):

        pass