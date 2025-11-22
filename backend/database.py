"""
Database configuration and models using SQLAlchemy.
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./agro_helpdesk.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)
    type = Column(String)
    summary = Column(String)
    channel = Column(String)
    location = Column(String)
    crop = Column(String)
    stage = Column(String, nullable=True)
    images = Column(JSON)  # Store as JSON list of strings
    status = Column(String)
    decision = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    steps = relationship("TicketStep", back_populates="ticket", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="ticket", cascade="all, delete-orphan")

class TicketStep(Base):
    __tablename__ = "ticket_steps"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.id"))
    agent = Column(String)
    text = Column(String)
    ts = Column(String)

    ticket = relationship("Ticket", back_populates="steps")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)

class Runbook(Base):
    __tablename__ = "runbooks"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    safe = Column(Boolean)

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    reduction = Column(Integer)
    avgResolutionTime = Column(Integer)
    accuracy = Column(Integer)
    escalated = Column(Integer)
    topSymptoms = Column(JSON)

class Plot(Base):
    __tablename__ = "plots"

    id = Column(String, primary_key=True, index=True)
    crop = Column(String)
    status = Column(String)
    lat = Column(Float)
    lng = Column(Float)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=True)
    sender = Column(String) # 'user' or 'agent'
    text = Column(Text)
    ts = Column(String)

    ticket = relationship("Ticket", back_populates="messages")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
