from app import app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s" 
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app,db)

# Create DB: Users table
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"Name: {self.first_name}"

# Create DB: Shipments table
class Shipments(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    # type = db.Column(db.String(50), nullable=False)
    # date = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Float(2), nullable=False)

# Create DB: Projects table
class Projects(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nation = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    invest_type = db.Column(db.String(50), nullable=False)
    ore_type = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    intro = db.Column(db.String(500), nullable=False)
    fund_raised = db.Column(db.Integer, nullable=True)
    profit_b4 = db.Column(db.Float(2), nullable=True)
    profit_after = db.Column(db.Float(2), nullable=True)
    tax_rate = db.Column(db.Float(2), nullable=True)
    other_expense = db.Column(db.Integer, nullable=True)
    cap_profit = db.Column(db.Integer, nullable=True)
    interest = db.Column(db.Float(2), nullable=True)
    wait_interest = db.Column(db.Float(2), nullable=True)
    commission = db.Column(db.Float(10), nullable=False)
    
    # Calculation Commission
    def commission_earned(self, Shipments,invest_unit):
        """
        Calculate the commission earned based on the Shipments.

        Parameters:
        - Shipments (db Model): Shipments Db model.
        - invest_unit (int): Investment unit for the project.
        
        Returns:
        - float: The Commission Earned for shipments of this project
        """
        shipments = Shipments.query.filter_by(name=self.name)
        total_quantity = sum(shipment.quantity for shipment in shipments)
        return self.commission*total_quantity*invest_unit
    
    # Project Status based on shipments
    def project_status(self, Shipments):
        """
        Calculate the project break-even status based on the Shipments.

        Parameters:
        - Shipments (db Model): Shipments Db model.
        
        Returns:
        - status (dict):{
            name (str): Project Name
            total_shipment (float): Total quantity of the ore shipments, rounded to 3 num after decemal
            tons_required (int): tons of ore shipment required to break even
            progress (float): Break-even progress in percentage
        }
        """
        shipments = Shipments.query.filter_by(name=self.name)
        total_quantity = sum(shipment.quantity for shipment in shipments)

        tons_required = self.fund_raised / self.profit_b4
        progress_percentage = round(total_quantity/tons_required*100)
        status = {
            'name':self.name,
            'total_shipment':round(total_quantity,3),
            'tons_required': tons_required,
            'progress':progress_percentage
        }
        return status
        
    def __repr__(self) -> str:
        return self.name
