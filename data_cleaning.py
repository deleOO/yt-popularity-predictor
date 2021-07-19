import json
import pickle

subset = "val"
dataset = pickle.load(open("parsed_%s.pkl" % subset, "rb"))

key_id = []
value = []

for x in dataset['videos']:
    key_id.append(x)
    value.append(dataset['videos'].get(x))

with open('videos_metadata.json') as f:
    data = json.load(f)

video_id = []

for i in range(len(data)):
    video_id.append(data[i]['video_id'])

# dict update with labels from yt8m

for x, i in zip(video_id, range(len(data))):
    data[i].update({'labels': dataset['videos'].get(x)})

#convert uploadDate from string to datetime
    
for i in range(len(data)):
    data[i]['uploadDate'] = data[i]['uploadDate'][:4] + '-' + data[i]['uploadDate'][4:6] + '-' + data[i]['uploadDate'][6:]
    # data[i]['uploadDate'] = datetime.strptime(data[i]['uploadDate'], '%Y-%m-%d')
    
with open('videos_metadata.json', 'w') as json_file:
    json.dump(data, json_file)

print('videos_metadata.json updated')

with open('channel_metadata.json') as f:
    data = json.load(f)

for i in range(len(data)):
    # clean upload date time
    if data[i]['pubblishedAt'] != None:
        data[i]['pubblishedAt'] = data[i]['pubblishedAt'][:10]
    else:
        data[i]['pubblishedAt'] = None
    if 'viewCount' in data[i]['statistics']:
        data[i]['statistics']['viewCount'] = float(data[i]['statistics']['viewCount'])
    else:
        data[i]['statistics']['viewCount'] = 0
    if 'videoCount' in data[i]['statistics']:
        data[i]['statistics']['videoCount'] = float(data[i]['statistics']['videoCount'])
    else:
        data[i]['statistics']['videoCount'] = 0

    if data[i]['statistics']['subscriberCount'] != None:
        data[i]['statistics']['subscriberCount'] = float(data[i]['statistics']['subscriberCount'])
    else:
        data[i]['statistics']['subscriberCount'] = 0

with open('channel_metadata.json', 'w') as json_file:
    json.dump(data, json_file)

print('channel_metadata.json updated')