# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
# [START gae_python3_render_template]
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import TextField
import sys
from apiclient.discovery import build
import youtube_dl
from pyyoutube import Api
from datetime import datetime, date
import pandas as pd
import pickle
from sklearn import metrics
from oauth2client.service_account import ServiceAccountCredentials
import json
from gcloud import storage
import urllib
from urllib.parse import urlparse
import numpy as np

# print('il valore passato :',s

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'




# Simple form handling using raw HTML forms
@app.route('/', methods=['GET', 'POST'])
def sign_up():
    error = ""
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        video = request.form['video']
        url_data = urlparse(video)
        query = urllib.parse.parse_qs(url_data.query)
        video_id = query["v"][0]
        
        # Validate form data
        if len(video_id) != 11 :
            # Form data failed validation; try again
            return render_template('base.html', message=('<h1 style="font-size:2vw"><b><cite>Devi inserire un link valido</h1></b></cite>' +
            '<b>Example:</b><br><b><cite>https://www.youtube.com/watch?v=jQzdwMXJuLg</b></cite>' + 
            '</h4><br><img src=' + '"https://icons.iconarchive.com/icons/papirus-team/papirus-apps/256/system-error-icon.png"' 
            + '<width="250" height="auto">'))
            
        else:
            # Form data is valid; move along
            
            return starScraping(video) 

    # Render the sign-up page
    return render_template('base.html', message=error)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

# Run the application
# use my personal api_key
api_key = 'AIzaSyC82xTxZfelpHfr1bdFA7-yx23FdomqJck'

#connect my key to youtube api v3
youtube = build ('youtube', 'v3', developerKey= api_key)

#define a function that get video stats
def get_videos_stats(video_id):
    stats = []
    res = youtube.videos().list(id=video_id, part='statistics').execute()
    stats += res['items']
        
    return stats


def get_metadata(video_id: str) -> str or None:
    url = 'https://www.youtube.com/watch?v=' + video_id
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    try:
        with ydl:
            result = ydl.extract_info(url, download=False)
            return result
    except youtube_dl.utils.DownloadError:
        return None

def is_pop(viewCount, subscriberCount):
    if viewCount>100_000 and subscriberCount>10_000:
        label=1
    else:
        label= 0
    return label

# url = input()

