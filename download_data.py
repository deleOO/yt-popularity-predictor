import json

import gdown
import tqdm

for path, url in tqdm.tqdm(json.load(open("urls.json")).items()):
    gdown.download(url, path, quiet=False)
    
