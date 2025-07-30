import pytest
import os
import sqlite3
from cloey.database import SQLiteConnection, PostgreSQLConnection
from cloey.orm import BaseModel
from models import User, Student, Marks


# Set up test database connection
@pytest.fixture(scope='module')
def setup_db():
    """Setup the database for testing."""
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")

    # BaseModel.set_connection(SQLiteConnection("test_database.db"))

    BaseModel.set_connection(PostgreSQLConnection(
        database="cloey",
        user="cloey",
        password="secret",
        host="localhost",
        port=5432
    ))
    
    with BaseModel.get_connection() as conn:
        User.create_table()
        Student.create_table()
        Marks.create_table()
        yield conn


# Test cases
def test_insert_user(setup_db):
    """Test inserting and finding a user."""
    conn = setup_db

    global user
    user = User.create(name="Jane Doe", email="jane.doe@example.com")
    assert user is not None
    assert type(user) is User
    assert user.id is not None
    assert user.name == "Jane Doe"
    assert user.email == "jane.doe@example.com"

def test_find_one_user(setup_db):
    """Test inserting and finding a user."""
    conn = setup_db
    _user = User.get(id=user.id)

    assert _user is not None
    assert _user.id == user.id
    assert _user.name == user.name
    assert _user.email == user.email

def test_find_users(setup_db):
    """Test inserting and finding a user."""
    conn = setup_db
    _users = User.filter(name="Jane Doe")

    assert len(_users) >= 1
    assert _users[0].name == user.name
    assert _users[0].email == user.email

def test_update_user(setup_db):
    """Test updating a user's email."""
    conn = setup_db

    # Insert a user
    User.create(name="Alice", email="alice@example.com")

    # Update the user's email
    User.update(data={"email": "alice.new@example.com"}, name="Alice")

    # Verify the update
    user = User.get(name="Alice")
    assert user is not None
    assert user.email == "alice.new@example.com"

def test_delete_user(setup_db):
    """Test deleting a user."""
    conn = setup_db

    # Insert a user
    User.create(name="Bob", email="bob@example.com")

    # Delete the user
    User.delete(email="bob@example.com")

    # Verify the deletion
    user = User.get(email="bob@example.com")
    assert user is None

def test_all_users(setup_db):
    """Test retrieving all users."""
    conn = setup_db

    # Insert multiple users
    User.create(name="Charlie", email="charlie@example.com")
    User.create(name="Dana", email="dana@example.com")

    # Retrieve all users
    users = User.all()
    assert len(users) >= 2
    names = {user.name for user in users}
    assert "Charlie" in names
    assert "Dana" in names

def test_not_explicit_tablename(setup_db):
    """Test tablename when when __tablename__ not provided"""
    conn = setup_db
    cursor = conn.cursor()

    class Test(BaseModel):
        name: str
        age: int
  
    Test.create_table()  
    query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE' 
        AND table_name = 'tests';""" if Test._get_conn_type() == 'psycopg2.extensions' else "SELECT name FROM sqlite_master WHERE type='table' AND name='tests'"
    cursor.execute(query)
    
    table = cursor.fetchone()
    

    assert table is not None, "The 'tests' table does not exist in the database"
    assert table[0] == 'tests', "Table name does not match 'tests'"

def test_explicit_tablename(setup_db):
    """Test tablename when __tablename__ is provided"""
    conn = setup_db
    cursor = conn.cursor()

    class Test(BaseModel):
        __tablename__ = "unit_tests"
        name: str
        age: int
    
    Test.create_table()  
    query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE' 
        AND table_name = 'unit_tests';""" if Test._get_conn_type() == 'psycopg2.extensions' else "SELECT name FROM sqlite_master WHERE type='table' AND name='unit_tests'"
    cursor.execute(query)
    
    table = cursor.fetchone()
    

    assert table is not None, "The 'tests' table does not exist in the database"
    assert table[0] == 'unit_tests', "Table name does not match 'tests'"

def test_migrations(setup_db):
    """Test generating and applying migrations."""
    conn = setup_db

    # Generate a migration script
    User.generate_and_save_migration()

    # Apply pending migrations
    User.apply_pending_migrations()

def test_foreign_key(setup_db):
    """Test generating and applying migrations."""
    conn = setup_db

    eusebio = Student.create(name="Eusebio Simango", email="e.s@email.com")

    Marks.create(**{'grade': 10, 'student_id': eusebio.id, 'subject': 'Maths'})
    Marks.create(**{'grade': 6.6, 'student_id': eusebio.id, 'subject': 'Ethics'})
    Marks.create(**{'grade': 10, 'student_id': eusebio.id, 'subject': 'Programming'})
    Marks.create(**{'grade': 5.8, 'student_id': eusebio.id, 'subject': 'English II'})

    assert len(eusebio.marks) == 4

    subjects = [m.subject for m in eusebio.marks]
    assert set(subjects) == {"Maths", "Ethics", "Programming", "English II"}

    marks_by_subject = {m.subject: m.grade for m in eusebio.marks}
    assert marks_by_subject["Maths"] == 10
    assert marks_by_subject["Ethics"] == 6.6
    assert marks_by_subject["Programming"] == 10
    assert marks_by_subject["English II"] == 5.8

    for mark in eusebio.marks:
        assert mark.student.id == eusebio.id
        assert mark.student_id == eusebio.id

if __name__ == "__main__":
    pytest.main()
