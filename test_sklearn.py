from sklearn import preprocessing

import numpy as np
X_train = np.array([[ 89., -1.,  2.],
                    [ 2.,  0.,  0.],
                    [ 0.,  1., -90.]])
min_max_scaler = preprocessing.MinMaxScaler()

X_train_minmax = min_max_scaler.fit_transform(X_train)
print(X_train_minmax[1])
