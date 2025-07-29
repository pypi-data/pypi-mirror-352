from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import random
import string

# --- Configuration ---
DB_USER = "vit"
DB_PASS = "1234"
DB_HOST = "34.46.74.13"
DB_NAME = "test1"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# --- Setup ---
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- Helper functions ---
def rand_str(n=8):
    return ''.join(random.choices(string.ascii_letters, k=n))

def rand_datetime(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# --- Table Definitions ---
class User(Base):
    __tablename__ = 'users2'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))
    created_at = Column(DateTime)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Float)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    product = Column(String(100))
    amount = Column(Float)
    order_time = Column(DateTime)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    message = Column(Text)
    level = Column(String(10))
    timestamp = Column(DateTime)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    location = Column(String(100))
    event_date = Column(DateTime)

# --- Create tables ---
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)

# --- Insert data ---
now = datetime.now()
start_date = now - timedelta(days=30)



# Orders
orders = [
    Order(
        product=rand_str(10),
        amount=round(random.uniform(10, 500), 2),
        order_time=rand_datetime(now,now + timedelta(days=30)
)
    ) for _ in range(random.randint(10, 30))
]
session.add_all(orders)



# --- Commit & Finish ---
session.commit()
session.close()
print("Tables created and sample data inserted.")
