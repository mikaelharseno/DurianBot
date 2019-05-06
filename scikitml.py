import pandas as pd
import pickle, os
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPRegressor

url = ""
names = ['preg', 'plas', 'pres', 'skin', 'test', 'mass', 'pedi', 'age', 'class']
basePath = os.path.dirname(os.path.abspath(__file__))
path = basePath + '/results.txt'
df = pd.read_csv(path, sep=" ", header=None)
df.columns = ['worstcaseprob', 'scout_report', 'actualvalue']

# print(data)
test_size = 0.2
X, Y = df.iloc[:, :2], df.iloc[:, 2]
X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=test_size)
#print(X_train)
#print("  ")
#print(Y_train)

# Fit the model on 33%
# model = LogisticRegression()
# model = SVC(C=1.0, kernel='poly', degree=3, gamma='auto', coef0=0.0,
#         shrinking=True, probability=False, tol=0.001, cache_size=200, class_weight=None,
#         verbose=False, max_iter=-1, decision_function_shape='ovr', random_state=None)
#model = SVC(kernel='poly', degree=2)
model = MLPRegressor(solver='adam', alpha=1e-5,\
                     hidden_layer_sizes=(10, 10), early_stopping = True)

model.fit(X, y)
print("Model Created. Starting training. ")
model.fit(X_train, Y_train)
print("Finished training. ")

print(list(model.predict(X_test)))

model.score(X_test, Y_test)

# save the model to disk
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

# some time later...

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, Y_test)
print(result)
