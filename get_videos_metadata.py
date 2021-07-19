import threading
import time
import json
import pickle
import random
import youtube_dl
from apiclient.discovery import build
import pandas as pd
from itertools import zip_longest


#load youtube8M validation dataset
subset = "val"
dataset = pickle.load(open("parsed_%s.pkl" % subset, "rb"))


#define a function that get video_id's metadata

def get_metadata(video_id: str) -> str or None:
    url = 'https://www.youtube.com/watch?v=' + video_id
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    try:
        with ydl:
            result = ydl.extract_info(url, download=False)
            return result
    except youtube_dl.utils.DownloadError:
        return None

#define a function that append in a list every video_id's metadata and store it in a json file every 20k download (backup)

def append_metadata(key):
    j = -1
    data_video.append(get_metadata(key))
    print('Download numero:', len(data_video))

    if len(data_video) % 20000 == 0:
        for i in range(len(data_video)):
            if data_video[i] != None:
                j += 1
                val.append({ 
                    'id' : j,
                    'video_id': data_video[i].get("id", None),
                    'title': data_video[i].get("title", None),
                    'description': data_video[i].get("description", None),
                    'channel_id': data_video[i].get("channel_id", None),
                    'channel_name': data_video[i].get("channel", None),
                    'duration': data_video[i].get("duration", None),
                    'viewCount': data_video[i].get("view_count", None),
                    'likeCount': data_video[i].get("like_count", None),
                    'dislikeCount': data_video[i].get("dislike_count", None),
                    'averageRating' : data_video[i].get("average_rating", None),
                    'categories': data_video[i].get("categories", None),
                    'uploadDate': data_video[i].get("upload_date", None)
                })
    
        # Store data backup
        with open('videos_metadata_backup.json', 'w') as json_file:
            json.dump(val, json_file)
        print('Salvataggio completato')

#extract every video_id from dataset

key_id = []

for x in (dataset['videos']):
    key_id.append(x)


data_video = []
val = []

#total download time calculation            
start = time.perf_counter()

threads = []

#download video's metadata with previous functions

#change range if you want to try to download only a part of metadata's dataset

# for i in range(len(key_id)):
for i in range(50):
    #single download time calculation 
    start_time = time.time()
    #threading module permits us to separate flow of execution. This means that program will have two things happening at once optimizing the cycle execution time
    t = threading.Thread(target=append_metadata, args=[key_id[i]])
    t.start()
    threads.append(t)

    #print download time   
    print("--- %s seconds ---" % (time.time() - start_time))
    
#Getting multiple tasks running simultaneously with threading module
for thread in threads:
    thread.join()   

finish = time.perf_counter()

#print total download time calculation
print(f'Finished in {round(finish-start, 2)} second(s)')

#extract only interesting features and store them in a list

val = []

j = -1

for i in range(len(data_video)):
    
    if data_video[i] != None:
        
        j += 1
        val.append({
            'id' : j,
            'video_id': data_video[i].get("id", None),
            'title': data_video[i].get("title", None),
            'description': data_video[i].get("description", None),
            'channel_id': data_video[i].get("channel_id", None),
            'channel_name': data_video[i].get("channel", None),
            'duration': data_video[i].get("duration", None),
            'viewCount': data_video[i].get("view_count", None),
            'likeCount': data_video[i].get("like_count", None),
            'dislikeCount': data_video[i].get("dislike_count", None),
            'averageRating' : data_video[i].get("average_rating", None),
            'categories': data_video[i].get("categories", None),
            'uploadDate': data_video[i].get("upload_date", None)
    })
    
#save video's metadata in json file called videos_metadata.json

with open('videos_metadata.json', 'w') as json_file:
    json.dump(val, json_file)

print('videos_metadata.json without comments data saved')


#we used the youtube_dl package to download the metadata but unfortunately we can't get the comments data
#for this reason we connect directly to the youtube api to retrieve this information and add it to the various videos of the json just saved

#we open the json with the metadata of the videos just downloaded
#load video_metadata
with open('videos_metadata.json') as f:
    data = json.load(f)

# use my personal api_key
api_key = 'AIzaSyCkM_kqJD-H0tv_Ao_k4_I-mgjaaF9gkxE'

#connect my key to youtube api v3
youtube = build ('youtube', 'v3', developerKey= api_key)

#define a function that gets the video statistics including the number of comments
def get_videos_stats(video_ids):
    stats = []
    comment = []
    for i in range(0, len(video_ids), 50):
        start_time = time.time()
        res = youtube.videos().list(id=','.join(video_ids[i:i+50]), part='statistics').execute()
        
        stats += res['items']
        
    return stats


video_ids = []

#extract every video_id from videos_metadata.json
for i in range(len(data)):
    video_ids.append(data[i]['video_id'])

#download video's stats
stats = get_videos_stats(video_ids)

#we extract only the video id and the number of comments and create a list of dictionaries with this information
comments = []

for i in range(len(stats)):
    if 'commentCount' in stats[i]['statistics']:
        comments.append({'video_id': stats[i]['id'],
                     'commentCount': stats[i]['statistics']['commentCount']})

    else:
        comments.append({'video_id': stats[i]['id'],
                     'commentCount': 0})

# we finally do the data merge between videos_metadata.json and dfComments in order to finally have the dataset with the complete metadata

# In python 3.5 or higher, you can merge dictionaries in a single statement with itertools library using zip_longest function

data_merge = [{**u, **v} for u, v in zip_longest(data, comments, fillvalue={})]

#we save the result and overwrite it in videos_metadata.json
with open('videos_metadata.json', 'w') as json_file:
    json.dump(data_merge, json_file)

print('We finally have all the video metadata of the youtube8m dataset val!')
print('Save the result and overwrite it in videos_metadata.json')