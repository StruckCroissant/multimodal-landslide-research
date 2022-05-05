import time
import numpy as np

class HX711:
    def __init__(self, *args):
        pass

    def get_weight(self, *args):
        time.sleep(0.0125)
        return np.random.uniform(low=0.001, high=500.001)

    def set_reference_unit(self, *args):
        pass

    def reset(self):
        pass

    def tare(self):
        pass