import pytest
import mysql.connector


@pytest.fixture(scope="session")
def db():
    return mysql.connector.connect(
        user='test_db',
        password='test_db',
        host='127.0.0.1',
        database='test_db')
