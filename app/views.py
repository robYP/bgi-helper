from app import app
from flask import Flask, render_template, url_for, redirect, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms.widgets import TextArea
from icecream import ic 
from sqlalchemy.orm.exc import NoResultFound
import pandas as pd
from .forms import RegisterForm, LoginForm, UserForm, ProjectForm, ShipmentForm, ProfitForm
from .models import db, migrate, Users, Projects, Shipments

# Flask_login
login_manager =LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create the table schema in db. Required application context.
with app.app_context():
    db.create_all()

# Import csv to database
def import_csv_to_database(table_name,csv_filename, *columns):
    df = pd.read_csv(csv_filename)
    for index,row in df.iterrows():
        record_data = { column:row[column] for column in columns}
        record = table_name(**record_data)
        db.session.add(record)
    db.session.commit()

# Export database to csv
def export_table_to_csv(table_name, csv_filename):
    query_result = db.session.query(table_name).all()
    df = pd.DataFrame([vars(item) for item in query_result])

    df.to_csv(csv_filename, index=False)

# Register Account 
@app.route('/register', methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check duplicate users by email
        duplicate_email = Users.query.filter_by(email=form.email.data).first()
        if duplicate_email is None:
            hashed_password = generate_password_hash(form.password_hash.data)
            new_user = Users(
                username = form.username.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                password_hash = hashed_password
            )    
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f"User, {new_user.username}, is created successfully")
                return redirect(url_for('dashboard'))
            except:
                flash("User is not added, please try again!")
                return redirect(url_for('dashboard'))
        else:
            flash(f"Email {form.email.data} has been registered")
            return redirect(url_for('dashboard'))

    return render_template("register.html", form=form)

# Login
@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # Check pw hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash(f"{user.username} has logged in successfully!")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong password. Please try again!")
        else:
            flash(f"User does not exist. Please try again!")
    return render_template("login.html", form=form)

# Logout
@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('login'))

# Dashboard
@app.route('/', methods=["GET"])
@login_required
def dashboard():
    
    def find_project_status(project_name:str, shipments) -> project_status | None:
        try:
            project = Projects.query.filter_by(name=project_name).one()
            project_status = project.project_status(shipments)
            return project_status
        except:
            flash(f"Project {project_name} not found!")
            return None
    # Projects

    # GAP_JETTY_II_project = Projects.query.filter_by(name="GAP JETTY II").one()
    # gap_jetty_ii_project_status = GAP_JETTY_II_project.project_status(Shipments)
    # ic(GAP_JETTY_II_project)
    all_projects = Projects.query.all()
    all_project_status = []
    for project in all_projects:
        project_status = find_project_status(project.name, Shipments)
        all_project_status.append(project_status)
    ic(all_project_status)
    gap_jetty_ii_project_status = find_project_status("GAP JETTY II", Shipments)
    gap_project_status = find_project_status("GAP", Shipments)
    rb_project_status = find_project_status("RB", Shipments)
    
    # GAP_project = Projects.query.filter_by(name="GAP").one()
    # gap_project_status = GAP_project.project_status(Shipments)
    # RB_project = Projects.query.filter_by(name="RB").one()
    # rb_project_status = RB_project.project_status(Shipments)
    
    return render_template("index.html",user=current_user, gap_jetty=gap_jetty_ii_project_status, gap=gap_project_status, rb=rb_project_status,Shipments=Shipments, all_project_status=all_project_status )

# Admin
@app.route('/admin', methods=["GET","POST"])
@login_required
def admin():
    ##READ FROM DB
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Users).order_by(Users.id))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_users = result.scalars()
    return render_template("admin.html", all_users=all_users,user=current_user)

# User update 
@app.route('/user/update/<int:id>', methods=["GET","POST"])
@login_required
def user_detail(id):
    user_selected = db.get_or_404(Users, id)
    form = UserForm()
    if request.method == "POST":
        user_selected.first_name = form.first_name.data
        user_selected.last_name = form.last_name.data
        try:
            db.session.commit()
            flash(f"User {user_selected.username} updated successfully!")
            return redirect(url_for('user_detail',id=current_user.id))
        except:
            flash(f"Not updated, something is wrong.. try again!")
            return redirect(url_for('user_detail',id=current_user.id))

    form.first_name.data = user_selected.first_name
    form.last_name.data = user_selected.last_name
    form.username.data = user_selected.username
    form.email.data = user_selected.email
    
    return render_template("user_profile.html", user=user_selected, form=form)

# User Delete
@app.route('/user/<int:id>/delete', methods=["GET"])
@login_required
def delete_user(id):
    # if id == current_user.id:
    user_selected = db.get_or_404(Users, id)
    db.session.delete(user_selected)
    db.session.commit()
    flash(f"User {user_selected.username} deleted!")
    # else:
    # flash("Access Denied!")
    return redirect(url_for('admin'))

# Shipments Detail
@app.route('/shipments', methods=["GET","POST"])
@login_required
def shipments():
    all_shipments = Shipments.query.all()
    form = ShipmentForm()
    
    if form.validate_on_submit():
        new_shipment = Shipments(
                name = str(form.name.data),
                number = form.number.data,
                date = form.date.data,
                quantity = form.quantity.data
        )
        try:
            db.session.add(new_shipment)
            db.session.commit()
            flash(f"Shipment: {new_shipment.name} {new_shipment.date} {new_shipment.quantity} is added successfully")
            return redirect(url_for('shipments'))
        except:
            flash("Shipment is not added, please try again!")
            return redirect(url_for('shipments'))
    
    return render_template("shipments.html",user=current_user, form=form,shipments=all_shipments)

