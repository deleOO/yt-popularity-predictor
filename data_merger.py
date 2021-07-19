import pandas as pd
import json
print("Libraries loaded")

dfData = pd.read_json('videos_metadata.json')
dfChannel = pd.read_json('channel_metadata.json')

print("Data loaded")
print("lenght of videos_metadata: %s" %len(dfData))
print("lenght of channel_metadata: %s" %len(dfChannel))
print("*********************************")
print("structure of videos_metadata:\n%s" %dfData.head(2).transpose())

# Convert 'categories' from list to objects
def to_obj(series):
    return pd.Series([x for _list in series for x in _list])

cat_to_obj= to_obj(dfData["categories"])
cat_to_obj = pd.DataFrame(cat_to_obj)
print("Converted 'categories' from list to objects")

#Overwrite the 'categories' list-colmuns with object-column
columns_to_overwrite = ["categories"]
dfData.drop(labels=columns_to_overwrite, axis="columns", inplace=True)
dfData[columns_to_overwrite] = cat_to_obj[0]

print("'categories' column updated")
print("*********************************")
print("structure of channel_metadata:\n%s" % dfChannel.head(2).transpose())

# Convert channel statistics from dictionary to columns
dfChn = pd.concat([dfChannel.drop(['statistics'], axis=1), dfChannel['statistics'].apply(pd.Series)], axis=1)
print("Dictionary in channel_metadata unpacked")

# Merge data on channel_id
df = dfData.merge(dfChn, on=('channel_id'),how='inner', suffixes=("_vid", "_chn"))
print('Data merged!')

# Filter out non-relevant columns
df = df.drop(['id_vid', 'id_chn','labels', 'title_chn', 'hiddenSubscriberCount', 'averageRating'], axis = 1)

print('Un-relevant data dropped')

# Filter out duplicates
df = df.drop_duplicates(subset='video_id')
df = df.rename(columns={'title_vid' : 'title',
                        'viewCount_vid' : 'viewCount'
                        })
print("*********************************")
print("final structure:\n%s" %df.head(2).transpose())
df = df.to_json('/home/cclsrt/yt-popularity-predictor/merged_data.json')

print("*******************************")
print('Saved in merged_data.json')