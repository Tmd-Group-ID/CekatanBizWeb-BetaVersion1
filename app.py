from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pony.orm import Database, Required, PrimaryKey, db_session
from datetime import datetime
import hashlib
import os
from werkzeug.utils import secure_filename
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
import pandas as pd
import pyspark.pandas as ps

app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")
app.secret_key = 'super_secret_key'

# Database configuration
database = Database()
database.bind(provider='mysql', host='localhost', user='root', passwd='', db='cekatanbiz')

class User(database.Entity):
    _table_ = 'user_data'
    userID = PrimaryKey(int, auto=True)
    name = Required(str)
    email = Required(str, unique=True)
    password = Required(str)
    reg_date = Required(datetime, default=lambda: datetime.now())

database.generate_mapping(create_tables=True)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

spark = SparkSession.builder.appName("CekatanBiz Tools Data Analyst").getOrCreate()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('register-signin.html', title='CekatanBiz is Tools Data Analyst')

@app.route('/register', methods=['POST'])
@db_session
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Please fulfill name, email, and password!'})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        user = User(name=name, email=email, password=hashed_password)
        database.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/login', methods=['POST'])
@db_session
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Please fill all the fields!'})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = User.get(email=email, password=hashed_password)

    if user:
        session['user_id'] = user.userID
        session['user_name'] = user.name
        session['user_email'] = user.email
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Email and password are wrong!'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/upload_files')
def upload_files():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('uploadfile.html', title='CekatanBiz is Tools Data Analyst')

@app.route('/get_user_details', methods=['GET'])
def get_user_details():
    if 'user_id' in session:
        user_details = {
            'userID': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email']
        }
        return jsonify(user_details)
    else:
        return jsonify({'error': 'User not logged in'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    column_name = request.form.get('column_name')
    if not column_name:
        return jsonify({'success': False, 'message': 'Please provide column name for pie chart'})
    
    try:
        psdf = ps.DataFrame(df)
        column_counts = psdf[column_name].value_counts()

        plt.figure(figsize=(10, 6))
        column_counts.plot.pie(autopct='%1.1f%%')
        plt.title("Your Data Chart Pie")
        pie_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pie_chart.png')
        plt.savefig(pie_chart_path)
        plt.close()

        return jsonify({'success': True, 'pie_chart_path': pie_chart_path})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10005)
