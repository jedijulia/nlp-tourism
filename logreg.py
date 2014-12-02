import math

from nltk import compat

import numpy as np

from scipy import sparse

from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder

class LogReg:
    def __init__(self):
        self.encoder = LabelEncoder()
        self.vectorizer = DictVectorizer(dtype=float, sparse=True)
        self.thetas = None
        self.alpha = 0.1

    def train(self, feature_sets):
        X, y = list(compat.izip(*feature_sets))
        X = self.vectorizer.fit_transform(X)
        y = self.encoder.fit_transform(y)

        if not self.thetas:
            self.thetas = sparse.rand(X.shape[1], 1, 1, 'csr')

        cost = self.compute_cost(X, y)
        print cost

        self.gradient_descent(X, y)

    def sigmoid(self, X):
        z = self.thetas.transpose() * X
        z = z.toarray()
        z = z[0][0]
        sigmoid = 1 / (1 + math.exp(-z))
        return sigmoid

    def compute_cost(self, X, y):
        sum = 0
        X_array = X.toarray()
        mod = .000000000000001
        for i in range(0, X.shape[0]):
            curr_x = X_array[i]
            curr_x = sparse.csr_matrix(curr_x).transpose()
            curr_y = y[i]
            sigmoid = self.sigmoid(curr_x)
            if ((sigmoid > 1 - mod) and (sigmoid < 1 + mod)):
                sigmoid = 1 - mod
            elif sigmoid < mod:
                sigmoid = mod
            result = (curr_y * math.log(sigmoid) + (1 - curr_y) * math.log(1 - sigmoid))
            sum += result
        J = (-1 / X.shape[0]) * sum
        return J

    def gradient_descent(self, X, y):
        print 'X Dimensions: ' + str(X.shape[0]) + ' x ' + str(X.shape[1])
        X_array = X.toarray()
        for k in range(0, 1):
            new_thetas = []
            errors = []
            for i in  range(0, X.shape[0]):
                curr_x = X_array[i]
                curr_x = sparse.csr_matrix(curr_x).transpose()
                curr_y = y[i]
                sigmoid = self.sigmoid(curr_x)
                errors.append(sigmoid - curr_y)     
            errors = np.array(errors)       
            for i in range(0, self.thetas.shape[0]):
                theta = self.thetas[i][0]
                sum = 0
                for j in range(0, len(errors)):
                    result = errors[j] * X_array[j][i]
                    sum += result
                theta = theta.toarray()[0][0] - self.alpha * sum
                new_thetas.append(theta)
            new_thetas = sparse.csr_matrix(np.array(new_thetas)).transpose()
            self.thetas = new_thetas
            print 'COST: ' + str(self.compute_cost(X, y))

    def classify(self, feature_set):
        to_classify = self.vectorizer.transform(feature_set).transpose()
        result = self.sigmoid(to_classify)
        if result >= 0.5:
            return 'tourism'
        else:
            return 'nontourism'

    def classify_many(self, feature_sets):
        classifications = []
        for feature_set in feature_sets:
            classifications.append(self.classify(feature_set))
        return classifications