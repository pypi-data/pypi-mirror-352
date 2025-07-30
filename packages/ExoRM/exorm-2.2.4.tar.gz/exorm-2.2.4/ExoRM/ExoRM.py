import numpy
import os
import pandas
import pickle

from platformdirs import user_data_dir
from scipy.optimize import curve_fit

def get_exorm_filepath(relative_filepath):
    return os.path.join(user_data_dir('ExoRM'), relative_filepath)

def load_model():
    path = get_exorm_filepath('radius_mass_model.pkl')
    model = ExoRM.load(path)

    return model

def read_rm_data():
    path = get_exorm_filepath('exoplanet_rm.csv')
    data = pandas.read_csv(path)

    return data

def read_exoplanet_data():
    path = get_exorm_filepath('exoplanet_data.csv')
    data = pandas.read_csv(path)

    return data

def unique_radius(data):
    counts = []
    for i in range(len(data['radius'])):
        while data.loc[i, 'radius'] in counts:
            data.loc[i, 'radius'] += 1e-12

        counts.append(data.loc[i, 'radius'])

    return data.sort_values('radius').reset_index(drop = True)

def preprocess_data(data):
    data['density'] = data['mass'] / data['radius'] ** 3
    data = data[~(data['density'] >= numpy.percentile(data['density'], 99))].reset_index(drop = True)

    return data

class ForecasterRM:
    log_mode = True

    @classmethod
    def forecaster(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = numpy.zeros_like(x)

        y = numpy.where(x < numpy.log10(1.23), cls.terran(x), y)
        y = numpy.where((x >= numpy.log10(1.23)) & (x < numpy.log10(14.3)), cls.neptunian(x), y)
        y = numpy.where(x >= numpy.log10(14.3), cls.stellar(x), y)

        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def terran(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x - 0.00346) / 0.2790
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def neptunian(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x + 0.0925) / 0.589
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def jovian(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x - 1.25) / -0.044
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def stellar(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x + 2.85) / 0.881
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

class ExoRM:
    def __init__(self, model, x, y):
        self.model = model
        self.model = self.model
        self.x = x
        self.y = y

        self.residuals = self.y - self.model(self.x)
        self.x_min, self.x_max, self.y_min, self.y_max = None, None, None, None

    def create_error_model(self):
        self.variances = (self.residuals ** 2)

        mask = self.x > numpy.percentile(self.x, 99)
        self.params, _ = curve_fit(self.error_model, self.x[~mask], self.variances[~mask], p0 = [1, 1], maxfev = 10000)

    def error_model(self, x, a, b):
        return a * (b ** x)

    def error(self, x):
        return numpy.sqrt(self.error_model(x, *self.params)) * numpy.where((x < min(self.x)) | (x > max(self.x)), 3, 2)

    def linear_error(self, linear_x):
        y = self.error(numpy.log10(linear_x))

        return numpy.power(10, y)

    def override_min(self, x_min, y_min):
        self.x_min = x_min
        self.y_min = y_min

    def override_max(self, x_max, y_max):
        self.x_max = x_max
        self.y_max = y_max

    def __call__(self, x):
        values = self.model(x)
        ForecasterRM.log_mode = True

        if self.x_min is not None:
            values = numpy.where(x < self.x_min, ForecasterRM.terran(x), values)

        if self.x_max is not None:
            values = numpy.where(x > self.x_max, ForecasterRM.stellar(x), values)

        return values

    predict = __call__
    def predict_linear(self, linear_x):
        y = self.__call__(numpy.log10(linear_x))
        return numpy.power(10, y)

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)