import json
import logging
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Generator

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi_agmin import create_agmin
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    Time,
    create_engine,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("sqlite:///test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI: yields a session and always closes it
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enums
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Models
class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    birth_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    bio = Column(Text)
    profile_picture = Column(LargeBinary)
    allocations = relationship("Allocation", back_populates="person")
    address = relationship("Address", back_populates="person", uselist=False)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), unique=True)
    street = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    person = relationship("Person", back_populates="address")

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(SAEnum(PriorityLevel), default=PriorityLevel.MEDIUM)
    due_date = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    budget = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    start_time = Column(Time)
    end_time = Column(Time)
    allocations = relationship("Allocation", back_populates="task")
    attachments = relationship("Attachment", back_populates="task")
    # Tasks that this task depends on (requirements)
    requirements = relationship(
        "TaskDependency",
        foreign_keys="[TaskDependency.dependent_task_id]",
        back_populates="dependent_task",
    )
    # Tasks that depend on this task (descendants)
    descendants = relationship(
        "TaskDependency",
        foreign_keys="[TaskDependency.requirement_task_id]",
        back_populates="requirement_task",
    )

    def __str__(self):
        return f"{self.title} ({self.status.value})"


class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    allocation_date = Column(Date)
    hours_worked = Column(Float, CheckConstraint("hours_worked IS NULL OR (hours_worked >= 2 AND hours_worked <= 60)"))
    hourly_rate = Column(Numeric(10, 2))
    notes = Column(Text)
    person = relationship("Person", back_populates="allocations")
    task = relationship("Task", back_populates="allocations")

    def __str__(self):
        person = self.person.name if self.person else "?"
        task = self.task.title if self.task else "?"
        return f"{person} - {task} ({self.allocation_date})"


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)  # in bytes
    upload_date = Column(DateTime, default=datetime.utcnow)
    content = Column(LargeBinary)
    task = relationship("Task", back_populates="attachments")

    def __str__(self):
        return f"{self.filename} ({self.file_type})"


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    id = Column(Integer, primary_key=True, index=True)
    dependent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    requirement_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    requirement_task = relationship("Task", foreign_keys=[requirement_task_id], back_populates="descendants")
    dependent_task = relationship("Task", foreign_keys=[dependent_task_id], back_populates="requirements")

    def __str__(self):
        dependent = self.dependent_task.title if self.dependent_task else "Unknown"
        requirement = self.requirement_task.title if self.requirement_task else "Unknown"
        return f"{dependent} depends on {requirement}"


