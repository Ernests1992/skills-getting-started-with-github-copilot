import copy
from urllib.parse import quote

from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def reset_activity_state():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)


def setup_function():
    reset_activity_state()


def teardown_function():
    reset_activity_state()


def test_root_redirects_to_static_index():
    # Arrange
    # Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_activity_data():
    # Arrange
    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = quote("Chess Club", safe="")

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    email = "emma@mergington.edu"
    activity = quote("Programming Class", safe="")

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_removes_entry():
    # Arrange
    email = "olivia@mergington.edu"
    activity = quote("Gym Class", safe="")

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Gym Class"
    assert email not in client.get("/activities").json()["Gym Class"]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    email = "notfound@mergington.edu"
    activity = quote("Chess Club", safe="")

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
