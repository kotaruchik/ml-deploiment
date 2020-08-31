from flask import Flask, render_template, request, redirect, flash, send_file
#from flask_session import Session
from flask_cors import CORS, cross_origin

import pickle
import numpy as np
from bulkdatavalidation import bulkdatavalidation
import pandas as pd
from app import app
import os
from flask import Response
from training.trainingmodel import trainingmodel
# import magic
import urllib.request
from app import app


from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Normalize the inputs and set the output
from sklearn.preprocessing import Normalizer
nr = Normalizer(copy=False)
file = open('static/Data/Energy.pkl', 'rb')
model = pickle.load(file)
file.close()

app = Flask(__name__)
app.secret_key = 'super secret key'
CORS(app)

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    RC=request.form['Relative_Compactness']
    SA=request.form['Surface_Area']
    WA=request.form['Wall_Area']
    RA=request.form['Roof_Area']
    OH=request.form['Overall_Height']
    OR=request.form['Orientation']
    GA=request.form['Glazing_Area']
    GAD=request.form['Glazing_Area_Distribution']
    arr = np.array([[RC,SA,WA,RA,OH,OR,GA,GAD]])
    arr = nr.fit_transform(arr)
    mpred=model.predict(arr)
    Heating_l=str(mpred[0,0])
    Colling_l=str(mpred[0,1])

    #return 'ok'+Heating_l+Colling_l
    return render_template('index.html', prediction_text='Energy efficiency heating load and colling load should be  {}'.format(Heating_l+' '+Colling_l),H=Heating_l,C=Colling_l)


@app.route("/bulkupload")
def bulkupload():
    return render_template('bulkupload.html')


@app.route("/bulkpredict",methods=['POST'])
def bulkpredict():
    try:

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join('static/uploads', filename))

                if(filename=='InputFile.csv'):
                    flash('File successfully uploaded')
                    blkv=bulkdatavalidation(filename)
                    blkv.valuesFromSchema()
                    blkv.validationFileNameRaw(filename)
                    blkv.validateColumnLength(8)
                    pred_data=blkv.getdata()
                    pred_data_nor=nr.fit_transform(pred_data)
                    bmpred=model.predict(pred_data_nor)
                    res = pd.DataFrame(bmpred)
                    res.rename(columns={'': 'index', 0: 'heating_load', 1: 'cooling_load'}, inplace=True)
                    res.drop(res.columns[res.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
                    res = pd.concat([pred_data, res], axis=1)
                    res.to_csv('static/Final/prediction.csv')
                    return send_file('static/Final/prediction.csv', as_attachment=True)
                else:
                    os.remove(os.path.join('static/uploads', filename))
                    flash('Soory we cannot predict  , please provide valid file name As InputFile')
                    return redirect('/bulkupload')
            else:
                flash('Allowed file types is csv')
                return redirect('/bulkupload')
    except ValueError:
        return Response("Error Occurred due to input value mismatch! %s" % ValueError)


    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred due to column name mismatch! %s" % e)
    return Response("Prediction successful !!")

@app.route("/retrain")
def retrain():
    train=trainingmodel()
    train.modeltrain()
    return render_template('retrain.html', traininng_text='Energy efficiency Model Training Successful ')


if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=22)
    app.run(debug=True)