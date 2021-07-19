import pandas as pd
import datetime
from datetime import date

print('Libraries imported')
df = pd.read_json ('merged_data.json')

print('Data successfully Loaded')

print('Converting textual predictive features into numeric values')
# Title and description into string lenght
df['title_length'] = df['title'].str.len()
df['descrip_length'] = df['description'].str.len()

# Computing channel age
df['chn_year'] = pd.DatetimeIndex(df['pubblishedAt']).year
df['year'] = float(datetime.date.today().year)
df['chn_age'] = (df['year'] - df['chn_year'])
# Drop processed values
df=df.drop(['pubblishedAt', 'year', 'chn_year'], axis = 1)

df['tday'] = date.today()
df['tday'] = pd.DatetimeIndex(df['tday'])
df['upl'] = pd.DatetimeIndex(df['uploadDate'])
df['day_gap'] = (df['tday'] - df['upl'])
df['day_gap']= pd.to_timedelta(df['day_gap']).dt.days

# Computing number of years between scraping and uploaded year
df['upl_year'] = pd.DatetimeIndex(df['uploadDate']).year
df['year'] = float(datetime.date.today().year)
df['year_gap'] = (df['year'] - df['upl_year'])

# Computing publishing day of videos
df['uploadDate'] = pd.to_datetime(df['uploadDate'])
df["publishing_day"] = df["uploadDate"].dt.day_name()
# Drop processed values
df = df.drop(['uploadDate', 'tday', 'upl', 'year', 'upl_year'], axis = 1)

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
df['subs_score']= round((safe_division(df.viewCount, df.subscriberCount))*100, 2)
# Compute user engagement score
df['ues']= round((safe_division((df.likeCount+df.dislikeCount+df.commentCount), df.viewCount))*100, 2)

print('User engagement score and channel score computed')

# Define popularity metric for long prediction
def is_pop(ues, chn_score):
    if ues > 5 and chn_score > 0.3:
        label = 1
    else:
        label = 0
    return label

df['pop'] = df.apply(lambda x: is_pop(x['ues'], x['chn_score']), axis=1)
print("Popularity metric for long-term computed")

# Filtering outliers
df = df[df.viewCount < 1*1e8]
print("Outliers deleted")
print("Final structure:")
print(df.head(1).transpose())
print('Features engineering concluded! Saving the data into json')
df = df.to_json('processed_data.json')
print("***********************************")
print('Saved in processed_data.json')