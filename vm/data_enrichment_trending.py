from apiclient.discovery import build
import json
import youtube_dl
import mysql.connector
import time
from pyyoutube import Api
from datetime import date

# insert your personal api_key
api_key = ''

#connect my key to youtube api v3
youtube = build ('youtube', 'v3', developerKey= api_key)

#define a function that get trending videos passing a region code Country
def get_pop_videos(country):
    
    videos = []
    next_page_token = None
    
    # to obtain more videos we need to make an API call several times. 
    # this loops manage nextPageToken helping us start directly on the next page of videos instead of starting from the beginning again

    while 1:  
        # Call the videos().list method to get trending videos passing a region code Country
        res = youtube.videos().list(part="snippet,contentDetails,statistics", chart="mostPopular",  
                            maxResults=50,pageToken=next_page_token, regionCode=country).execute()
        
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
        
    
    return videos

#define a function that get statistics of 200 videos for each trending video's country passing a list of country codes
def get_pop_videos_stats(country_codes):
    videos = []
    
    #for each country code we call the get_pop_videos function
    for code in country_codes:
        stats = []
        stats.append(get_pop_videos(code))
        
        # get only the interested features
        for x in stats[0]:
            videos.append({'video_id': x['id'], 'statistics' : x['statistics']})
           
            
    return videos

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

#define a function that get metadata of 200 videos for each trending video's country passing a list of country codes
def get_pop_videos_metadata(country_codes):

    #call get_pop_videos_stats to get video's stats for every video_ids from get_pop_videos(country) function
    stats = get_pop_videos_stats(country_codes)
    #insert your personal api key
    api = Api(api_key= "")

    #for the statistics of each video obtained we call the function get_metadata to get more metadata
    for i in range(len(stats)):
        data = get_metadata(stats[i]['video_id'])

        # we manage with if statement all cases in which data is missing in the download

        # if the metadata download was successful we add the following key value pairs
        if data != None:
            stats[i]['title'] = data.get("title", None)
            stats[i]['description'] = data.get("description", None)
            stats[i]['uploadDate'] = data.get("upload_date", None)
            stats[i]['channel_name'] =  data.get("channel", None)
            stats[i]['channel_id'] = data.get("channel_id", None)
            stats[i]['duration'] = data.get("duration", None)
            stats[i]['categories'] = data.get("categories", None)
            stats[i]['statistics']['averageRating'] = float (data.get("average_rating", None))

        # otherwise we add the features with null value
        else:
            stats[i]['title'] = None
            stats[i]['description'] = None
            stats[i]['uploadDate'] = None
            stats[i]['channel_name'] = None
            stats[i]['channel_id'] = None
            stats[i]['duration'] = None
            stats[i]['categories'] = None
            stats[i]['statistics']['averageRating'] = None

        #if the channel id is present among the metadata, we download the channel statistics
        if stats[i]['channel_id'] != None:
            channel = api.get_channel_info(channel_id= data.get("channel_id", None))
            channel_metadata = channel.items[0].to_dict()
            stats[i]['chn_PublishedAt'] = channel_metadata['snippet']['publishedAt']
            stats[i]['chn_viewCount'] = channel_metadata['statistics']['viewCount']
            stats[i]['chn_subscriberCount'] = channel_metadata['statistics']['subscriberCount']
            stats[i]['chn_videoCount'] = channel_metadata['statistics']['videoCount']
                
        #otherwise we add the channel statistics with null values
        else:
            stats[i]['chn_PublishedAt'] = None
            stats[i]['chn_viewCount'] = None
            stats[i]['chn_subscriberCount'] = None
            stats[i]['chn_videoCount'] = None
        
    return stats


# we selected 6 countries. We'll get 200 trending video's metadata for every country

country_codes = ['US', 'IN', 'DE','RU', 'JP', 'BR']


#In order to run, the script needs country codes for the countries to collect trending videos from. 
#These are 2 letter country abbreviations according to ISO 3166-1. A list of all existing ones can be found [here](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes)
#however not all of these are assured to work with the YouTube API. For this reason we have decided to use countries where we have tested the operation

#Trending YouTube videos for whatever country you are in currently can be found [here](https://www.youtube.com/feed/trending).

data_video = get_pop_videos_metadata(country_codes)

#function that delete potential duplicates 
def keep_first(iterable, key=None):
    if key is None:
        key = lambda x: x

    seen = set()
    for elem in iterable:
        k = key(elem)
        if k in seen:
            continue

        yield elem
        seen.add(k)

