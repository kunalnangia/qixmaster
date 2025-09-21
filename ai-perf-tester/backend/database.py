# Database models for AI Performance Tester
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class PerfTestRun(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, index=True)
    test_name = Column(String)
    test_type = Column(String)
    url = Column(String)
    concurrent_users = Column(Integer)
    duration = Column(Integer)
    ramp_up_time = Column(Integer)
    thresholds = Column(JSON)
    summary_metrics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ai_analysis = Column(Text, nullable=True)
    jmx_file_path = Column(String, nullable=True)
    
    # Define relationship to details
    details = relationship("PerfRunDetail", back_populates="test_run", cascade="all, delete-orphan")
    
    # Define relationship to AI recommendations
    recommendations = relationship("AIRecommendation", back_populates="test_run", cascade="all, delete-orphan")

class PerfRunDetail(Base):
    __tablename__ = "run_details"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"))
    timestamp = Column(DateTime)
    avg_response_time = Column(Float)
    error_rate = Column(Float)
    throughput = Column(Integer)
    
    # Define relationship to test run
    test_run = relationship("PerfTestRun", back_populates="details")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"))
    category = Column(String)  # 'bottleneck', 'recommendation', 'next_test'
    description = Column(Text)
    
    # Define relationship to test run
    test_run = relationship("PerfTestRun", back_populates="recommendations")