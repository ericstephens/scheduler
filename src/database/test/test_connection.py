import pytest
import os
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import (
    get_database_url, create_db_engine, create_session_factory,
    get_db_session, init_database
)

class TestDatabaseConnection:
    def test_get_database_url_defaults(self):
        """Test database URL generation with default values."""
        with patch.dict(os.environ, {}, clear=True):
            url = get_database_url()
            expected = "postgresql+psycopg://postgres:postgres@localhost:5432/scheduler"
            assert url == expected

    def test_get_database_url_custom_values(self):
        """Test database URL generation with custom environment variables."""
        env_vars = {
            'DB_HOST': 'custom-host',
            'DB_PORT': '5433',
            'DB_NAME': 'custom_db',
            'DB_USER': 'custom_user',
            'DB_PASSWORD': 'custom_pass'
        }
        
        with patch.dict(os.environ, env_vars):
            url = get_database_url()
            expected = "postgresql+psycopg://custom_user:custom_pass@custom-host:5433/custom_db"
            assert url == expected

    def test_create_db_engine(self):
        """Test engine creation."""
        test_url = "postgresql+psycopg://test:test@localhost:5432/test"
        engine = create_db_engine(test_url)
        
        assert engine is not None
        # SQLAlchemy masks passwords in string representation
        engine_url_str = str(engine.url)
        assert "postgresql+psycopg://test:" in engine_url_str
        assert "@localhost:5432/test" in engine_url_str

    def test_create_session_factory(self):
        """Test session factory creation."""
        test_url = "postgresql+psycopg://test:test@localhost:5432/test"
        engine = create_db_engine(test_url)
        session_factory = create_session_factory(engine)
        
        assert session_factory is not None
        # Test that it's callable and returns a session-like object
        assert callable(session_factory)

    @patch('src.database.connection.create_engine')
    def test_create_db_engine_with_echo(self, mock_create_engine):
        """Test engine creation with echo enabled."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch.dict(os.environ, {'DB_ECHO': 'true'}):
            create_db_engine()
            
        # Verify create_engine was called with echo=True
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        assert call_args[1]['echo'] == True

    @patch('src.database.connection.create_engine')
    def test_create_db_engine_without_echo(self, mock_create_engine):
        """Test engine creation with echo disabled (default)."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch.dict(os.environ, {}, clear=True):
            create_db_engine()
            
        # Verify create_engine was called with echo=False
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        assert call_args[1]['echo'] == False

    def test_get_db_session(self, db_engine):
        """Test database session generator."""
        # Use the test engine to create a session factory
        from src.database.connection import create_session_factory
        test_session_factory = create_session_factory(db_engine)
        
        # Patch the global SessionLocal with our test factory
        with patch('src.database.connection.SessionLocal', test_session_factory):
            session_gen = get_db_session()
            
            # Test that it yields a session
            session = next(session_gen)
            assert session is not None
            
            # Test that it closes the session when done
            try:
                next(session_gen)
            except StopIteration:
                # This is expected - generator should close after yielding
                pass

    def test_init_database(self, db_engine):
        """Test database initialization."""
        with patch('src.database.connection.engine', db_engine):
            # This should not raise an exception
            init_database()
            
        # Verify tables exist
        from src.database.connection import Base
        assert len(Base.metadata.tables) > 0

class TestDatabaseEnvironmentVariables:
    def test_all_environment_variables(self):
        """Test that all expected environment variables are handled."""
        env_vars = {
            'DB_HOST': 'test-host',
            'DB_PORT': '1234',
            'DB_NAME': 'test-db',
            'DB_USER': 'test-user',
            'DB_PASSWORD': 'test-password'
        }
        
        with patch.dict(os.environ, env_vars):
            url = get_database_url()
            
        # Verify all variables are included
        assert 'test-host' in url
        assert '1234' in url
        assert 'test-db' in url
        assert 'test-user' in url
        assert 'test-password' in url

    def test_partial_environment_variables(self):
        """Test behavior with only some environment variables set."""
        env_vars = {
            'DB_HOST': 'partial-host',
            'DB_NAME': 'partial-db'
            # Missing DB_PORT, DB_USER, DB_PASSWORD
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            url = get_database_url()
            
        # Should use custom values where provided, defaults elsewhere
        assert 'partial-host' in url
        assert 'partial-db' in url
        assert 'postgres:postgres' in url  # Default user:password
        assert ':5432/' in url  # Default port

class TestDatabaseConnectionIntegration:
    def test_full_connection_flow(self, db_engine):
        """Test the complete connection flow with real database."""
        # Test session creation and basic operations
        from src.database.connection import create_session_factory
        SessionLocal = create_session_factory(db_engine)
        
        # Create a session
        session = SessionLocal()
        
        try:
            # Test basic database operation
            from sqlalchemy import text
            result = session.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
            
        finally:
            session.close()

    def test_session_transaction_rollback(self, db_engine):
        """Test that sessions properly handle rollback on error."""
        from src.database.connection import create_session_factory
        from src.database.models import Instructor
        
        SessionLocal = create_session_factory(db_engine)
        session = SessionLocal()
        
        try:
            # Create an instructor
            instructor = Instructor(
                first_name="Test",
                last_name="Rollback",
                email="rollback@test.com"
            )
            session.add(instructor)
            
            # Force an error by adding duplicate email
            instructor2 = Instructor(
                first_name="Test2", 
                last_name="Rollback2",
                email="rollback@test.com"  # Duplicate email
            )
            session.add(instructor2)
            
            # This should raise an exception
            with pytest.raises(Exception):
                session.commit()
                
        finally:
            session.rollback()
            session.close()
            
        # Verify no data was committed
        session2 = SessionLocal()
        try:
            count = session2.query(Instructor).filter(
                Instructor.email == "rollback@test.com"
            ).count()
            assert count == 0
        finally:
            session2.close()