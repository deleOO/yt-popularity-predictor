import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import pickle

print("Libraries loaded")

# Read the data from the json file
df = pd.read_json ('processed_data.json')
print("Data loaded")

# Convert only relevant features for long-term prediction
# Discard publishing day
df['categories'] = df['categories'].astype('category')
df["categories_cat"] = df["categories"].cat.codes

df['publishing_day'] = df['publishing_day'].astype('category')
df["publishing_day_cat"] = df["publishing_day"].cat.codes

df = df.select_dtypes(exclude=['object', 'category'])
df= df.dropna()
print("Cat features converted into numeric")

# Define the label to predict
Y = np.array(df['pop'])
# Define what influence the prediction
features = df.drop(labels=['pop','viewCount', 'likeCount', 'dislikeCount', 'commentCount',
                           'viewCount_chn', 'subscriberCount', 'videoCount'], axis=1)
# Convert features into array
X = np.array(features)

# creating test and train dataset
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.4, random_state=20)

# oversample the data by creating synthetic data using the SMOTE technique
smote = SMOTE(random_state=14)
X_train, Y_train = smote.fit_resample(X_train, Y_train)
print('\nlabels balanced. Starting training...')

model = RandomForestClassifier(n_estimators = 100, random_state=42)
# train the model
model.fit(X_train, Y_train)


print("**************************************")
print('Model Training Completed Successfully')
print("\nsaving the model...")

# save the model to disk
filename = 'l_model.pkl'
pickle.dump(model, open(filename, 'wb'))
print('model saved!')

#check the features importance
print('\nRandom Forest Feature Importance Computed:')
feature_list = list(features.columns)
feature_imp = pd.Series(model.feature_importances_, index=feature_list).sort_values(ascending=False)
print(feature_imp)


