from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db,User, Student, Company, Application,Drive
from flask import render_template
from flask import request,redirect 
from flask import flash
from flask import session 
from werkzeug.security import generate_password_hash, check_password_hash

# When a user signs up
# hashed_pw = generate_password_hash("my-secret-password")

# # When a user logs in
# is_correct = check_password_hash(hashed_pw, "typed-password")



app = Flask(__name__)

# Database Configuration

app.secret_key = "horeb_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')
#============= login,registrations of  student, admin,company======================================
@app.route('/student_login', methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password) and user.role=='student':
            if user.is_blacklisted:
                flash('you are blacklisted','warning')
                return redirect('/student_login')
            # create session
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Logged in successfully!', 'success')
            return redirect('/student_dashboard')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('student_login.html')


@app.route('/student_registration', methods=["GET", "POST"])
def student_registration():

    if request.method == 'POST':

        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        # hash password
        hashed_password = generate_password_hash(password)
        email = request.form.get('email')
        contact = request.form.get('contact')

        department = request.form.get('department')
        cgpa = request.form.get('cgpa')
        resume = request.form.get('resume')


        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        if existing_user:
            flash("Username or Email already exists", "danger")
            return redirect('/student_login')
        new_user = User(username=username,name=name,password=hashed_password,role="student",email=email,contact=contact,is_approved=True)
        db.session.add(new_user)
        db.session.commit()

        student_profile = Student(name=name,department=department,cgpa=cgpa,contact=contact,resume=resume,user_id=new_user.id)
        db.session.add(student_profile)
        db.session.commit()

        flash("Registration successful", "success")
        return redirect('/student_login')

    return render_template('student_registration.html')






@app.route('/company_login', methods=["GET", "POST"])
def company_login():

    if request.method == "POST":

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()


        if user and check_password_hash(user.password, password)and user.role=='company':
            if user.is_blacklisted:
                flash('you are blacklisted','warning')
                return redirect('/company_login')
            elif not user.is_approved:
                flash("admin approval is pending", "warning")
                return redirect('/company_login')
            
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Logged in successfully!', 'success')


            return redirect('/company_dashboard')

        else:

            flash('Invalid username or password', 'danger')
    return render_template('company_login.html')



@app.route('/company_registration', methods=["GET", "POST"])
def company_registration():
    if request.method=='POST':
        name=request.form.get('name')
        username=request.form.get('username')
        email=request.form.get('email')
        hr_name=request.form.get('hr_name')
        hr_contact=request.form.get('hr_contact')
        website=request.form.get('website')
        location=request.form.get('location')

        password=request.form.get('password')
        hased_pwd=generate_password_hash(password)

        existing_user= User.query.filter((User.username==username) |( User.email==email)).first()
        if existing_user:
            flash("Username or Email already exists", "danger")
            return redirect('/company_login')
        
        new_user=User(name=name,username=username,password=hased_pwd,role="company",email=email,contact=hr_contact,is_approved=False)
        db.session.add(new_user)
        db.session.commit()

        new_company=Company(name=name,hr_name=hr_name,hr_contact=hr_contact,website=website,location=location,user_id=new_user.id)
        db.session.add(new_company)
        db.session.commit()

        flash("Registered successfully!, But wait for admin approval", "info")
        return redirect('/company_login')

    
    return render_template('company_registration.html')



@app.route('/admin_login',methods=["GET","POST"])
def admin_login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        
        user=User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password,password) and user.role=='admin':
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/admin_dashboard')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin_login.html')

#===============================dashboards of admin 
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash("login first",'danger')
        return redirect('/')
    user=User.query.get(session['user_id'])

    if not user or user.role !='admin':
        flash("access denied","danger")
        return redirect('/')
    
    student_count=Student.query.count()
    company_count=Company.query.count()
    drive_count=Drive.query.count()
    application_count=Application.query.count()
    stats={"student":student_count,"company":company_count,"drive":drive_count,"application":application_count}
    return render_template("admin_dashboard.html",stats=stats)
    
    

