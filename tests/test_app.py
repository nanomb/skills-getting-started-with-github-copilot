"""
Test suite for the Mergington High School Activities API.
Tests the API endpoints for viewing and managing activity signups.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to the static index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    assert "index.html" in response.url

def test_get_activities():
    """Test retrieving the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Verify response structure
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check a specific activity for required fields
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    test_email = "test_student@mergington.edu"
    
    # First ensure the test email is not already registered
    response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    # Verify the response message
    result = response.json()
    assert "message" in result
    assert test_email in result["message"]
    assert activity_name in result["message"]
    
    # Verify the student was actually added
    activities = client.get("/activities").json()
    assert test_email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    activity_name = "Chess Club"
    test_email = "test_student@mergington.edu"
    
    # First sign up the student
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    
    # Verify error message
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"].lower()

def test_unregister_success():
    """Test successfully unregistering from an activity"""
    activity_name = "Chess Club"
    test_email = "test_student@mergington.edu"
    
    # First sign up the student
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Try to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    # Verify the response message
    result = response.json()
    assert "message" in result
    assert test_email in result["message"]
    assert activity_name in result["message"]
    
    # Verify the student was actually removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    activity_name = "Chess Club"
    test_email = "nonexistent@mergington.edu"
    
    # Try to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not registered" in result["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"].lower()