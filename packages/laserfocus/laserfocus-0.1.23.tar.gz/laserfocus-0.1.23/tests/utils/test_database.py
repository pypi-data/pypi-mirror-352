import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
from laserfocus.utils.database import DatabaseHandler
from laserfocus.utils.response import Response

# Test setup
Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime)

@pytest.fixture
def db_handler():
    engine = create_engine('sqlite:///:memory:')
    handler = DatabaseHandler(Base, engine, type='sqlite')
    return handler

def test_database_initialization(db_handler):
    assert db_handler.engine is not None
    assert db_handler.type == 'sqlite'
    assert db_handler.base is not None
    assert db_handler.metadata is not None

def test_create_record(db_handler):
    data = {'name': 'test_name'}
    response = db_handler.create('test_table', data)
    
    assert response['status'] == 'success'
    assert isinstance(response['content'], int)  # Should return the new ID

    # Verify the record exists
    read_response = db_handler.read('test_table', {'id': response['content']})
    assert read_response['status'] == 'success'
    assert len(read_response['content']) == 1
    assert read_response['content'][0]['name'] == 'test_name'

def test_update_record(db_handler):
    # First create a record
    data = {'name': 'original_name'}
    create_response = db_handler.create('test_table', data)
    record_id = create_response['content']

    # Update the record
    update_data = {'name': 'updated_name'}
    update_response = db_handler.update('test_table', {'id': record_id}, update_data)
    
    assert update_response['status'] == 'success'
    
    # Verify the update
    read_response = db_handler.read('test_table', {'id': record_id})
    assert read_response['content'][0]['name'] == 'updated_name'

def test_read_records(db_handler):
    # Create multiple records
    db_handler.create('test_table', {'name': 'test1'})
    db_handler.create('test_table', {'name': 'test2'})
    
    # Read all records
    response = db_handler.read('test_table')
    assert response['status'] == 'success'
    assert len(response['content']) == 2
    
    # Read with filter
    filtered_response = db_handler.read('test_table', {'name': 'test1'})
    assert filtered_response['status'] == 'success'
    assert len(filtered_response['content']) == 1
    assert filtered_response['content'][0]['name'] == 'test1'

def test_delete_record(db_handler):
    # Create a record
    data = {'name': 'to_delete'}
    create_response = db_handler.create('test_table', data)
    record_id = create_response['content']
    
    # Delete the record
    delete_response = db_handler.delete('test_table', {'id': record_id})
    assert delete_response['status'] == 'success'
    
    # Verify deletion
    read_response = db_handler.read('test_table', {'id': record_id})
    assert len(read_response['content']) == 0

def test_delete_all_records(db_handler):
    # Create multiple records
    db_handler.create('test_table', {'name': 'test1'})
    db_handler.create('test_table', {'name': 'test2'})
    
    # Delete all records
    response = db_handler.delete_all('test_table')
    assert response['status'] == 'success'
    
    # Verify all records are deleted
    read_response = db_handler.read('test_table')
    assert len(read_response['content']) == 0

def test_get_tables(db_handler):
    response = db_handler.get_tables()
    assert response['status'] == 'success'
    assert 'test_table' in response['content']

def test_get_schema(db_handler):
    response = db_handler.get_schema('test_table')
    assert response['status'] == 'success'
    schema = response['content']
    
    assert 'id' in schema
    assert 'name' in schema
    assert 'created' in schema
    assert 'updated' in schema
    
    assert schema['id']['primary_key'] is True
    assert schema['name']['type'] == 'VARCHAR'

def test_from_data_object(db_handler):
    data = [
        {'name': 'bulk1'},
        {'name': 'bulk2'}
    ]
    
    response = db_handler.from_data_object(data, 'test_table', overwrite=True)
    assert response['status'] == 'success'
    
    # Verify data was imported
    read_response = db_handler.read('test_table')
    assert len(read_response['content']) == 2
    names = [record['name'] for record in read_response['content']]
    assert 'bulk1' in names
    assert 'bulk2' in names

def test_error_handling(db_handler):
    # Test invalid table name
    response = db_handler.read('nonexistent_table')
    assert response['status'] == 'error'
    assert 'Database error' in response['content']
    
    # Test invalid column name in filter
    response = db_handler.read('test_table', {'nonexistent_column': 'value'})
    assert response['status'] == 'success'  # Should ignore invalid column
    
    # Test invalid data type
    response = db_handler.from_data_object("not a list", 'test_table')
    assert response['status'] == 'error'
    assert 'Data must be a list of dictionaries' in response['content'] 