@app.route('/admin_dashboard/students/search', methods=["GET"])
def admin_searchfor_students():
    if 'user_id' not in session:
        flash('login first', 'danger')
        return redirect('/')
    
    admin = User.query.get(session['user_id'])
    if not admin or admin.role != 'admin':
        flash('access denied', 'danger')
        return redirect('/')
    
    search = request.args.get('search', '')

    if search.isdigit():
        student = Student.query.get(int(search))
        searched_students = [student] if student else []
    elif search:
        searched_students=Student.query.filter( Student.name.contains(search) | Student.contact.contains(search)).all()
    else:
        searched_students=Student.query.all()
        
    return render_template('admin_dashboard_students.html', students=searched_students, search=search)

@app.route('/admin_dashboard/companies/search',methods=["GET"])
def admin_dashboard_companies():
    if 'user_id' not in session:
        flash("login first",'danger')
        return redirect('/')
    user=User.query.get(session['user_id'])
    if not user or user.role !='admin':
        flash("access denied","danger")
        return redirect('/')
    search= request.args.get('search','')
    if search.isdigit():
        company= Company.query.get(int(search))
        searched_companies= [company] if company else []
    elif search:
        searched_companies=Company.query.filter(
            Company.name.contains(search) | Company.hr_name.contains(search)).all()
    else:
        searched_companies=Company.query.all()
    return render_template('admin_dashboard_companies.html',companies=searched_companies,search=search)

@app.route('/admin_dashboard/drives')
def admin_dashboard_drives():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    
    user=User.query.get(session['user_id'])
    if not user or user.role!='admin':
        flash("access denied","danger")
        return redirect('/')
    
    drives=Drive.query.all()
    return render_template('admin_dashboard_drives.html',drives=drives)

@app.route('/admin_dashboard/applications')
def admin_dashboard_applications():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    admin=User.query.get(session['user_id'])
    if not admin or admin.role!='admin':
        flash('access denied','danger')
        return redirect('/')
    applications=Application.query.all()
    return render_template("admin_dashboard_applications.html",applications=applications)



#==============================dashboards of student===============================

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    student_user=User.query.get(session['user_id'])
    if not student_user or student_user.role!='student':
        flash('access denied','danger')
        return redirect('/')
    drives_count = Drive.query.filter_by(status='active').count()
    applications_count = Application.query.filter_by(student_id=session['user_id'] ).count()
    stats={'drives':drives_count,'applications':applications_count}
    return render_template('student_dashboard.html',stats=stats,student_user=student_user)


@app.route('/student_dashboard/drives')
def student_dashboard_drives():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    student_user=User.query.get(session['user_id'])
    if not student_user or student_user.role != 'student':
        flash('access denied','danger')
        return redirect('/')
    drives = Drive.query.filter_by(status='active').all()
    return render_template( "student_dashboard_drives.html", drives=drives, student_user=student_user)

@app.route('/student_dashboard/applications')
def student_dashboard_applications():

    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')

    student_user = User.query.get(session['user_id'])

    if not student_user or student_user.role != 'student':
        flash('access denied','danger')
        return redirect('/')

    applications = Application.query.filter_by(
        student_id=student_user.id
    ).all()

    return render_template(
        "student_dashboard_applications.html",
        applications=applications,
        student_user=student_user
    )

    
    

#=================================studnets crud operation of his/her profile
@app.route('/student_dashboard/profile', methods=["GET","POST"])
def student_dashboard_profile():

    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')

    user = User.query.get(session['user_id'])
    if not user or user.role != 'student':
        flash('access denied','danger')
        return redirect('/')

    student = user.student_profile
    if request.method == "POST":

        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.contact = request.form.get("contact")
        student.name = request.form.get("name")
        student.department = request.form.get("department")
        student.cgpa = request.form.get("cgpa")
        student.resume = request.form.get("resume")
        db.session.commit()

        flash("Profile updated successfully","success")
        return redirect('/student_dashboard/profile')

    return render_template("student_dashboard_profile.html", student=student)

