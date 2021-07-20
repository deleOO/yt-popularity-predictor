# yt-popularity-predictor
Final project exam of Big Data Technologies, University of Trento, 2020-21.

## General info
This project is designed for providing a real-time prediction of the popularity in short and long term of videos recently uploaded on YouTube.
The outcome of both predictions is displayed on a web application hosted in a cloud server that allows users to personally pick a video and discover whether that video will be popular or not by simply inserting the URL in a form. 

![web_app](https://user-images.githubusercontent.com/83338910/126363152-229a7795-bacf-4639-985d-ed8f4f6510f3.jpeg)



To reach the goal, we developed two different machine learning model, one for long term prediction (`l_model`) and one for short term prediction (`s_model`). As training data, we used: 

- for`l_model`, an existing dataset [YouTube-8M](https://research.google.com/youtube8m/index.html) (YT8M), which we enriched by scraping metadata with youtube api v3; 
- for `s_model`, we daily scraped around 2000 videos metadata among videos uploaded for at least a week and trending videos. To automate the operation, we used a Virtual Machine (VM) hosted in a cloud server set to schedule the launch scripts and retrain day-to-day the `s_model` at a pre-defined time.

This project is designed to be run in three different stages, each with a dedicated virtual environment:
1) Extract, transform, and load (ETL) for `l_model`
2) Virtual Machine (VM) for `s_model`
3) Web Application

Please, follow carefully setup instructions. 

## Setup
Tested on Windows 10 Home 20H2.

### 1) ELT for `l_model`
Clone the repo. Then create a virtual environment in the main folder:
```
python -m venv .venv
.venv\Scripts\activate
```
First install required packages: 
```
pip install -r requirements.txt
```
To train the `l_model`, you need to have processed data saved locally. This means to download the validation partition from YT8M dataset and extract information from TensorFlow Record files. Since this process takes a long time, you can easily download from:

* [parsed_val.pkl](https://drive.google.com/uc?export=download&id=1rEGoFPZZtrJtvJe0uYq-VVdJfurClCP8)

Alternatively, you can regenerate data by running:
```
mkdir -p ~/data/yt8m/video; cd ~/data/yt8m/video
curl data.yt8m.org/download.py | partition=2/video/validate mirror=eu python

python data_parser.py
```
Please, make sure you have at least 4 GB of free space in your hard disk before running the above code.

To proceed, you need to have the file parsed_val.pkl locally saved in your machine, no matter which of the previous options you chose.
If you want to replacate step-by-step the operations we performed from data enrichment to the model, run the following scripts in the given order: 
```
python get_videos_metadata.py
python get_channels_metadata.py
python data_cleaning.py
python data_merger.py
python features_engineering.py
python l_model.py
```

At this point, you should finally have the `l_model` saved as pickle file in your machine. 
If you want to save time, you can download all the ELT script outputs (l_model included) by running:
```
python download_data.py
```
We now move to the second stage of the project.

### 2) Virtual Machine (VM)
This VM environmnet is designed to be deployed on an external server. Every script is designed to be run programmatically on a daily basis. 
To do this we rely on Task Scheduler, a component of Microsoft Windows, that provides the ability to schedule the launch scripts at pre-defined times with batch files.
However, VM can be replicated locally by following the instructions below.

Enter in the vm folder, create virtual environment and install required packages.
```
cd vm
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
To retrain `s_model`, you need access to MySQL db hosted in a cloud instance. This needs authentication for you to be able to query information.
Please, contact us for credentials.
Once obtained, run the following scripts in the order indicated:
```
python data_enrichment_new_videos.py
python data_enrichment_trending.py
python clock_query.py
python s_model.py
```
Please, note that an input file is needed to run `clock_query.py`. You can create an empty json named 'mysql_data.json' or download it from:
* [mysql_data.json](https://drive.google.com/uc?export=download&id=1Ep-L7Vvm1nYpfYUWnWV6Zpi4f9t6yhHG)

Let's dive into the last stage.

### 3) Web App
Web app is designed to be deployed on a cloud server with specific credentials. 
You can find the web app at this URL:
https://bdt2021-315814.oa.r.appspot.com/

To use it online, please contact us to enable the application. 
However, you can test the web app locally following this steps:

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
Make sure to have `l_model` in the same folder when running the above script. 
If you did not donwloaded it before, do now from:
* [l_model.pkl](https://drive.google.com/uc?export=download&id=1RUGbdKE2bQK-ayPlI7TUsj35J0S1_tpb)

Pick a random video URL on YouTube and discover whether it will be popular or not, in short and long term.
You can now choose on your own what video will be the best for investing in ads to promote your business!  

Pay attention to select a day-old video. Otherwise no prediction will be provided.

*Have a good time!*