def create_sample_data(session=None):
    """Create sample data for testing."""
    if session is None:
        db = SessionLocal()
    else:
        db = session

    try:
        # Create Persons
        persons = [
            Person(
                name="John Doe",
                email="john@example.com",
                phone="123-456-7890",
                birth_date=date(1990, 1, 1),
                is_active=True,
                bio="Senior Developer",
            ),
            Person(
                name="Jane Smith",
                email="jane@example.com",
                phone="098-765-4321",
                birth_date=date(1992, 5, 15),
                is_active=True,
                bio="Project Manager",
            ),
            Person(
                name="Bob Wilson",
                email="bob@example.com",
                phone="555-123-4567",
                birth_date=date(1985, 12, 31),
                is_active=False,
                bio="QA Engineer",
            ),
        ]
        db.add_all(persons)
        db.flush()  # To get IDs

        # Create Addresses
        addresses = [
            Address(
                person_id=persons[0].id,
                street="123 Main St",
                city="New York",
                state="NY",
                country="USA",
                postal_code="10001",
                latitude=40.7128,
                longitude=-74.0060,
            ),
            Address(
                person_id=persons[1].id,
                street="456 Park Ave",
                city="San Francisco",
                state="CA",
                country="USA",
                postal_code="94102",
                latitude=37.7749,
                longitude=-122.4194,
            ),
        ]
        db.add_all(addresses)

        # Create Tasks
        tasks = [
            Task(
                title="Implement User Authentication",
                description="Add OAuth2 authentication to the API",
                status=TaskStatus.IN_PROGRESS,
                priority=PriorityLevel.HIGH,
                due_date=datetime(2024, 6, 1),
                estimated_hours=40.0,
                actual_hours=25.0,
                budget=Decimal("5000.00"),
                start_time=time(9, 0),
                end_time=time(17, 0),
            ),
            Task(
                title="Database Migration",
                description="Migrate from SQLite to PostgreSQL",
                status=TaskStatus.PENDING,
                priority=PriorityLevel.MEDIUM,
                due_date=datetime(2024, 7, 1),
                estimated_hours=80.0,
                actual_hours=0.0,
                budget=Decimal("10000.00"),
            ),
            Task(
                title="Frontend Redesign",
                description="Update UI to match new brand guidelines",
                status=TaskStatus.COMPLETED,
                priority=PriorityLevel.LOW,
                due_date=datetime(2024, 5, 1),
                estimated_hours=60.0,
                actual_hours=55.0,
                budget=Decimal("7500.00"),
                is_archived=True,
            ),
        ]
        db.add_all(tasks)
        db.flush()

        # Create Allocations
        allocations = [
            Allocation(
                person_id=persons[0].id,
                task_id=tasks[0].id,
                allocation_date=date(2024, 5, 1),
                hours_worked=25.0,
                hourly_rate=Decimal("50.00"),
                notes="Working on OAuth implementation",
            ),
            Allocation(
                person_id=persons[0].id,
                task_id=tasks[1].id,
                allocation_date=date(2024, 5, 2),
                hours_worked=19.0,
                hourly_rate=Decimal("50.00"),
                notes="Working on OAuth implementation 2 (repeatead)",
            ),
            Allocation(
                person_id=persons[1].id,
                task_id=tasks[1].id,
                allocation_date=date(2024, 5, 2),
                hours_worked=None,  # Planning phase, no hours worked yet
                hourly_rate=Decimal("75.00"),
                notes="Planning phase",
            ),
            Allocation(
                person_id=persons[2].id,
                task_id=tasks[2].id,
                allocation_date=date(2024, 4, 15),
                hours_worked=55.0,
                hourly_rate=Decimal("45.00"),
                notes="Completed UI updates",
            ),
        ]
        db.add_all(allocations)

        # Create Attachments
        attachments = [
            Attachment(
                task_id=tasks[0].id,
                filename="auth_design.pdf",
                file_type="application/pdf",
                file_size=1024 * 1024,  # 1MB
                upload_date=datetime(2024, 5, 1),
            ),
            Attachment(
                task_id=tasks[1].id,
                filename="migration_plan.docx",
                file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_size=512 * 1024,  # 512KB
                upload_date=datetime(2024, 5, 2),
            ),
        ]
        db.add_all(attachments)

        # Create Task Dependencies
        dependencies = [
            # Database Migration depends on User Authentication
            TaskDependency(
                dependent_task_id=tasks[1].id,  # Database Migration
                requirement_task_id=tasks[0].id,  # User Authentication
            ),
            # Frontend Redesign depends on Database Migration
            TaskDependency(
                dependent_task_id=tasks[2].id,  # Frontend Redesign
                requirement_task_id=tasks[1].id,  # Database Migration
            ),
        ]
        db.add_all(dependencies)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db():
    """Initialize the database with tables and sample data."""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create sample data
    create_sample_data()


# Initialize database
init_db()

# FastAPI app setup
app_test = FastAPI()


@app_test.middleware("http")
async def log_requests(request: Request, call_next):
    # Log request
    body = await request.body()
    logger.debug(f"Request: {request.method} {request.url}")
    if body:
        try:
            logger.debug(f"Request body: {json.loads(body)}")
        except json.JSONDecodeError:
            logger.debug(f"Request body: {body}")

    # Get response
    response = await call_next(request)

    # Log response
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    logger.debug(f"Response status: {response.status_code}")
    if response_body:
        try:
            logger.debug(f"Response body: {json.loads(response_body)}")
        except json.JSONDecodeError:
            logger.debug(f"Response body: {response_body}")

    # Reconstruct response
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


# Initialize SQLAlchemyAgmin
create_agmin(Base, get_session=get_db, app=app_test, home_url="/dash", ignored_columns=["status"])