#delete potential duplicates
data_video = list(keep_first(data_video, lambda d: (d['video_id'], d['title'])))

#data cleaning
for i in range(len(data_video)):
    
    if data_video[i]['chn_PublishedAt'] != None:
        data_video[i]['chn_PublishedAt'] = data_video[i]['chn_PublishedAt'][:10]

    if 'commentCount' in data_video[i]['statistics']:
        data_video[i]['statistics']['commentCount'] = int(data_video[i]['statistics']['commentCount'])
    
    else:
        data_video[i]['statistics']['commentCount'] = 0

    if 'likeCount' in data_video[i]['statistics']:
        data_video[i]['statistics']['likeCount'] = float(data_video[i]['statistics']['likeCount'])
    
    else:
        data_video[i]['statistics']['likeCount'] = 0

    if 'viewCount' in data_video[i]['statistics']:
        data_video[i]['statistics']['viewCount'] = float(data_video[i]['statistics']['viewCount'])
    
    else:
        data_video[i]['statistics']['viewCount'] = 0

    if 'dislikeCount' in data_video[i]['statistics']:
        data_video[i]['statistics']['dislikeCount'] = float(data_video[i]['statistics']['dislikeCount'])
    
    else:
        data_video[i]['statistics']['dislikeCount'] = 0


#insert your credential to connect to mysql istance   
mydb = mysql.connector.connect(
  user="",
  host="",
  password="",
  database=""
)

mycursor = mydb.cursor()


# #insert data video in video table

mycursor.execute("SELECT * from videos")
query = mycursor.fetchall()

j = len(query)

val = []

for i in range(len(data_video)):
    j += 1
            
    val.append ((j, data_video[i]["video_id"], json.dumps(data_video[i]["categories"]), data_video[i]["channel_id"],
                    data_video[i]["title"], data_video[i]["description"], date.today()
                    ))
    
sql = "INSERT INTO videos(id, video_id, categories, channel_id, title_vid, description, downloadDate_vid) VALUES (%s, %s, %s, %s, %s, %s,  %s)"


mycursor.executemany(sql, val)

mydb.commit()

print(mycursor.rowcount, "rows were inserted in videos table.")



# insert channels metadata in stats_channels table

mycursor.execute("SELECT * from stats_videos")
query = mycursor.fetchall()

j = len(query)

val = []

for i in range(len(data_video)):
    j += 1
    
    val.append ((j, data_video[i]["video_id"], data_video[i]['statistics']["averageRating"], data_video[i]['statistics']["viewCount"],
                data_video[i]['statistics']["likeCount"], data_video[i]['statistics']["dislikeCount"], data_video[i]['statistics']['commentCount'],
                data_video[i]["uploadDate"], data_video[i]["duration"] ))
    
    
sql = "INSERT INTO youtube_videos.stats_videos(id_vid, video_id, averageRating, viewCount_vid, likeCount, dislikeCount, commentCount, uploadDate, duration ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"


mycursor.executemany(sql, val)

mydb.commit()

print(mycursor.rowcount, "rows were inserted in stats_video table.")


    
# insert channels data in channels table

mycursor.execute("SELECT * from channels")
query = mycursor.fetchall()

j = len(query)

val = []

for i in range(len(data_video)):
    j += 1
    
    val.append ((j, data_video[i]['channel_id'], data_video[i]['channel_name'], date.today())) 
    
sql = "INSERT INTO youtube_videos.channels(id, channel_id, channel_name, downloadDate_chn) VALUES (%s, %s, %s, %s)"


mycursor.executemany(sql, val)

mydb.commit()

print(mycursor.rowcount, "rows were inserted in channels table.")


# insert channels metadata in stats_channels table

mycursor.execute("SELECT * from stats_channels")
query = mycursor.fetchall()

j = len(query)

val = []

for i in range(len(data_video)):
    j += 1
    
    val.append ((j, data_video[i]['channel_id'], data_video[i]['chn_videoCount'], data_video[i]['chn_viewCount'],
                data_video[i]['chn_subscriberCount'], data_video[i]['chn_PublishedAt'])) 
    
sql = "INSERT INTO youtube_videos.stats_channels(id_chn, channel_id, videoCount, viewCount_chn, subscriberCount, pubblishedAt) VALUES (%s, %s, %s, %s, %s, %s)"


mycursor.executemany(sql, val)

mydb.commit()

print(mycursor.rowcount, "rows were inserted in stats_channels table.")