@app.route('/student_dashboard/drive/apply/<int:drive_id>')
def student_dashboard_apply_drive(drive_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    student_user=User.query.get(session['user_id'])
    if not student_user or student_user.role!='student':
        flash('access denied','danger')
        return redirect('/')
    import datetime 
    drive = Drive.query.get_or_404(drive_id)
    if drive.deadline and drive.deadline < datetime.datetime.utcnow():
        flash("Application deadline passed", "danger")
        return redirect('/student_dashboard/drives')
    
    existing = Application.query.filter_by(student_id=student_user.id, drive_id=drive_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('successfully withdraw','success')
    else:
        new_application = Application(student_id=student_user.id,drive_id=drive_id)
        db.session.add(new_application)
        db.session.commit()
        flash('application submitted','success')
    return redirect('/student_dashboard/drives')
    














#
#==============================dashboards of company===============================
@app.route('/company_dashboard')
def company_dashboard():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    company_user=User.query.get(session['user_id'])
    if not company_user or company_user.role!='company':
        flash('access denied','warning')
    drives_count=Drive.query.filter_by(company_id=session['user_id']).count()
    applications_count = Application.query.join(Drive).filter(Drive.company_id == session['user_id']).count()
    stats={"drives":drives_count,"applications":applications_count}
    return render_template('company_dashboard.html',stats=stats,company_user=company_user)
#

@app.route('/company_dashboard/drives')
def company_dashboard_drives():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    company_user=User.query.get_or_404(session['user_id'])
    if not company_user or company_user.role!='company':
        flash('access denied','danger')
        return redirect('/')
    drives=Drive.query.filter_by(company_id=session['user_id']).all()
    return render_template('company_dashboard_drives.html',drives=drives,company_user=company_user)

@app.route('/company_dashboard/applications')
def company_dashboard_applications():

    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')

    company_user = User.query.get(session['user_id'])

    if not company_user or company_user.role != 'company':
        flash('access denied','danger')
        return redirect('/')

    applications = Application.query.join(Drive).filter(Drive.company_id == company_user.id).all()

    return render_template( "company_dashboard_applications.html",applications=applications,company_user=company_user)
#=========================================company profile edit

@app.route('/company_dashboard/profile', methods=["GET","POST"])
def company_dashboard_profile():

    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')

    user = User.query.get(session['user_id'])
    if not user or user.role != 'company':
        flash('access denied','danger')
        return redirect('/')

    company_user= user.company_profile
    if request.method == "POST":
        user.name = request.form.get('name')
        user.username = request.form.get('username')
        user.email = request.form.get('email')

        company_user.hr_name = request.form.get('hr_name')
        company_user.hr_contact = request.form.get('hr_contact')
        company_user.website = request.form.get('website')
        company_user.location = request.form.get('location')

        db.session.commit()

        flash("Profile updated successfully","success")
        return redirect('/company_dashboard/profile')
    return render_template("company_dashboard_profile.html", company_user=company_user)


#==========================================company crud  for drive======================
@app.route('/company_dashboard/add_drive',methods=["GET","POST"] )
def add_drive_for_company():
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    company_user=User.query.get(session['user_id'])
    if not company_user or company_user.role!='company':
        flash('access denied','danger')
        return redirect('/')
    if request.method=='POST':
        company_id=company_user.id
        title=request.form.get('title')
        description=request.form.get('description')
        eligibility=request.form.get('eligibility')
        salary=request.form.get('salary')
        location=request.form.get('location')
        deadline=request.form.get('deadline')
        from datetime import datetime
        deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        drive=Drive(company_id=company_id,title=title,description=description,eligibility=eligibility,salary=salary,location=location,deadline=deadline,status='pending')
        db.session.add(drive)
        db.session.commit()
        flash('drive created successfully,but wait for admin approval','success')
        return redirect('/company_dashboard')
    return render_template("company_dashboard_add_drive.html",company_user=company_user)

@app.route('/company_dashboard/drives/block_unblock/<int:drive_id>')
def company_dashboard_block_unblock(drive_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    company_user=User.query.get_or_404(session['user_id'])
    if not company_user or company_user.role!='company':
        flash('access denied','danger')
        return redirect('/')

    drive = Drive.query.filter_by(id=drive_id, company_id=session['user_id']).first()
    if not drive:
        flash('Drive not found', 'danger')
        return redirect('/company_dashboard/drives')

    if drive.status == 'active':
        drive.status = 'closed'
        flash('Drive closed', 'success')
    elif drive.status == 'closed':
        drive.status = 'active'
        flash('Drive re-opened', 'success')
    else:
        flash('wait for the admin approval', 'warning')
        return redirect('/company_dashboard/drives')

    db.session.commit()
    return redirect('/company_dashboard/drives')

@app.route('/company_dashboard/drives/delete/<int:drive_id>')
def company_dashboard_drive_delete(drive_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    company_user=User.query.get(session['user_id'])
    if not company_user or company_user.role!='company':
        flash('access denied','danger')
        return redirect('/')
    drive=Drive.query.get(drive_id)
    if not drive:
        flash('drive not found','danger')
        return redirect('/company_dashboard/drives')
    db.session.delete(drive)
    db.session.commit()
    flash('deleted successfully','danger')
    return redirect('/company_dashboard/drives')

     
@app.route('/company_dashboard/applications/change_status/<int:app_id>')
def change_application_status(app_id):

    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')

    company_user = User.query.get(session['user_id'])

    if not company_user or company_user.role != 'company':
        flash('access denied','danger')
        return redirect('/')
    application = Application.query.get_or_404(app_id)
    if application.status == "applied":
        application.status = "shortlisted"
    elif application.status == "shortlisted":
        application.status = "selected"
    elif application.status == "selected":
        application.status = "rejected"
    else:
        application.status = "shortlisted"

    db.session.commit()

    return redirect('/company_dashboard/applications')




#======================admin crud  for students===============================================

@app.route("/admin_dashboard/students/block_unblock/<int:user_id>")
def student_block_unblock(user_id):
    if 'user_id' not in session:
        flash('login first', "danger")
        return redirect('/')
    admin = User.query.get(session['user_id'])

    if not admin or admin.role != 'admin':
        flash('access denied','danger')
        return redirect('/')

    student_user = User.query.get(user_id)

    if not student_user or student_user.role != 'student':
        flash('student not found','danger')
        return redirect('/admin_dashboard/students/search')

    if student_user.is_blacklisted:
        student_user.is_blacklisted = False
        student_user.is_approved = True
        flash("student unblocked", "success")
    else:
        student_user.is_blacklisted = True
        student_user.is_approved = False
        flash("student blocked", "success")

    db.session.commit()
    return redirect('/admin_dashboard/students/search')


@app.route("/admin_dashboard/students/delete/<int:user_id>")
def student_delete(user_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect("/")

    admin=User.query.get(session['user_id'])

    if not admin or admin.role !='admin':
        flash('access denied','danger')
        return redirect("/")
    
    student_user=User.query.get(user_id)
    if not student_user or student_user.role !='student':
        flash('student not found','danger')
        return redirect('/admin_dashboard/students/search')
    
    db.session.delete(student_user)
    db.session.commit()
    flash('student deleted successfully','success')
    return redirect("/admin_dashboard/students/search")


    





#======================admin crud  for companies ===============================================
@app.route('/admin_dashboard/companies/block_unblock/<int:user_id>')
def company_block_unblock(user_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    
    admin=User.query.get(session['user_id'])
    if not admin or admin.role!='admin':
        flash('access denied','danger')
        return redirect('/')
    company_user=User.query.get(user_id)

    if company_user.is_blacklisted:
        # If blacklisted → approve
        company_user.is_blacklisted = False
        company_user.is_approved = True
        flash("Company Approved", "success")

    elif company_user.is_approved:
        company_user.is_approved = False
        company_user.is_blacklisted = True
        flash("Company Blacklisted", "warning")

    else:
        company_user.is_approved = True
        flash("Company Approved", "success")

    db.session.commit()
    return redirect('/admin_dashboard/companies/search')


@app.route("/admin_dashboard/companies/delete/<int:user_id>")
def company_delete(user_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    
    admin=User.query.get(session['user_id'])
    if not admin or admin.role !='admin':
        flash('access denied','danger')
        return redirect('/')
    
    company_user=User.query.get(user_id)

    if not company_user or company_user.role!='company':
        flash('company not found','danger')
        return redirect('/admin_dashboard/companies/search')
    db.session.delete(company_user)
    db.session.commit()
    flash('company deleted successfully','success')
    return redirect('/admin_dashboard/companies/search')


#======================admin crud  for drives ===============================================
@app.route('/admin_dashboard/drives/block_unblock/<int:drive_id>')
def drives_block_unblock(drive_id):
    if 'user_id' not in session:
        flash('login first','danger')
        return redirect('/')
    admin=User.query.get(session['user_id'])
    if not admin or admin.role!='admin':
        flash('access denied','danger')
        return redirect('/')
    drive=Drive.query.get(drive_id)
    if not drive:
        flash('drive not found','danger')
        return redirect('/admin_dashboard/drives')

    if drive.status=='pending':
        # If blacklisted → approve
        drive.status='active'
        flash("drive Approved", "success")

    elif drive.status=='active':
        drive.status='closed'
        flash('drive closed','info')
    elif drive.status=='closed':
        drive.status='active'
        flash('drive approved','success')
    db.session.commit()
    return redirect('/admin_dashboard/drives')

@app.route('/admin_dashboard/drives/delete/<int:drive_id>')
def admin_dashboard_drives_delete(drive_id):
    if 'user_id' not in session:
        flash('login in first','danger')
        return redirect('/')
    admin=User.query.get(session['user_id'])
    if not admin or admin.role!='admin':
        flash('access denied','danger')
        return redirect('/')
    
    drive=Drive.query.get(drive_id)
    if not drive:
        flash('Drive not found', 'danger')
        return redirect('/admin_dashboard/drives')
    db.session.delete(drive)
    db.session.commit()
    return redirect("/admin_dashboard/drives")




    





@app.route('/admin_dashboard/add_admin/<int:user_id>')
def stud_admin(user_id):

    if 'user_id' not in session:
        flash('login first','warning')
        return redirect('/')

    admin = User.query.get(session['user_id'])
    if not admin or admin.role != 'admin':
        flash('access denied','warning')
        return redirect('/')

    # ✅ get student FIRST
    student = User.query.get(user_id)

    if not student:
        flash('user not found','danger')
        return redirect('/admin_dashboard/students/search')

    # 🔒 protect root admin
    if student.username == 'adminadmin':
        flash('cannot modify root admin', 'danger')
        return redirect('/admin_dashboard/students/search')

    # 🔁 toggle
    if student.role == 'admin':
        student.role = 'student'
        flash('admin privilege removed', 'success')
    else:
        student.role = 'admin'
        flash('promoted to admin', 'success')

    db.session.commit()
    return redirect('/admin_dashboard/students/search')











@app.route("/logout")
def logout():
    session.clear()
    flash("you are logged out","info")
    return redirect('/')

    



with app.app_context():
        db.create_all()         # Creates all tables

        admin=User.query.filter_by(role='admin').first()
        if not admin:
            admin_user=User(username='adminadmin',name='admin',password=generate_password_hash('1234567890'),role='admin',email='admin@gmail.com',contact='8985876455')
            db.session.add(admin_user)
            db.session.commit()


if __name__ == '__main__':
    
    app.run(debug=True)
