import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from imblearn.over_sampling import SMOTE
import pickle

from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import json

print("Libraries loaded")

# Read the data from the json file
df = pd.read_json ('mysql_data.json')
print("Data loaded")

# Convert to datetime object YT_publishTime
df['categories'] = df['categories'].astype('category')
df["categories_cat"] = df["categories"].cat.codes

df['publishing_day'] = df['publishing_day'].astype('category')
df["publishing_day_cat"] = df["publishing_day"].cat.codes

df = df.select_dtypes(exclude=['object', 'category'])
df= df.dropna()
print("All features converted into numeric")

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
filename = 's_model.pkl'
pickle.dump(model, open(filename, 'wb'))
print('model saved!')

#save the model to gcp bucket

#load your gcp bucket credential in json
with open('') as f:
    credentials_dict = json.load(f)

# Setting credentials using the downloaded JSON file
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict
)
client = storage.Client(credentials=credentials, project='bdt2021')

# Creating bucket object
bucket = client.get_bucket('bdt2021-315814.appspot.com')

# Name of the object to be stored in the bucket
blob = bucket.blob('s_model.pkl')

# Name of the object in local file system
blob.upload_from_filename('s_model.pkl')

print('uploaded')


