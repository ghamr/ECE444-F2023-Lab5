import pytest
from pathlib import Path
from project.app import app, db

import json

TEST_DB = "test.db"


@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)


def test_index(client):
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200


def test_database(client):
    """initial test. ensure that the database exists"""
    tester = Path("test.db").is_file()
    assert tester


def test_empty_db(client):
    """Ensure database is blank"""
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data


def test_login_logout(client):
    """Test login and logout using helper functions"""
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Invalid username" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Invalid password" in rv.data


def test_delete_message(client):
    """Ensure the messages are being deleted"""
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1


def test_messages(client):
    """Ensure that user can post messages"""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"No entries here so far" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


"""
first, login with login()
then add a post by asking the client to change the data of the element named "title" to something, and the element named "text" to something else
follow redirects?
now have the client get the results of a search query,
usually search queries are done by adding a ?query=whatever to the end of the html link
we do the above manually
search for an example that is in the db
search for an example that is not in the db
"""


# def test_search(client):
#     """Ensure that the client can search for something and get results"""
#     login(client, app.config["USERNAME"], app.config["PASSWORD"])
#     rv = client.post(
#         "/add",
#         data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
#         follow_redirects=True,
#     )
#     rv2 = client.get("/search/?query=allow")
#     assert b'example1' not in rv2.data
#     assert b'allowed here' in rv2.data
# @login_required
# def test_helper():
#     return jsonify({'status': -1, 'message': 'you are logged in.'})
# def test_login_required(client):
#    @login_required
#     def test_helper():
#         return jsonify({'status': -1, 'message': 'you are logged in.'})
#     rv=client.get("/login_required_test")
#     assert rv.status_code == 401
#     assert rv.message == 'Please log in.'
#     login(client, app.config["USERNAME"], app.config["PASSWORD"])
#     assert rv.get_json.message == 'you are logged in.'
