import json
import time

#import a library that provides an easy way to use YouTube Data API V3.
from pyyoutube import Api

# use my personal api_key
api = Api(api_key= "AIzaSyCXA77OXGfC8_JRTcRExnSBOBDhHEORiAI")

#load video_metadata
with open('videos_metadata.json') as f:
    data = json.load(f)

# create a list with all channel_ids from every video of the dataset    
channel_ids = []
for i in range(len(data)):
    channel_ids.append(data[i]['channel_id'])

#total download time calculation
start = time.perf_counter()

#call youtube api with pyyoutube and download data for every channels

stats = []
j = -1

for i in range(0, len(channel_ids), 50):
    start_time = time.time()
    channel_by_ids = api.get_channel_info(channel_id= ','.join(channel_ids[i:i+50]))
    for metadata in channel_by_ids.items:
        if metadata.to_dict()['id'] in channel_ids:
            j += 1
            stats.append({
                'id' : j,
                'channel_id' :   metadata.to_dict()['id'],
                'pubblishedAt' : metadata.to_dict()['snippet']['publishedAt'],
                'title' :        metadata.to_dict()['snippet']['title'],
                'statistics' :   metadata.to_dict()['statistics']
            })
    #print download time 50 channel's metadata  
    print("--- %s seconds ---" % (time.time() - start_time))

finish = time.perf_counter()

#print total download time calculation
print(f'Finished in {round(finish-start, 2)} second(s)')

#save everything in a json file called channel_metadata            

with open('channel_metadata.json', 'w') as json_file:
            json.dump(stats, json_file)

print('--- Everything saved ---')