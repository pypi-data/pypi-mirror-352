import json
import logging

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.testclient import TestClient
from fastapi_agmin import create_agmin
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from tests.fastapi_agmin.app_test import Base, create_sample_data

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
session_factory = None


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def _session_factory(engine):
    """Create a session factory."""
    global session_factory
    session_factory = scoped_session(sessionmaker(bind=engine))
    return session_factory


@pytest.fixture(scope="function")
def db(_session_factory):
    """Create a test database session."""
    session = _session_factory()
    try:
        # Clean up existing data
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

        # Create test data using the shared function
        create_sample_data(session)
        yield session
    finally:
        session.close()
        _session_factory.remove()


def get_session():
    """Get a database session for FastAPI dependency injection."""
    if session_factory is None:
        raise RuntimeError("Session factory not initialized")
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def app(_session_factory):
    """Create and configure the FastAPI application."""
    app_for_test = FastAPI(title="Test App")

    @app_for_test.middleware("http")
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

    # Initialize admin interface
    create_agmin(Base, get_session=get_session, app=app_for_test)

    return app_for_test


@pytest.fixture(scope="function")
def client(app, db):
    """Create a test client for the FastAPI application."""
    return TestClient(app)
