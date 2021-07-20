### yt-popularity-predictor
Final project exam of Big Data Technologies, University of Trento, 2020-21.

## General info
This project is designed for providing a real-time prediction of the popularity in short and long term of videos recently uploaded on YouTube.
The outcome of both predictions is deployed on a web application hosted in a cloud server that allows users to personally pick a video and discover whether that video will be popular or not by simply inserting the URL in a form. 

To reach the goal, we developed two different machine learning model, one for long term prediction (`l_model`) and one for short term prediction (`s_model`). As training data, we used: 

- for`l_model`, an existing dataset [YouTube-8M](https://research.google.com/youtube8m/index.html), which we enriched by scraping metadata with youtube api v3; 
- for `s_model`, we daily scraped around 2000 videos metadata among trending videos and videos uploaded for at least a week. To automate the operation, we used a Virtual Machine (VM) hosted in a cloud server set to schedule the launch scripts and retrain day-to-day the `s_model` at a pre-defined time.

This project is designed to be run in three different stages, each with a dedicated virtual environment:
1) Local ELT for `l_model`
2) Virtual Machine (VM) for `s_model`
3) Web Application

Please, follow carefully setup instructions. 

## Setup
Tested on Windows 10 Home 20H2.
1) Local Local ELT for `l_model`
Create your virtual environment in the main folder:
```
python -m venv .venv
.venv\Scripts\activate
```
First install required packages: 
```
pip install -r requirements.txt
```
To obtain historical dataset, explore it and train long term machine learning, you need to have data saved locally. You can download it by running:
```
python download_data.py
```
If you want to regenerate data and replicate every single steps to create historical data from YT8M validation dataset run:
```
mkdir -p ~/data/yt8m/video; cd ~/data/yt8m/video
curl data.yt8m.org/download.py | partition=2/video/validate mirror=eu python

python data_parser.py
python get_videos_metadata.py
python get_channels_metadata.py
python data_cleaning.py
python data_merger.py
python features_engineering.py
python l_model.py
```
At this point you have the l_model for long term prediction trained. 
We now move to the s_model for short term prediction.

2) Virtual Machine (VM)
This VM environmnet is designed to be deployed on an external server. Every script is designed to be run programmatically on a daily basis. 
To do this we rely on Task Scheduler, a component of Microsoft Windows, that provides the ability to schedule the launch scripts at pre-defined times with batch files.
However, VM can be replicated locally by following the above instruction.

Enter in the vm folder, create virtual environment and install required packages.
```
cd vm
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
To retrain s_model you need access to MySQL db hosted in a cloud instance. To do this, please ask MySQL credentials to us.
Once obtained, run the following scripts in the order indicated:
```
python data_enrichment_new_videos.py
python data_enrichment_trending.py
python clock_query.py
python s_model.py
```

3) Web App
Web app is designed to be deployed on a cloud server with specific credentials. 
You can find the web app at this URL:
https://bdt2021-315814.oa.r.appspot.com/
To use it online, please ask to enable the application to us. 
However, you can run and test it locally following the above instruction.
Enter in the building-an-app folder, create virtual environment and install required packages.
```
cd building-an-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
To test the web application run this script
```
python main.py
```
Pick a yt random video and discover whether or not will be popular. 
Pay attention to select a day-old video. Otherwise no prediction will be provided.
Have a good time! 