# Shipment Edit
@app.route('/shipments/edit/<int:id>', methods=["GET","POST"])
@login_required
def edit_shipment(id):
    shipment = db.get_or_404(Shipments,id)
    form = ShipmentForm(obj=shipment)
    if form.validate_on_submit():
        shipment.name = str(form.name.data)
        shipment.date = form.date.data
        shipment.quantity = form.quantity.data
        try:
            db.session.commit()
            flash(f"Shipment {shipment.name} updated successfully!")
            return redirect(url_for('shipments'))
        except:
            flash(f"Not updated, something is wrong.. try again!")
            return redirect(url_for('shipments'))

    # form.name.data = shipment.name
    # date = datetime.strptime(shipment.date, '%Y-%m-%d')
    # form.date.data = date
    # form.quantity.data = shipment.quantity
    return render_template('shipment.html',form=form, shipment=shipment,user=current_user, datetime=datetime)

# Shipment Delete
@app.route('/shipments/delete/<int:id>', methods=["GET","POST"])
@login_required
def delete_shipment(id):
    shipment_to_delete = db.get_or_404(Shipments,id)
    try:
        db.session.delete(shipment_to_delete)
        db.session.commit()
        flash(f"Shipment {shipment_to_delete.name} deleted")
        return redirect(url_for('shipments'))
    except:
        flash("Shipment not deleted!")
        return redirect(url_for('shipments'))

# Shipments import from csv
@app.route('/shipments/import_from_csv', methods=["GET"])
@login_required
def import_shipments():
    import_csv_to_database(Shipments, "gap_shipments.csv", "name","number","quantity")
    return redirect(url_for('shipments'))

# Shipments export to csv
@app.route('/shipments/export_to_csv', methods=["GET","POST"])
@login_required
def export_shipments():
    export_table_to_csv(Shipments, "exported_shipments.csv")
    return redirect(url_for('shipments'))

# Projects Page
@app.route('/projects', methods=["GET","POST"])
@login_required
def projects():
    form = ProjectForm()
    all_projects = Projects.query.order_by(Projects.id).all()

    if form.validate_on_submit():
        # Check duplicate project by project name
        duplicate_project = Projects.query.filter_by(name=form.name.data).first()
        if duplicate_project is None:
            new_project = Projects(
                name = form.name.data,
                nation = form.nation.data,
                location = form.location.data,
                invest_type = form.invest_type.data,
                ore_type = form.ore_type.data,
                date = form.date.data,
                intro = form.intro.data,
                fund_raised = form.fund_raised.data,
                profit_b4 = form.profit_b4.data,
                profit_after = form.profit_after.data,
                tax_rate = form.tax_rate.data,
                other_expense = form.other_expense.data,
                cap_profit = form.cap_profit.data,
                interest = form.interest.data,
                wait_interest = form.wait_interest.data,
                commission = form.commission.data,
            )
            try:
                db.session.add(new_project)
                db.session.commit()
                flash(f"Project, {new_project.name}, is created successfully")
            except:
                flash("Project is not added, please try again!")
        else:
            flash(f"Project {form.name.data} has already existed!")
        return redirect(url_for('projects'))
    
    return render_template('projects.html', user=current_user, form=form, projects=all_projects)

# Project Edit
@app.route('/projects/edit/<int:id>', methods=["GET","POST"])
@login_required
def edit_project(id):
    project = db.get_or_404(Projects,id)
    form = ProjectForm(obj=project) 
    if form.validate_on_submit():
        form.populate_obj(project)
        # Replace long code such as:
        # project.name = form.name.data
        # project.location = form.location.data ... 
        try:
            db.session.commit()
            flash(f"Project {project.name} updated successfully!")
            return redirect(url_for('projects'))
        except:
            flash(f"Not updated, something is wrong.. try again!")
            return redirect(url_for('projects'))
    return render_template('project.html',form=form, project=project,user=current_user)

# Project Delete
@app.route('/projects/delete/<int:id>', methods=["GET","POST"])
@login_required
def delete_project(id):
    if current_user.id == 1:
        project_to_delete = db.get_or_404(Projects,id)
        try:
            db.session.delete(project_to_delete)
            db.session.commit()
            flash(f"Project {project_to_delete.name} deleted")
        except:
            flash("Project not deleted.. Try again!")
    else:
        flash("You do not have permission! ")
    return redirect(url_for('projects'))

# Profit calculator
@app.route('/profit-calculator', methods=["GET","POST"])
@login_required
def profit():
    form = ProfitForm()
    if form.validate_on_submit():
        project = form.project.data
        investment = form.investment.data
        eta_shipment = form.shipment.data
        # 回本前每月分潤
        before_even= project.profit_b4 * eta_shipment / project.fund_raised * (investment*10000)
        # 回本月數
        months_to_even= round((investment*10000)/(project.profit_b4 * eta_shipment / project.fund_raised * (investment*10000)),1)
        # 回本後每月分潤
        after_even= project.profit_after * eta_shipment / project.fund_raised * (investment*10000)
        # 回本後年報酬率
        roi_after_even = round((project.profit_after * eta_shipment / project.fund_raised * (investment*10000))/(investment*10000)*12*100,1)
        # 預估每月佣金分潤
        commission = round(project.commission * eta_shipment * investment,2)
        calc_result = {
            'project':str(project),
            'before_even':before_even,
            'months_to_even':months_to_even,
            'after_even':after_even,
            'roi_after_even':roi_after_even,
            'commission':commission
        }
        return render_template('profit.html', user=current_user, form=form, calc_result=calc_result)
    calc_result = {
            'project':'',
            'before_even':0,
            'months_to_even':0,
            'after_even':0,
            'roi_after_even':0,
            'commission':0
    }

    return render_template('profit.html', user=current_user, form=form, calc_result=calc_result)