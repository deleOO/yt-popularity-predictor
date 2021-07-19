#aggiungere al dizionario le labels prendendole dal dataset di youtube 8m e matchando gli id

import json
from datetime import datetime 

    
with open('videos_metadata.json') as f:
    data = json.load(f)
    
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
    data[i]['statistics']['viewCount'] = float (data[i]['statistics']['viewCount'])
    data[i]['statistics']['subscriberCount'] = float (data[i]['statistics']['subscriberCount'])
    data[i]['statistics']['videoCount'] = float (data[i]['statistics']['videoCount'])
    data[i]['pubblishedAt'] = data[i]['pubblishedAt'][:10]
#     data[i]['pubblishedAt'] = datetime.strptime(data[i]['pubblishedAt'], '%Y-%m-%d')

with open('channel_metadata.json', 'w') as json_file:
    json.dump(data, json_file)

print('channel_metadata.json updated')