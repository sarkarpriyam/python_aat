from flask import Flask, render_template, session, request, redirect, g, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

import os

# Initialization of app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Mlproblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_topic = db.Column(db.String(80), default='General topic')
    question_description = db.Column(db.String(600), nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)
    question_answer = db.Column(db.String(1000), nullable=False)

# from app import db
# with app.app_context():
#     db.create_all()


# Global variables
user_email = None

# All the respective routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:
            session['user'] = email
            global user_email
            user_email = email
            session['name'] = user.name
            return redirect('/forum')

    return render_template('login.html')

@app.route('/forum')
def forum():
    if 'user' in session:
        return render_template('forum.html')
    return redirect('login')

@app.route('/ml', methods=['GET', 'POST'])
def ml():
    if request.method == 'POST':
        question_topic = request.form.get('question_topic')
        question_description = request.form.get('question_description')
        mlproblem = Mlproblem(question_topic=question_topic, question_description=question_description)
        db.session.add(mlproblem)
        db.session.commit()
        return redirect('ml')
    if 'user' in session:
        datas = Mlproblem.query.all()
        return render_template('ml.html', datas=datas)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    global user_email
    user_email = None
    return redirect('login')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    phone = request.form.get('phone')
    valid = re.search(r"^[\w\.]+\.(ai)\d{2}@bmsce\.ac\.in$", email)
    if not valid:
        return render_template('400.html')
    name = request.form.get('name')
    year = request.form.get('year')
    department = request.form.get('department')
    password = request.form.get('password')
    user = User(username=email, phone=phone, name=name, year=year, department=department, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect('login')

@app.route('/ml/answer/<int:question_id>')
def answer(question_id):
    
    datas = Answer.query.filter_by(question_id=question_id).all()
    return render_template('answer.html', datas=datas, question_id=question_id)

@app.route('/ml/answer/submit', methods=['POST'])
def submit():
    id = request.form.get('answer_id')
    question_answer = request.form.get('question_answer')
    data = Answer(question_id=id, question_answer=question_answer)
    db.session.add(data)
    db.session.commit()
    return redirect('/ml')


# Delete and edit routes
@app.route('/deletepage')
def deletepage():
    if user_email == "priyamsarkar.ai23@bmsce.ac.in":
        datas = Mlproblem.query.all()
        return render_template('delete.html',datas=datas)
    return "Login first"

@app.route('/delete/<id>')
def delete(id):
    sql = Mlproblem.query.get(id)
    db.session.delete(sql)
    db.session.commit()
    return redirect('/deletepage')

@app.route('/userpage')
def userpage():
    if user_email == "priyamsarkar.ai23@bmsce.ac.in":
        datas = User.query.all()
        return render_template('userpage.html', datas=datas)
    return "Login First!"

@app.route('/userdelete/<id>')
def userdelete(id):
    sql = User.query.get(id)
    db.session.delete(sql)
    db.session.commit()
    return redirect('/userpage')


@app.route('/answerpage')
def answerpage():
    if user_email == "priyamsarkar.ai23@bmsce.ac.in":
        datas = Answer.query.all()
        return render_template('answerpage.html', datas=datas)
    return "Login First"

@app.route('/answerdelete/<id>')
def answerdelete(id):
    sql = Answer.query.get(id)
    db.session.delete(sql)
    db.session.commit()
    return redirect('/answerpage')

if __name__ == "__main__":
    app.run(debug=True)