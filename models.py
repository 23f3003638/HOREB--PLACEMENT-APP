from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


# ================= USER =====
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False,unique=True,index=True)
    name = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(255),nullable=False)
    role = db.Column(db.String(20),nullable=False,index=True)# admin, student, company
    email = db.Column(db.String(120), nullable=False,unique=True,index=True)
    contact = db.Column(db.String(15))
    is_approved = db.Column(db.Boolean,default=False)
    is_blacklisted = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    # Relationships
    student_profile = db.relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    company_profile = db.relationship(
        "Company",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    drives = db.relationship(
        "Drive",
        back_populates="company",
        cascade="all, delete-orphan"
    )

    applications = db.relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan"
    )



# ================= STUDENT PROFILE =================
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    contact = db.Column(db.String(15))
    resume = db.Column(db.String(500))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False,unique=True)
    user = db.relationship(
        "User",
        back_populates="student_profile"
    )
    


# ================= COMPANY PROFILE =================
class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hr_name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(20))
    website = db.Column(db.String(255))
    location = db.Column(db.String(100))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False,unique=True)
    user = db.relationship(
        "User",
        back_populates="company_profile"
    )
    


# PLACEMENT DRIVE 
class Drive(db.Model):
    __tablename__ = 'drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False,index=True)
    title = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)
    eligibility = db.Column(db.Text,nullable=False)
    salary = db.Column(db.String(50))
    location = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20),default='pending',index=True)
    created_at = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    company = db.relationship(
        "User",
        back_populates="drives"
    )

    applications = db.relationship(
        "Application",
        back_populates="drive",
        cascade="all, delete-orphan"
    )
    


# ================= APPLICATION =================
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False,index=True)
    drive_id = db.Column(db.Integer,db.ForeignKey('drives.id'),nullable=False,index=True)
    application_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    status = db.Column(db.String(50),default='applied',index=True)# applied, shortlisted, selected, rejected

    student = db.relationship(
        "User",
        back_populates="applications"
    )

    drive = db.relationship(
        "Drive",
        back_populates="applications"
    )
