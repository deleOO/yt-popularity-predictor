import sys
from urllib.request import urlopen
try:
    import tensorflow.compat.v1 as tf

    tf.disable_v2_behavior()
except ImportError:
    import tensorflow as tf
import glob
import pickle

import csv
import pandas as pd

subset = "val"
# Specify your path
dirloc = ""
# For privacy reasons the video IDs in the YT8M dataset
# were provided with a codification.
# Instructions here: https://research.google.com/youtube8m/video_id_conversion.html

def get_real_id(random_id: str) -> str:
    url = 'http://data.yt8m.org/2/j/i/{}/{}.js'.format(random_id[0:2], random_id)
    request = urlopen(url).read()
    real_id = request.decode()
    return real_id[real_id.find(',') + 2:real_id.find(')') - 1]

# The path to the TensorFlow record
video_lvl_record = {}
for file in glob.iglob(f'{dirloc}/*.tfrecord'):
     video_lvl_record[file] = file

vid_ids = []
labels = []
pseudo_ids = []
num_videos_in_record = 0
# Iterate the TensorFlow Records to extract video_ids and info
for video_level_data in video_lvl_record:
    print('processing ', video_level_data)

    num_videos_in_part = 0
    for example in tf.python_io.tf_record_iterator(video_level_data):
        num_videos_in_record += 1
        num_videos_in_part += 1
        tf_example = tf.train.Example.FromString(example)

        # get video id and labels from example
        pseudo_ids.append(tf_example.features.feature['id'].bytes_list.value[0].decode(encoding='UTF-8'))
        labels.append(tf_example.features.feature['labels'].int64_list.value)

        try:
            for e in pseudo_ids:
                vid_ids.append(get_real_id(e))
        except:
            e = sys.exc_info()

print("****************************")
print('TensorFlow records processed')

csv_reader = csv.reader(open("vocabulary.csv", "r"))
headers = next(csv_reader, None)
rows = {key: [] for key in headers}
for row in csv_reader:
    for ii, item in enumerate(row):
        rows[headers[ii]].append(item)
df = pd.DataFrame(rows, columns = ['Name'])
df = df.rename(columns = {'Name':'vocabulary'})
vocabulary = df.to_dict()

# print ("Original key list is : " + str(vid_ids))
# print ("Original value list is : " + str(labels))

dataset = dict(zip(vid_ids, labels))
dataset = {"videos": dataset, "vocabulary": vocabulary}

#print("This is a list of the all the labels:", dataset['vocabulary'])
#print("This is a list of the all the videos:", dataset['videos'])
print(dataset.items())

# # Convert object to a list
dataset = list(dataset)
pickle.dump(dataset, open("parsed_%s.pkl" % subset, "wb"))
print("*****************")
print("done")