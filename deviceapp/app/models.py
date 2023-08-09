from dataclasses import dataclass
from .extensions import db
from datetime import datetime

@dataclass
class App(db.Model):
    deviceid: str
    data1: float
    data2: float
    data3: float
    data4: float
    data5: float
    dt_start: datetime
    
    id = db.Column(db.Integer, primary_key=True)
    deviceid = db.Column(db.String(5), unique=False, nullable=False)
    data1 = db.Column(db.Float, unique=False, nullable=False)
    data2 = db.Column(db.Float, unique=False, nullable=False)
    data3 = db.Column(db.Float, unique=False, nullable=False)
    data4 = db.Column(db.Float, unique=False, nullable=False)
    data5 = db.Column(db.Float, unique=False, nullable=False)
    dt_start = db.Column(db.DateTime, nullable=False, default=datetime.now)