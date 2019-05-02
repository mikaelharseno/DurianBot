import pandas as pd
import pickle, os
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression

url = ""
names = ['preg', 'plas', 'pres', 'skin', 'test', 'mass', 'pedi', 'age', 'class']
basePath = os.path.dirname(os.path.abspath(__file__))
path = basePath + '/results.txt'
df = pd.read_csv(path, sep=" ", header=None)
df.columns = ['worstcaseprob', 'scout_report', 'actualvalue']

data = df.values
# print(data)
test_size = 0.3
X, Y = data[:, :1], data[:, 2]
X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=test_size)

# Fit the model on 33%
model = LogisticRegression()
model.fit(X_train, Y_train)

# save the model to disk
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

# some time later...

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, Y_test)
print(result)
