# dsa3101-2120-01-air/frontend
Building an interactive dashboard "De-layover" that is able to return predictions for flight delay, interactive charts to visualise past trends, as well as easy access to real-time flight information fetched from AviationStack API.

## How to run De-layover with Docker?
* Make sure the variable flask_url in frontend/flask_url.txt is set to 'http://flask:5000/prediction'.
* In the directory dsa3101-2120-01-air/ run ```docker-compose build``` to build new images if you made changes to the other files. For first time users, you don't need to run this.
* Then run ```docker-compose up```
* Visit 'http://localhost:8050/' to view De-layover!

## How to run De-layover without Docker?
* Make sure the Flask app in frontend/model/lm.py is up and running.
* Make sure the variable flask_url in frontend/flask_url.txt is set to 'http://127.0.0.1:5000/prediction'.
* Run ```python app.py``` in the frontend/ directory.
* Visit 'http://localhost:8050/' to view De-layover!

