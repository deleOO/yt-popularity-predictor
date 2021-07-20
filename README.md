# yt-popularity-predictor
This repo consist of our team-project for the final exam in the Big Data Technologies course, University of Trento, 2021.

## General info
This project is designed for providing a real-time prediction of the popularity in short and long term of recently uploaded youtube videos.
To reach the goal, we trained two different machine learning model, one for long term (`l_model`) prediction and one for short term (`s_model`).
The first one 


This project is designed to be run in three different stages each with a dedicated virtual environment:
1) Historical Dataset for ML
2) Virtual Machine (VM)
3) Web Application
For this reason, follow carefully setup instructions. 

## Setup
Tested on Windows 10 Home 20H2.
1) Historical Dataset for ML
Create your virtual environment in the main folder:
```
python -m venv .venv
.venv\Scripts\activate
```
First install required packages: 
```
pip install -r requirements.txt
```
To obtain historical dataset, explore it and train long term machine learning run you need to have data saved locally. You can download it by running:
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
```
You can examine the data by running `data_explorer.py`.
