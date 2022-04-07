from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import joblib
import numpy as np
import pandas as pd

lm_2012_dep, ct2, test_2012 = joblib.load('lm_2012_dep.pkl')
app = Flask(__name__)

model_list = ['lm_2012_dep']

# curl -G -d 'yr = 2012' -d 'mon = 1' -d 'day_of_week = 7' -d 'dep_hour = 9' -d 'arr_hour = 12' -d 'u_carrier = AA' -d 'origin_airport_code = JFK' -d 'dest_airport_code = LAX' -d 'distance_grp = 10' http://127.0.0.1:5000/prediction
@app.route("/prediction", methods=["GET"])
def make_prediction():
    yr = request.args.get('yr')
    mon = request.args.get('mon')
    day_of_week = request.args.get('day_of_week')
    dep_hour = request.args.get('dep_hour')
    arr_hour = request.args.get('arr_hour')
    u_carrier = request.args.get('u_carrier')
    origin_airport_code = request.args.get('origin_airport_code')
    dest_airport_code = request.args.get('dest_airport_code')
    distance_grp = request.args.get('distance_grp')
    new_df = pd.DataFrame.from_records([(yr, mon, day_of_week, dep_hour, arr_hour, u_carrier, origin_airport_code, dest_airport_code, distance_grp)], 
                                       columns=['yr', 'mon', 'day_of_week', 'dep_hour', 'arr_hour', 'u_carrier', 'origin_airport_code', 'dest_airport_code', 'distance_grp'])
    return jsonify(f"{lm_2012_dep.predict(ct2.transform(new_df))[0]:.3f}")

#curl -F model=@test_upload.txt http://127.0.0.1:5000/upload -v
@app.route("/upload", methods=["POST"])
def upload_model():
    f = request.files['model']
    #print(f.filename)
    f.save(f"{secure_filename(f.filename)}")
    model_list.append(f.filename)
    return render_template('uploaded.html', fname='test')