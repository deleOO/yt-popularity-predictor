from apiclient.discovery import build
import json
import youtube_dl
import mysql.connector
import time
from pyyoutube import Api
from datetime import datetime
from datetime import date
from datetime import datetime, timedelta

# use my personal api_key
api_key = 'AIzaSyB2-UdBlLeCWxFdBQYzG_1MADdP3fvrVZs'

#connect my key to youtube api v3
youtube = build ('youtube', 'v3', developerKey= api_key)

# define a function that randomly takes videos uploaded 7 days ago on youtube
def youtube_search(parameter, max_results):
    #to take each time the videos uploaded between 6 days ago and 7 days ago I make the difference between today's date minus 6 and 7 days
    start = date.today() - timedelta(days=7)
    end = date.today() - timedelta(days=6)
    #set the datetime limits with which to make the video request to youtube
    start_time = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = end.strftime('%Y-%m-%dT%H:%M:%SZ')
    # use my personal api_key
    api_key = 'AIzaSyB2-UdBlLeCWxFdBQYzG_1MADdP3fvrVZs'
    #connect my key to youtube api v3
    youtube = build ('youtube', 'v3', developerKey= api_key)

    # Call the search.list method to retrieve results matching the specified parameter term.
    search_response = youtube.search().list(
        part='id,snippet',
        type='video',
        order= parameter,
        publishedAfter=start_time, 
        publishedBefore=end_time,
        maxResults=50
    ).execute()

    nextPageToken = search_response.get('nextPageToken')

    #Each time we submit a request, we get maxResults number of comments in the items list. The maximum number of results we can obtain is limited between 1 and 100.
    #to obtain more than 100 videos we need to make an API call several times. 
    # The nextPageToken helps us start directly on the next page of videos instead of starting from the beginning again. 
    while ('nextPageToken' in search_response):
        nextPage = youtube.search().list(
            part='id,snippet',
            type='video',
            order= parameter,
            publishedAfter=start_time, 
            publishedBefore=end_time,
            maxResults=50,
            pageToken=nextPageToken
        ).execute()
        search_response['items'] = search_response['items'] + nextPage['items']

        #we set the maximum of videos to be taken with the max_results parameter
        if len(search_response.get('items', [])) == max_results:
            break

        if 'nextPageToken' not in nextPage:
            search_response.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']

    video_ids = []

    # we add the video id of each video to a list and return it

    for search_result in search_response.get('items', []):
        video_ids.append(search_result['id']['videoId'])
        
    return video_ids

#define a function that get video stats
def get_videos_stats(video_ids):
    stats = []
    
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(id=','.join(video_ids[i:i+50]),
                                   part='statistics').execute()
        stats += res['items']

    return stats

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



#define a function that get max_results number of videos uploaded 7 days before today's date that have 1 week of life's cycle
def get_last_videos(parameter, max_results):

    #call youtube_search function that randomly takes videos uploaded 7 days ago on youtube
    video_ids = youtube_search(parameter, max_results)

    #call get_videos_stats to get video's stats for every video_ids
    stats = get_videos_stats(video_ids)

    api = Api(api_key= "AIzaSyB2-UdBlLeCWxFdBQYzG_1MADdP3fvrVZs")

    #for the statistics of each video obtained we call the function get_metadata to get more metadata
    for i in range(len(stats)):
        data = get_metadata(stats[i]['id'])

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

# order_parameter = ['searchSortUnspecified', 'date', 'rating', 'viewCount', 'relevance', 'title', 'videoCount']

#call get_last videos function with one of the possible parameter. 
#We use date parameter to get videos randomly and not focus on trending videos

data_video = get_last_videos('date', 1000)

print('Download completed')
print(len(data_video))

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
data_video = list(keep_first(data_video, lambda d: (d['id'], d['title'])))

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

    
#connect to gpc mysql istance   
mydb = mysql.connector.connect(
  user="root",
  host="35.246.250.240",
  password="M4culture",
  database="youtube_videos"
)

mycursor = mydb.cursor()


# #insert data video in video table

mycursor.execute("SELECT * from videos")
query = mycursor.fetchall()

j = len(query)

val = []

for i in range(len(data_video)):
    j += 1
            
    val.append ((j, data_video[i]["id"], json.dumps(data_video[i]["categories"]), data_video[i]["channel_id"],
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
    
    val.append ((j, data_video[i]["id"], data_video[i]['statistics']["averageRating"], data_video[i]['statistics']["viewCount"],
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