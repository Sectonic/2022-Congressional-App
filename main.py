from flask import Flask, render_template, request, session, redirect, url_for, flash, get_flashed_messages, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime 
import json
import random
import pytz
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SECRET_KEY'] = 'hello github!'
db = SQLAlchemy(app)
tz = pytz.timezone('US/Mountain')

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True)
    nickname = db.Column(db.String())
    password = db.Column(db.String())
    timezone = db.Column(db.String())
    classes = db.relationship('Class', backref='taught_class', lazy=True)


class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    start = db.Column(db.String())
    end = db.Column(db.String())
    tardy = db.Column(db.Boolean(), default=False)
    tardy_delay = db.Column(db.Integer())
    pin = db.Column(db.Integer())
    teacher = db.Column(db.Integer(), db.ForeignKey('teacher.id'))
    students = db.relationship('Student', backref='class_student', lazy=True)
    questions = db.relationship('Question', backref='class_question', lazy=True)


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    student_class = db.Column(db.Integer(), db.ForeignKey('class.id'))

class Question(db.Model):
    __tablname__ = 'question'
    id = db.Column(db.Integer(), primary_key=True)
    question = db.Column(db.String())
    type = db.Column(db.String())
    question_class = db.Column(db.Integer(), db.ForeignKey('class.id'))


@app.route('/')
def index():
    if "user" in session:
        user = True
    else:
        user = False
    return render_template('home.html', user=user)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if not "user" in session:
        if request.method == 'POST':
            username = request.form.get('username')
            nickname = request.form.get('nickname')
            password = request.form.get('password')
            timezone = request.form.get('timezone')

            new_user = Teacher(username=username, nickname=nickname, password=password, timezone=timezone)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = username
            return redirect(url_for('classes'))
    else:
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if not "user" in session:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')

            find_user = Teacher.query.filter_by(username=username, password=password).first()
            if find_user:
                session['user'] = username
                return redirect(url_for('classes'))
    else:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/classes', methods=['POST', 'GET'])
def classes():
    if "user" in session:
        data = json.load(open('static/json/data.json'))
        current_user = Teacher.query.filter_by(username=session['user']).first()
        classes = Class.query.filter_by(teacher=current_user.id)

        if request.method == "POST":

            if request.form.get('name'):
                className = request.form.get('name')
                startTime = request.form.get('start')
                endTime = request.form.get('end')
                tardy = True if request.form.get('tardy') == 'on' else False
                tardy_delay = request.form.get('tardy_delay')
                students = request.form.get('all_students')
                questions = request.form.get('all_questions')
                
                new_class = Class(name=className, start=startTime, end=endTime, tardy=tardy, tardy_delay=tardy_delay, teacher=current_user.id, pin=random.randrange(10000, 90000))
                db.session.add(new_class)
                
                students_split = students.split('|')
                for student in students_split:
                    new_student = Student(name=student, student_class=Class.query.count())
                    db.session.add(new_student)

                questions_split = questions.split('|')
                for question in questions_split:
                    question_parts = question.split('/')
                    new_question = Question(question=question_parts[0], type=question_parts[1], question_class=Class.query.count())
                    db.session.add(new_question)
            
            if request.form.get('delete_class'):
                Class.query.filter_by(id=int(request.form.get('delete_class'))).delete()
                Student.query.filter_by(student_class=int(request.form.get('delete_class'))).delete()
                Question.query.filter_by(question_class=int(request.form.get('delete_class'))).delete()
                for key, value in data.items():
                    if str(request.form.get('delete_class')) in data[key]:
                        del data[key][str(request.form.get('delete_class'))]
                    with open('static/json/data.json', "w") as f:
                        f.write(json.dumps(data, indent=4))

            db.session.commit()

        class_info = []
        for classroom in classes:
            students = Student.query.filter_by(student_class=classroom.id).count()
            class_info.append([classroom, students])

    else:
        return redirect(url_for('index'))
    return render_template('classes.html', user=session, class_info=class_info)


@app.route('/sheets', methods=['POST', 'GET'])
def sheets():
    if "user" in session:
        current_user = Teacher.query.filter_by(username=session['user']).first()
        classes = Class.query.filter_by(teacher=current_user.id)
    else:
        return redirect(url_for('index'))
    return render_template('sheets.html', classes=classes)

@app.route('/form/<form_id>', methods=['POST', 'GET'])
def form(form_id):

    classroom = Class.query.filter_by(id=int(form_id)).first()
    teacher = Teacher.query.filter_by(id=classroom.teacher).first()
    students = Student.query.filter_by(student_class=classroom.id)
    questions = Question.query.filter_by(question_class=classroom.id)

    data = json.load(open('static/json/data.json'))
    date = datetime.datetime.now(tz).strftime("%Y-%m-%d")
    class_start = datetime.datetime.strptime(f"{date} {classroom.start}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo('US/Mountain'))
    class_end = datetime.datetime.strptime(f"{date} {classroom.end}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo('US/Mountain'))
    start_time_difference = datetime.datetime.now(tz) - class_start
    start_difference_minutes = round(start_time_difference.total_seconds()/60)

    if request.method == "POST":
        if class_start <= datetime.datetime.now(tz) < class_end:
            pin = request.form.get('pin')
            if int(pin) == classroom.pin:
                student = request.form.get('student')

                new_entry = {
                    "name": student,
                    "attendance": True,
                    "submitted_time": start_difference_minutes,
                }

                for question in questions:
                    current_field = request.form.get(question.question)
                    new_entry[question.question] = current_field

                student_names = []
                for student in students:
                    student_names.append(student.name)

                if date in data.keys():
                    if form_id in data[date].keys():
                        data[date][form_id]["data"].append(new_entry)
                    else:
                        data[date][form_id] = {
                            "info": {
                                "tardy": classroom.tardy,
                                "tardy_delay": classroom.tardy_delay,
                            },
                            "data": [
                                new_entry
                            ]
                        }
                else:
                    data[date] = {
                        form_id: {
                            "info": {
                                "tardy": classroom.tardy,
                                "tardy_delay": classroom.tardy_delay,
                            },
                            "data": [
                                new_entry
                            ] 
                        }
                    }

                with open('static/json/data.json', "w") as f:
                    f.write(json.dumps(data, indent=4))
            else:
                flash(f"{pin} is not the correct pin")
        else:
            flash(f"{classroom.name} is not in session")
        
    return render_template('form.html', classroom=classroom, teacher=teacher, students=students, questions=questions)

@app.route('/change_pin/', methods=['POST', 'GET'])
def change_pin():
    class_id = request.args.get('changing')
    new_pin = request.args.get('pin')
    get_class = Class.query.filter_by(id=int(class_id)).first()
    get_class.pin = int(new_pin)
    db.session.commit()
    return jsonify({'response': 200})

@app.route('/get_students/', methods=['POST', 'GET'])
def get_students():
    class_id = request.args.get('class')
    current_class = Class.query.filter_by(id=class_id).first()
    all_students = Student.query.filter_by(student_class=class_id)
    all_questions = Question.query.filter_by(question_class=class_id)
    start_time = datetime.datetime.strptime(current_class.start, "%H:%M").strftime("%I:%M %p")
    end_time = datetime.datetime.strptime(current_class.end, "%H:%M").strftime("%I:%M %p")
    students = []
    for student in all_students:
        students.append(student.name)
    questions = []
    for question in all_questions:
        questions.append(question.question)
    return jsonify({'students': students, 'questions': questions, 'start': start_time, 'end': end_time})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=81)
