from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField, PasswordField, BooleanField, ValidationError, DecimalField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import datetime
from app.models import Projects

def projects_query():
    return Projects.query

# Create a Register Form
class RegisterForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Password: ", validators=[DataRequired(),EqualTo("password_hash2", message="Passwords need to match.")])
    password_hash2 = PasswordField("Confirm Password: ", validators=[DataRequired()])
    submit = SubmitField("Register")
    
# Create a Login Form
class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Login")

# Create a User Form
class UserForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")
    
# Create a Shipment Form
class ShipmentForm(FlaskForm):
    name = QuerySelectField(query_factory= projects_query, allow_blank=False, get_label="name")
    number = IntegerField("出貨序號", validators=[DataRequired()])
    date = DateField("出貨日期", validators=[DataRequired()], format='%Y-%m-%d')
    quantity = DecimalField("出貨量", validators=[DataRequired()])
    submit = SubmitField("輸入")
    
# Create a Project Form
class ProjectForm(FlaskForm):
    nation = SelectField("國家", choices=["MAL","IND"])
    location = StringField("地點" )
    name = StringField("項目名稱", validators=[DataRequired()])
    invest_type = SelectField("礦種", validators=[DataRequired()], choices=["礦權","固定收益"])
    ore_type = SelectField("礦種", choices=["NICKLE","TIN","IRON"])
    date = DateField("募資日期", validators=[DataRequired()], format='%Y-%m-%d')
    intro = TextAreaField("簡介", validators=[DataRequired()])
    fund_raised = IntegerField("總募資金額")
    profit_b4 = DecimalField("回本前分潤（噸）")
    profit_after = DecimalField("回本後分潤（噸）")
    tax_rate = DecimalField("稅率")
    other_expense = IntegerField("其他花費")
    cap_profit = IntegerField("年分潤上限")
    interest = DecimalField("固定收益預估年報酬")
    wait_interest = DecimalField("等待期利息")
    commission = DecimalField("顧問佣金", validators=[DataRequired()], places=7)
    submit = SubmitField("輸入")

# Create a Profit Form
class ProfitForm(FlaskForm):
    project = QuerySelectField(query_factory= projects_query, allow_blank=False, get_label="name")
    investment = IntegerField("投資單位（萬美）", validators=[DataRequired()])
    shipment = IntegerField("每月預計出貨噸數", validators=[DataRequired()])
    submit = SubmitField("計算", validators=[DataRequired()])