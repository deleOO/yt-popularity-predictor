import pymysql
import pandas as pd
from datetime import datetime, date
import json

dbcon = pymysql.connect(
  user="root",
  host="35.246.250.240",
  password="M4culture",
  database="youtube_videos"
)

# Load data previously collected in sql
df_base = pd.read_json ('mysql_data.json')
print("Data loaded")

# Download daily update
try:
    SQL_Query = pd.read_sql_query(
    '''
    SELECT *
    FROM videos AS v
    INNER JOIN stats_videos AS sv 
    ON sv.video_id=v.video_id
    AND v.downloadDate_vid= CURRENT_DATE
    INNER JOIN stats_channels AS sc 
    ON sc.channel_id=v.channel_id
    INNER JOIN channels AS c 
    ON c.channel_id=v.channel_id
    ''',
      dbcon)

    df = pd.DataFrame(SQL_Query)
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.drop_duplicates(subset='video_id', keep='first')
    df = df.drop(['id', 'id_vid', 'id_chn', 'downloadDate_chn',
                  'averageRating', 'downloadDate_vid'], axis=1)
except:
    print("Error: unable to convert the data")

dbcon.close()

print("Query executed")
# Perform feature engineering
df['categories'] = df['categories'].apply(lambda x: x.replace('["','').replace('"]',''))
df = df.rename(columns = {"title_vid": "title",
                          "viewCount_vid": "viewCount"}
               )

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
              'tday', 'upl', 'year', 'upl_year'], axis = 1)

print('Features converted into numeric values')
print("Introduce a function to prevent zero division error")
df=df.dropna(subset=['commentCount', 'viewCount', 'likeCount', 'dislikeCount', 'subscriberCount', 'viewCount_chn'])
print("NaN values dropped")

# Introduce a function to prevent zero division error
def safe_division(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0

# Compute channel score
df['chn_score']= round((safe_division(df.subscriberCount, df.viewCount_chn))*100, 2)
# Compute views to subscribers
df['subs_score'] = round((safe_division(df.viewCount, df.subscriberCount))*100, 2)
# Compute user engagement score
df['ues'] = round((safe_division((df.likeCount+df.dislikeCount+df.commentCount), df.viewCount))*100, 2)

print('User engagement score and channel score computed')

# Define popularity metric for short-term prediction
def is_pop(ues):
    if ues > 5:
        label = 1
    else:
        label = 0
    return label

df['pop'] = df.apply(lambda x: is_pop(x['ues']), axis=1)
print("Popularity metric for long-term computed")

print('Features engineering concluded! Saving the data into json')
print(df.head().transpose())
print(len(df))
print(len(df_base))
#concatenate dataframes
df = pd.concat([df_base, df], ignore_index = True)

print(len(df))

df = df.to_json('mysql_data.json')

print('Data successfully saved!')

