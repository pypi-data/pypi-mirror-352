import logging
import time
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from fastapi_agmin.agmin import StaticAssetFilter
from sqlalchemy.orm import Session

from src.fastapi_agmin.agmin import SQLAlchemyAgmin

from .app_test import Address, Allocation, Base, Person, Task


@pytest.fixture(autouse=True)
def cleanup_database(db: Session):
    """Clean up the database before each test."""
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    yield


def test_get_metadata(client: TestClient):
    """Test getting model metadata."""
    response = client.get("/agmin/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "Person" in data["models"]
    assert "Task" in data["models"]
    assert "Allocation" in data["models"]
    assert "Address" in data["models"]


def test_list_persons(client: TestClient, db: Session):
    """Test listing persons."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    persons = [
        Person(
            name="John Doe",
            email=f"john_{timestamp}@example.com",
            phone="123-456-7890",
            birth_date=date(1990, 1, 1),
            is_active=True,
            bio="Senior Developer",
        ),
        Person(
            name="Jane Smith",
            email=f"jane_{timestamp}@example.com",
            phone="098-765-4321",
            birth_date=date(1992, 5, 15),
            is_active=True,
            bio="Project Manager",
        ),
        Person(
            name="Bob Wilson",
            email=f"bob_{timestamp}@example.com",
            phone="555-555-5555",
            birth_date=date(1985, 11, 30),
            is_active=False,
            bio="QA Engineer",
        ),
    ]
    for person in persons:
        db.add(person)
    db.commit()
    db.refresh(persons[0])
    db.refresh(persons[1])
    db.refresh(persons[2])

    response = client.get("/agmin/api/person")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "John Doe"
    assert data[1]["name"] == "Jane Smith"
    assert data[2]["name"] == "Bob Wilson"


def test_list_persons_performance(client, db):
    """Test listing >=1000 persons for performance and correctness."""
    # Bulk insert 1000 persons
    persons = [
        Person(
            name=f"Person {i}",
            email=f"person_{i}@example.com",
            phone="000-000-0000",
            birth_date=date(1990, 1, 1),
            is_active=True,
        )
        for i in range(1000)
    ]
    db.bulk_save_objects(persons)
    db.commit()

    start = time.time()
    response = client.get("/agmin/api/person")
    elapsed = time.time() - start

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1000
    # Check a few random records
    assert any(p["name"] == "Person 0" for p in data)
    assert any(p["name"] == "Person 999" for p in data)
    # Performance: adjust threshold as needed
    assert elapsed < 2.0, f"Listing 1000 persons took too long: {elapsed:.2f}s"


def test_create_person(client: TestClient):
    """Test creating a person."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person_data = {
        "name": "John Doe",
        "email": f"john_{timestamp}@example.com",
        "phone": "123-456-7890",
        "birth_date": "1990-01-01",
        "is_active": True,
        "bio": "Senior Developer",
    }
    response = client.post("/agmin/api/person", json=person_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == person_data["name"]
    assert data["email"] == person_data["email"]
    assert data["phone"] == person_data["phone"]
    assert data["birth_date"] == person_data["birth_date"]
    assert data["is_active"] == person_data["is_active"]
    assert data["bio"] == person_data["bio"]


def test_create_task(client: TestClient):
    """Test creating a task."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task_data = {
        "title": f"Test Task {timestamp}",
        "description": "A test task",
        "status": "pending",
        "priority": "high",
        "due_date": "2025-12-31",
    }
    response = client.post("/agmin/api/task", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert data["priority"] == task_data["priority"]
    assert data["due_date"].startswith(task_data["due_date"])


def test_create_allocation(client: TestClient, db: Session):
    """Test creating an allocation."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person = Person(
        name="John Doe",
        email=f"john_{timestamp}@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
    )
    task = Task(
        title=f"Test Task {timestamp}",
        description="A test task",
        status="pending",
        priority="high",
        due_date=date(2025, 12, 31),
    )
    db.add(person)
    db.add(task)
    db.commit()
    db.refresh(person)
    db.refresh(task)

    allocation_data = {
        "person_id": person.id,
        "task_id": task.id,
        "allocation_date": "2025-01-01",
        "hours_worked": 8.0,
        "hourly_rate": 50.0,
        "notes": "Test allocation",
    }
    response = client.post("/agmin/api/allocation", json=allocation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["person_id"] == allocation_data["person_id"]
    assert data["task_id"] == allocation_data["task_id"]
    assert data["allocation_date"] == allocation_data["allocation_date"]
    assert float(data["hours_worked"]) == allocation_data["hours_worked"]
    assert float(data["hourly_rate"]) == allocation_data["hourly_rate"]
    assert data["notes"] == allocation_data["notes"]


def test_update_person(client: TestClient, db: Session):
    """Test updating a person."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person = Person(
        name="John Doe",
        email=f"john_{timestamp}@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
        bio="Senior Developer",
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    # Update person
    new_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    update_data = {
        "name": "John Updated",
        "email": f"john_updated_{new_timestamp}@example.com",
        "phone": "999-999-9999",
        "bio": "Updated Bio",
    }
    response = client.put(f"/agmin/api/person/{person.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["phone"] == update_data["phone"]
    assert data["bio"] == update_data["bio"]


def test_delete_person(client: TestClient, db: Session):
    """Test deleting a person."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person = Person(
        name="John Doe",
        email=f"john_{timestamp}@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    # Delete person
    response = client.delete(f"/agmin/api/person/{person.id}")
    assert response.status_code == 200

    # Verify deletion
    response = client.get(f"/agmin/api/person/{person.id}")
    assert response.status_code == 404


def test_search_persons(client: TestClient, db: Session):
    """Test searching persons."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person = Person(
        name="John Doe",
        email=f"john_{timestamp}@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
        bio="Senior Developer",
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    # Search for person
    response = client.get("/agmin/api/person/search?q=John")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["label"] == f"John Doe (john_{timestamp}@example.com)"


def test_relationship_loading(client: TestClient, db: Session):
    """Test loading relationships."""
    # Create test data
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    person = Person(
        name="John Doe",
        email=f"john_{timestamp}@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
    )
    task = Task(
        title=f"Test Task {timestamp}",
        description="A test task",
        status="pending",
        priority="high",
        due_date=date(2025, 12, 31),
    )
    address = Address(
        street="123 Main St",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001",
    )
    allocation = Allocation(
        person=person,
        task=task,
        allocation_date=date(2025, 1, 1),
        hours_worked=8.0,
        hourly_rate=50.0,
    )
    person.address = address
    db.add(person)
    db.add(task)
    db.add(allocation)
    db.commit()
    db.refresh(person)
    db.refresh(task)
    db.refresh(allocation)

    # Get person with relationships
    response = client.get(f"/agmin/api/person/{person.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == person.name
    assert data["email"] == person.email
    assert data["address"]["street"] == address.street
    assert len(data["allocations"]) == 1
    assert data["allocations"][0]["task"]["title"] == task.title


def test_metadata_relationship_columns(client: TestClient):
    """Test that metadata includes local_columns and remote_columns for relationships."""
    response = client.get("/agmin/api/metadata")
    assert response.status_code == 200
    data = response.json()
    models = data["models"]

    # Check Allocation -> Task relationship
    allocation_rels = models["Allocation"]["relationships"]
    assert "task" in allocation_rels
    task_rel = allocation_rels["task"]
    assert "local_columns" in task_rel
    assert "remote_columns" in task_rel
    # Allocation.task_id -> Task.id
    assert task_rel["local_columns"] == ["task_id"]
    assert task_rel["remote_columns"] == ["id"]

    # Check Allocation -> Person relationship
    assert "person" in allocation_rels
    person_rel = allocation_rels["person"]
    assert person_rel["local_columns"] == ["person_id"]
    assert person_rel["remote_columns"] == ["id"]


def test_allocation_grid_columns(client: TestClient):
    """Test that the Allocation grid shows only the expected columns."""
    response = client.get("/agmin/api/metadata")
    assert response.status_code == 200
    metadata = response.json()

    allocation_columns = metadata["models"]["Allocation"]["columns"]
    allocation_relationships = metadata["models"]["Allocation"]["relationships"]

    # Check that foreign key columns are not present
    assert "person_id" not in allocation_columns
    assert "task_id" not in allocation_columns

    # Check that all expected columns are present
    expected_columns = {"display_name_", "id", "allocation_date", "hours_worked", "hourly_rate", "notes"}
    assert set(allocation_columns.keys()) == expected_columns

    # Check that relationships are present
    assert "person" in allocation_relationships
    assert "task" in allocation_relationships


def test_person_with_many_allocations(client, db):
    """Test a person with 1000+ allocations loads relationships correctly."""
    person = Person(
        name="Bulk Alloc Person",
        email="bulkalloc@example.com",
        is_active=True,
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    # Create 1000 tasks and allocations
    tasks = [
        Task(
            title=f"Task {i}",
            description="Bulk task",
            status="pending",
            priority="high",
            due_date=date(2025, 12, 31),
        )
        for i in range(1000)
    ]
    db.add_all(tasks)
    db.commit()
    db.refresh(tasks[0])

    allocations = [
        Allocation(
            person_id=person.id,
            task_id=tasks[i].id,
            allocation_date=date(2025, 1, 1),
            hours_worked=8.0,
            hourly_rate=50.0,
        )
        for i in range(1000)
    ]
    db.bulk_save_objects(allocations)
    db.commit()

    response = client.get(f"/agmin/api/person/{person.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["allocations"]) == 1000
    # Check that each allocation has a task
    for alloc in data["allocations"][:10]:  # Just sample 10 for speed
        assert "task" in alloc
        assert alloc["task"]["title"].startswith("Task")


def test_static_asset_filter():
    """Test the StaticAssetFilter to ensure it filters out static asset requests."""
    log_filter = StaticAssetFilter()

    # Create mock log records
    static_asset_record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='"GET /assets/somefile.js HTTP/1.1"',
        args=(),
        exc_info=None,
    )
    non_static_asset_record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='"GET /api/someendpoint HTTP/1.1"',
        args=(),
        exc_info=None,
    )

    # Assert filtering behavior
    assert not log_filter.filter(static_asset_record), "Static asset requests should be filtered out."
    assert log_filter.filter(non_static_asset_record), "Non-static asset requests should not be filtered out."


def test_serialize_instance(db: Session):
    """Test the `_serialize_instance` method for SQLAlchemy instances."""
    # Create test data
    person = Person(
        name="John Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
        bio="Senior Developer",
    )
    address = Address(
        street="123 Main St",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001",
    )
    person.address = address
    db.add(person)
    db.commit()
    db.refresh(person)

    # Initialize SQLAlchemyAgmin
    agmin = SQLAlchemyAgmin(Base, lambda: db)

    # Serialize the person instance
    serialized = agmin._serialize_instance(person)

    # Assert serialized is a dictionary
    assert isinstance(serialized, dict), "Serialized instance should be a dictionary."

    # Assert serialized data
    assert serialized["name"] == person.name
    assert serialized["email"] == person.email
    assert serialized["address"]["street"] == address.street
    assert serialized["address"]["city"] == address.city
    assert serialized["address"]["state"] == address.state
    assert serialized["address"]["country"] == address.country
    assert serialized["address"]["postal_code"] == address.postal_code


def test_generate_metadata(db: Session):
    """Test the `generate_metadata` method for SQLAlchemy models."""
    # Initialize SQLAlchemyAgmin
    agmin = SQLAlchemyAgmin(Base, lambda: db)

    # Generate metadata
    metadata = agmin.generate_metadata()

    # Assert metadata structure
    assert "Person" in metadata["models"], "Person model should be in metadata."
    assert "Task" in metadata["models"], "Task model should be in metadata."

    # Assert Person model metadata
    person_metadata = metadata["models"]["Person"]
    assert "columns" in person_metadata, "Person metadata should include columns."
    assert "relationships" in person_metadata, "Person metadata should include relationships."
    assert "name" in person_metadata["columns"], "Person columns should include 'name'."
    assert "email" in person_metadata["columns"], "Person columns should include 'email'."

    # Assert Task model metadata
    task_metadata = metadata["models"]["Task"]
    assert "columns" in task_metadata, "Task metadata should include columns."
    assert "relationships" in task_metadata, "Task metadata should include relationships."
    assert "title" in task_metadata["columns"], "Task columns should include 'title'."
    assert "description" in task_metadata["columns"], "Task columns should include 'description'."


def test_list_items(client: TestClient, db: Session):
    """Test the `list_items` endpoint for listing items and applying filters."""
    # Create test data
    person1 = Person(
        name="John Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
        is_active=True,
    )
    person2 = Person(
        name="Jane Smith",
        email="jane.smith@example.com",
        phone="987-654-3210",
        birth_date=date(1992, 5, 15),
        is_active=False,
    )
    task1 = Task(
        title="Task 1",
        description="First task",
        status="pending",
        priority="high",
        due_date=date(2025, 12, 31),
    )
    task2 = Task(
        title="Task 2",
        description="Second task",
        status="completed",
        priority="low",
        due_date=date(2025, 11, 30),
    )
    allocation1 = Allocation(
        person=person1,
        task=task1,
        allocation_date=date(2025, 1, 1),
        hours_worked=8.0,
        hourly_rate=50.0,
    )
    allocation2 = Allocation(
        person=person2,
        task=task2,
        allocation_date=date(2025, 2, 1),
        hours_worked=6.0,
        hourly_rate=60.0,
    )
    db.add_all([person1, person2, task1, task2, allocation1, allocation2])
    db.commit()

    # Test listing persons
    response = client.get("/agmin/api/person")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "John Doe"
    assert data[1]["name"] == "Jane Smith"

    # Test listing tasks
    response = client.get("/agmin/api/task")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"

    # Test relationships between persons and tasks via allocations
    response = client.get(f"/agmin/api/person/{person1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["allocations"]) == 1
    assert data["allocations"][0]["task"]["title"] == "Task 1"

    response = client.get(f"/agmin/api/person/{person2.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["allocations"]) == 1
    assert data["allocations"][0]["task"]["title"] == "Task 2"
