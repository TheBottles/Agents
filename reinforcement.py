import datetime
from sklearn.linear_model import SGDRegressor
import pickle


def load(filename):
    print(filename)
    return pickle.load(open(filename, 'rb'))

class model(SGDRegressor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(self, **kwargs):
        filename = kwargs.get('file') or 'Weights:%s' % (datetime.datetime.now().isoformat())
        pickle.dump(self, open(filename, 'wb'), protocol=2)

    def update(self, train, label, **kwargs):
        """ Trains on a very small set using very small step size
            To be used to learn as you go.
        """
        temp_iter = self.max_iter
        temp_alpha = self.alpha
        self.max_iter = kwargs.get('iter') or 1
        self.alpha = kwargs.get('alpha') or 0.0000000001
        super().fit(train, label, **kwargs)
        self.max_iter = temp_iter
        self.alpha = temp_alpha
        return self
