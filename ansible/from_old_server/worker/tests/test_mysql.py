import mysql.connector
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


@pytest.fixture
def conn():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        database="covid_internet_controls",
    )

    yield conn
    conn.close()


def test_mysql_is_connected(conn):
    """Assert we have a valid connection."""
    assert conn.is_connected()


def test_show_databases(conn):
    """Assert that our database is present."""
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")

    found = False
    for databases in cursor:
        if databases[0] == "covid_internet_controls":
            found = True

    assert found


def test_insert(conn):
    """Assert that we can add, update, and delete."""

    # first add a test country
    cursor = conn.cursor()
    sql = "INSERT IGNORE INTO countries VALUES (%s, %s, %s)"
    val = ("ts", "test country", "test continent")
    cursor.execute(sql, val)
    conn.commit()

    # assure that it was inserted properly
    sql = "SELECT * FROM countries WHERE country_code = 'ts'"
    cursor.execute(sql)
    cursor.fetchall()
    assert cursor.rowcount == 1

    # delete the entry
    sql = "DELETE FROM countries WHERE country_code = 'ts'"
    cursor.execute(sql)
    conn.commit()

    # ensure it was actually deleted
    sql = "SELECT * FROM countries WHERE country_code = 'ts'"
    cursor.execute(sql)
    cursor.fetchall()
    assert cursor.rowcount == 0
