from flask import Flask, render_template, request, redirect, send_from_directory, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pymysql
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import favicon

Base = declarative_base()
app = Flask(__name__)
UPLOAD_FOLDER = 'path/where/you/want/to/save/uploaded/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['SECRET_KEY'] = "kjvjhevfehjfvehjv"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine('mysql+pymysql://root:password@localhost/database_name')
DBsession = sessionmaker(bind=engine)
sess = DBsession()

class employeeData(Base):
    __tablename__='Data'
    Id=Column(Integer, primary_key=True)
    Names=Column(String(120))
    Employee_id=Column(Integer, unique=True)
    Email=Column(String(120), unique=True)
    Password=Column(String(50))
    Gender=Column(String(50))
    Level=Column(String(50))
    College=Column(String(120))
    Image=Column(String(500))

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up', methods=['POST','GET'])
def signup():
    if request.method=='POST':
        name=request.form["Name"]
        email=request.form["Email_ID"]
        employeeID=request.form["Employee_ID"]
        password=request.form["Password"]
        gender=request.form.get("Gender")
        qual=request.form.get("Qualification")
        coll=request.form["College"]
        empimage=request.files["file"]
        if empimage and allowed_file(empimage.filename):
            filename = secure_filename(empimage.filename)
            empimage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        employees=employeeData(Names=name, Employee_id=employeeID, Email=email, Password=password, Gender=gender, Level=qual, College=coll, Image=filename)
        sess.add(employees)
        sess.commit()
        return render_template('login.html')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        Eid=request.form["Employee_ID"]
        Pswrd=request.form["Password"]
        emp= sess.query(employeeData).filter_by(Employee_id=Eid).filter_by(Password=Pswrd).first()
        if emp is not None:
            name = emp.Names
            E_Id = emp.Employee_id
            email = emp.Email
            password=emp.Password
            gender = emp.Gender
            level = emp.Level
            col = emp.College
            img = emp.Image
            session["login_user"] = name
            return render_template('profileview.html', Name=name, eid=E_Id, Email=email, Gender=gender, Level=level, Col=col, Img=img)
        else:
            flash('Please enter correct Employee ID/ Password!')
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    if session.get("login_user") is not None:
        session["login_user"] = None
        flash('Please login first!!')
        return redirect('/login')
    if session.get("login_user") is None:
        return redirect('/login')

@app.route('/profileview', methods=['GET','POST'])
def profileview():
    if session.get("login_user") is not None:
        if request.method=='POST':
            return render_template('employees.html')
        else:
            return render_template('profileview.html')
    else:
        return redirect('/login')

@app.route('/employees', methods=['GET','POST'])
def employees():
    if session.get("login_user") is not None:
        if request.method=='POST':
            sql= sess.query(employeeData).all()
            return render_template('employees.html', empl=sql)
        else:
            sql= sess.query(employeeData).all()
            return render_template('employees.html', empl=sql)
    else:
        return redirect('/login')

@app.route('/edit_employee/<int:id>', methods=['GET','POST'])
def editemployee(id):
    if session.get("login_user") is not None:
        if request.method=='POST':
            employees = sess.query(employeeData).filter_by(Employee_id=id)
            sql= sess.query(employeeData).all()
            for employee in employees:
                employee.Names = request.form["Name"]
                employee.Email = request.form["Email_ID"]
                employee.Gender = request.form.get('Gender')
                employee.Level = request.form.get('Qualification')
                employee.College = request.form["College"]
            sess.commit()
            return render_template('employees.html', empl=sql)
        else:
            sql = sess.query(employeeData).filter_by(Employee_id=id)
            for emp in sql:
                name = emp.Names
                E_Id = emp.Employee_id
                email = emp.Email
                gender = emp.Gender
                level = emp.Level
                col = emp.College
            return render_template('editemployee.html', Name=name, eid=E_Id, Email=email, Gender=gender, Level=level, Col=col)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.debug = True
    Base.metadata.create_all(engine)
    app.run(port=5000)