def starScraping(url):
    url_data = urlparse(url)
    query = urllib.parse.parse_qs(url_data.query)
    video_id = query["v"][0]
    stats = get_videos_stats(video_id)
    metadata = get_metadata(video_id)

    stats[0]['statistics']['commentCount'] = int(stats[0]['statistics']['commentCount'])

    api = Api(api_key="AIzaSyC82xTxZfelpHfr1bdFA7-yx23FdomqJck")

    channel = api.get_channel_info(channel_id=metadata.get("channel_id"))
    for data in channel.items:
        channel_metadata = data.to_dict()

    channel_metadata['snippet']['publishedAt'] = channel_metadata['snippet']['publishedAt'][:10]

    data_video = {'video_id': metadata.get("id", None),
                'title': metadata.get("title", None),
                'description': metadata.get("description", None),
                'channel_id': metadata.get("channel_id", None),
                'channel_name': metadata.get("channel", None),
                'duration': metadata.get("duration", None),
                'viewCount': float(metadata.get("view_count", None)),
                'likeCount': float(metadata.get("like_count", None)),
                'dislikeCount': float(metadata.get("dislike_count", None)),
                'averageRating': float(metadata.get("average_rating", None)),
                'uploadDate': metadata.get("upload_date", None),
                'commentCount': float(stats[0]['statistics']['commentCount']),
                'categories': metadata.get("categories", None),
                'pubblishedAt': channel_metadata['snippet']['publishedAt'],
                'viewCount_chn': channel_metadata['statistics']['viewCount'],
                'subscriberCount': channel_metadata['statistics']['subscriberCount'],
                'videoCount': channel_metadata['statistics']['videoCount']
                }
    # data cleaning
    data_video['uploadDate'] = data_video['uploadDate'][:4] + '-' + data_video['uploadDate'][4:6] + '-' + data_video[
                                                                                                            'uploadDate'][
                                                                                                        6:]
    data_video['uploadDate'] = datetime.strptime(data_video['uploadDate'], '%Y-%m-%d')
    data_video['pubblishedAt'] = datetime.strptime(data_video['pubblishedAt'], '%Y-%m-%d')
    data_video['viewCount_chn'] = float(data_video['viewCount_chn'])
    data_video['subscriberCount'] = float(data_video['subscriberCount'])
    data_video['videoCount'] = float(data_video['videoCount'])

    df = pd.DataFrame.from_dict(data_video)

    print('Converting textual predictive features into numeric values')
    # Title and description into string lenght
    df['title_length'] = df['title'].str.len()
    df['descrip_length'] = df['description'].str.len()

    # Computing channel age
    df['chn_year'] = pd.DatetimeIndex(df['pubblishedAt']).year
    df['year'] = float(date.today().year)
    df['chn_age'] = (df['year'] - df['chn_year'])

    # Computing number of days between scraping and uploaded
    df['tday'] = date.today()
    df['tday'] = pd.DatetimeIndex(df['tday'])
    df['upl'] = pd.DatetimeIndex(df['uploadDate'])
    df['day_gap'] = (df['tday'] - df['upl'])
    df['day_gap']= pd.to_timedelta(df['day_gap']).dt.days

    # Computing number of years between scraping and uploaded year
    df['upl_year'] = pd.DatetimeIndex(df['uploadDate']).year
    df['year_gap'] = (df['year'] - df['upl_year'])

    # Computing publishing day of videos
    df['uploadDate'] = pd.to_datetime(df['uploadDate'])
    df["publishing_day"] = df["uploadDate"].dt.day_name()

    # Drop processed values
    df = df.drop(['uploadDate', 'pubblishedAt', 'chn_year',
                'tday', 'upl', 'year', 'upl_year', 'averageRating'], axis = 1)

    print("Introduce a function to prevent zero division error")
    df = df.dropna(subset=['commentCount', 'viewCount', 'likeCount',
                        'dislikeCount', 'subscriberCount', 'viewCount_chn'])

    # Introduce a function to prevent zero division error
    def safe_division(x,y):
        try:
            return x/y
        except ZeroDivisionError:
            return 0

    # Compute channel score
    df['chn_score']= round((safe_division(df.subscriberCount, df.viewCount_chn))*100, 2)
    # Compute views to subscribers
    df['subs_score']= round((safe_division(df.viewCount, df.subscriberCount))*100, 2)
    # Compute user engagement score
    df['ues']= round((safe_division((df.likeCount+df.dislikeCount+df.commentCount), df.viewCount))*100, 2)
    print('User engagement score and channel score computed')

    # Convert to datetime object YT_publishTime
    df['categories'] = df['categories'].astype('category')
    df["categories_cat"] = df["categories"].cat.codes

    df['publishing_day'] = df['publishing_day'].astype('category')
    df["publishing_day_cat"] = df["publishing_day"].cat.codes

    # Drop un-readable data for machine learning
    df = df.select_dtypes(exclude=['object', 'category'])
    df = df.dropna()
    print("Categorical features converted into numeric")

    # Define what influence the prediction
    features = df.drop(labels=['viewCount', 'likeCount', 'dislikeCount', 'commentCount',
                            'viewCount_chn', 'subscriberCount', 'videoCount'], axis=1)
    # Convert features into array
    X = np.array(features)
    
    date_format = "%Y/%m/%d"
    date_video = metadata.get("upload_date", None)
    date_video = date_video[:4] + '/' + date_video[4:6] + '/' + date_video[6:]
    date_video = datetime.strptime(date_video , date_format)
    today = datetime.today()
    today = today.strftime("%Y/%m/%d")
    today = datetime.strptime(today, date_format)
    delta = today - date_video

    if delta.days <= 1:

        s_model = pickle.load(open('s_model.pkl', 'rb'))
        result_short = s_model.predict(X)

        l_model = pickle.load(open('l_model.pkl', 'rb'))
        result_long = l_model.predict(X)
        
        # feature_list = list(X_test.columns)
        # feature_imp = pd.Series(loaded_model.feature_importances_, index=feature_list).sort_values(ascending=False)

        if result_short == 1.0 and result_long == 1.0:
            return render_template('base.html', message=(('<h1 style="font-size:2vw"><b><cite>' + data_video['title'] + '</h1></b></cite>' + '<br>'
            + '</h4><br><img src="' + metadata.get("thumbnails", None)[0]['url'] + '<width="250" height="auto">' + '<br><br>'+
            '<b>Nome del canale: </b>'+ data_video['channel_name'] + '<br>' + 
            '<b>Data di upload del video: </b>' + str(data_video['uploadDate'])[:10] + '<br>' +'<b>Durata video: </b>'+ str (data_video['duration']) + ' secondi' + '<br>'+
            '<b>Categoria: </b>' + str(data_video['categories'][0]) +
            '<br><br>' +
            '<mark><i>Statistiche del video</mark></i>' + '<br>' + '<b>Numero di like: </b>' + str(data_video['likeCount']) + '<br>' + '<b>Numero di views: </b>' + str(data_video['viewCount']) +'<br>' 
            + '<b>Numero di dislike: </b>' + str(data_video['dislikeCount']) + 
            '<br>' + '<b>Numero di commenti: </b>' + str(data_video['commentCount']) +
            '<br><br>' +
            '<mark><i>Statistiche del canale</mark></i>' + '<br>' + '<b>Numero di video: </b>' + str(data_video['videoCount']) + '<br>' + 
            '<b>Numero di views tot: </b>' + str(data_video['viewCount_chn']) + '<br>' + '<b>Numero di iscritti al canale: </b>' + str(data_video['subscriberCount']) + '<br><br>'
            + '<h4 class="popolare">Questo video sarà popolare sul breve termine' + '<br>' + '<h4 class="popolare">Questo video sarà popolare sul lungo termine'
            )))

        elif result_short == 0 and result_long == 1.0:
            return render_template('base.html', message=(('<h1 style="font-size:2vw"><b><cite>' + data_video['title'] + '</h1></b></cite>' + '<br>'
            + '</h4><br><img src="' + metadata.get("thumbnails", None)[0]['url'] + '<width="300" height="300" border="1px">' + '<br><br>'+
            '<b>Nome del canale: </b>'+ data_video['channel_name'] + '<br>' + 
            '<b>Data di upload del video: </b>' + str(data_video['uploadDate'])[:10] + '<br>' +'<b>Durata video: </b>'+ str (data_video['duration']) + ' secondi' + '<br>'+
            '<b>Categoria: </b>' + str(data_video['categories'][0]) +
            '<br><br>' +
            '<mark><i>Statistiche del video</mark></i>' + '<br>' + '<b>Numero di like: </b>' + str(data_video['likeCount']) + '<br>' + '<b>Numero di views: </b>' + str(data_video['viewCount']) +'<br>' 
            + '<b>Numero di dislike: </b>' + str(data_video['dislikeCount']) + 
            '<br>' + '<b>Numero di commenti: </b>' + str(data_video['commentCount']) +
            '<br><br>' +
            '<mark><i>Statistiche del canale</mark></i>' + '<br>' + '<b>Numero di video: </b>' + str(data_video['videoCount']) + '<br>' + 
            '<b>Numero di views tot: </b>' + str(data_video['viewCount_chn']) + '<br>' + '<b>Numero di iscritti al canale: </b>' + str(data_video['subscriberCount']) + '<br><br>'
            + '<h4 class="non_popolare">Questo video non sarà popolare sul breve termine' + '<br>' + '<h4 class="popolare">Questo video sarà popolare sul lungo termine'
            )))

        elif result_short == 1.0 and result_long == 0:
            return render_template('base.html', message=(('<h1 style="font-size:2vw"><b><cite>' + data_video['title'] + '</h1></b></cite>' + '<br>'
            + '</h4><br><img src="' + metadata.get("thumbnails", None)[0]['url'] + '<width="300" height="300" border="1px">' + '<br><br>'+
            '<b>Nome del canale: </b>'+ data_video['channel_name'] + '<br>' + 
            '<b>Data di upload del video: </b>' + str(data_video['uploadDate'])[:10] + '<br>' +'<b>Durata video: </b>'+ str (data_video['duration']) + ' secondi' + '<br>'+
            '<b>Categoria: </b>' + str(data_video['categories'][0]) +
            '<br><br>' +
            '<mark><i>Statistiche del video</mark></i>' + '<br>' + '<b>Numero di like: </b>' + str(data_video['likeCount']) + '<br>' + '<b>Numero di views: </b>' + str(data_video['viewCount']) +'<br>' 
            + '<b>Numero di dislike: </b>' + str(data_video['dislikeCount']) + 
            '<br>' + '<b>Numero di commenti: </b>' + str(data_video['commentCount']) +
            '<br><br>' +
            '<mark><i>Statistiche del canale</mark></i>' + '<br>' + '<b>Numero di video: </b>' + str(data_video['videoCount']) + '<br>' + 
            '<b>Numero di views tot: </b>' + str(data_video['viewCount_chn']) + '<br>' + '<b>Numero di iscritti al canale: </b>' + str(data_video['subscriberCount']) + '<br><br>'
            + '<h4 class="popolare">Questo video sarà popolare sul breve termine' + '<br>' + '<h4 class="non_popolare">Questo video non sarà popolare sul lungo termine'
            )))

            
        else:
            return render_template('base.html', message=(('<h1 style="font-size:2vw"><b><cite>' + data_video['title'] + '</h1></b></cite>' + '<br>'
            + '</h4><br><img src="' + metadata.get("thumbnails", None)[0]['url'] + '<width="300" height="300" border="1px">' + '<br><br>'+
            '<b>Nome del canale: </b>'+ data_video['channel_name'] + '<br>' + 
            '<b>Data di upload del video: </b>' + str(data_video['uploadDate'])[:10] + '<br>' +'<b>Durata video: </b>'+ str (data_video['duration']) + ' secondi' + '<br>'+
            '<b>Categoria: </b>' + str(data_video['categories'][0]) +
            '<br><br>' +
            '<mark><i>Statistiche del video</mark></i>' + '<br>' + '<b>Numero di like: </b>' + str(data_video['likeCount']) + '<br>' + '<b>Numero di views: </b>' + str(data_video['viewCount']) +'<br>' 
            + '<b>Numero di dislike: </b>' + str(data_video['dislikeCount']) + 
            '<br>' + '<b>Numero di commenti: </b>' + str(data_video['commentCount']) +
            '<br><br>' +
            '<mark><i>Statistiche del canale</mark></i>' + '<br>' + '<b>Numero di video: </b>' + str(data_video['videoCount']) + '<br>' + 
            '<b>Numero di views tot: </b>' + str(data_video['viewCount_chn']) + '<br>' + '<b>Numero di iscritti al canale: </b>' + str(data_video['subscriberCount']) + '<br><br>'
            + '<h4 class="non_popolare">Questo video non sarà popolare sul breve termine' + '<br>' + '<h4 class="non_popolare">Questo video non sarà popolare sul lungo termine'
            )))

    else:
        return render_template('base.html', message=('<h1 style="font-size:2vw"><b><cite>Il video è troppo vecchio!</h1></b></cite>' + 
        '<br><b>Il modello è pensato per video caricati da massimo 24 ore sulla piattaforma di YouTube </b>'))

        


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_python_static_files]
