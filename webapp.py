import datetime
import os
import time
import subprocess
import pandas as pd
from flask import Flask, json, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from subprocess import PIPE, run

api = Flask(__name__)
api.config['UPLOAD_FOLDER'] = 'static/uploads'
api.config['MAX_CONTENT_PATH'] = 99999999

def create_app():
   return api

@api.route('/sample', methods=['GET'])
def sample():
    args = request.args
    t_ms = args.get("result", default="", type=str)
    folder = "/".join([api.config['UPLOAD_FOLDER'], t_ms])
    data1 = pd.read_csv("/".join([folder, 'Image1' ,'outputs.csv']), index_col=False)
    data1.index = data1.index + 1
    data2 = pd.read_csv("/".join([folder, 'Image2' ,'outputs.csv']), index_col=False)
    data2.index = data2.index + 1
    return render_template('result.html', utc_dt=datetime.datetime.utcnow(), active_page='dash', folder=folder, file1="Image1", file2="Image2", table1=[data1.to_html()], table2=[data2.to_html()], titles=[''])

@api.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        t = time.time()
        t_ms = str(int(t * 1000))
        folder = "/".join([api.config['UPLOAD_FOLDER'], t_ms])
        path = os.path.join(os.getcwd(), api.config['UPLOAD_FOLDER'], t_ms)
        os.mkdir(path)

        f = request.files['file-a']
        f.save(os.path.join(path, secure_filename(f.filename)))
        file1 = "/".join([folder, f.filename])

        d = request.files['file-b']
        d.save(os.path.join(path, secure_filename(d.filename)))
        file2 = "/".join([folder, d.filename])

        command_process = "python3 main.py -folder '{0}' -out '{0}'".format(path)
        try:
            result_success = subprocess.check_output([command_process], shell=True)
            data1 = pd.read_csv("/".join([folder, 'Image1' ,'outputs.csv']), index_col=False)
            data1.index = data1.index + 1

            data2 = pd.read_csv("/".join([folder, 'Image2' ,'outputs.csv']), index_col=False)
            data2.index = data2.index + 1
        except subprocess.CalledProcessError as e:
            return "An error occurred while trying to fetch task status updates."
        return render_template('result.html', utc_dt=datetime.datetime.utcnow(), active_page='dash', folder=folder, file1=f.filename, file2=d.filename, table1=[data1.to_html()], table2=[data2.to_html()], titles=[''])

@api.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@api.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@api.route('/500')
def error500():
    abort(500)

@api.route('/about/')
def about():
    return render_template('about.html', utc_dt=datetime.datetime.utcnow(), active_page='about')

@api.route('/')
def hello():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow(), active_page='dash', sample = '1665480824258')

if __name__ == '__main__':
    api.run()
