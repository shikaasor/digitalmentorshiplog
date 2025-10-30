"""
Facility Endpoint Tests

Tests for facility CRUD operations and filtering.
"""

import pytest

from app.models import UserRole
from tests.helpers import (
    create_test_user, create_test_facility,
    get_auth_headers, assert_success, assert_forbidden,
    assert_not_found
)


@pytest.mark.integration
class TestListFacilities:
    """Tests for listing facilities"""

    def test_list_all_facilities(self, client, db_session):
        """Test listing all facilities"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        # Create test facilities
        create_test_facility(db_session, code="FAC1", name="Kano General Hospital", state="Kano", lga="Kano Municipal")
        create_test_facility(db_session, code="FAC2", name="Jigawa Specialist Hospital", state="Jigawa", lga="Dutse")
        create_test_facility(db_session, code="FAC3", name="Bauchi Medical Center", state="Bauchi", lga="Bauchi")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/facilities", headers=headers)
        data = assert_success(response)

        assert len(data) >= 3
        assert any(f["code"] == "FAC1" for f in data)

    def test_filter_by_state(self, client, db_session):
        """Test filtering facilities by state"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        create_test_facility(db_session, code="FAC1", name="Kano Hospital", state="Kano", lga="Kano Municipal")
        create_test_facility(db_session, code="FAC2", name="Jigawa Hospital", state="Jigawa", lga="Dutse")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/facilities?state=Kano", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert all(f["state"] == "Kano" for f in data)

    def test_filter_by_lga(self, client, db_session):
        """Test filtering facilities by LGA"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        create_test_facility(db_session, code="FAC1", name="Municipal Hospital", state="Kano", lga="Kano Municipal")
        create_test_facility(db_session, code="FAC2", name="Gwale Clinic", state="Kano", lga="Gwale")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/facilities?lga=Gwale", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert all(f["lga"] == "Gwale" for f in data)

    def test_search_by_name(self, client, db_session):
        """Test searching facilities by name"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        create_test_facility(db_session, code="FAC1", name="Kano General Hospital", state="Kano", lga="Kano Municipal")
        create_test_facility(db_session, code="FAC2", name="Specialist Clinic", state="Kano", lga="Gwale")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/facilities?search=General", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert any("General" in f["name"] for f in data)

    def test_search_by_code(self, client, db_session):
        """Test searching facilities by code"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        create_test_facility(db_session, code="KN001", name="Kano Hospital", state="Kano", lga="Kano Municipal")
        create_test_facility(db_session, code="JG001", name="Jigawa Hospital", state="Jigawa", lga="Dutse")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/facilities?search=KN001", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert data[0]["code"] == "KN001"

    def test_pagination(self, client, db_session):
        """Test pagination parameters"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        # Create multiple facilities
        for i in range(5):
            create_test_facility(db_session, code=f"FAC{i}", name=f"Facility {i}", state="Kano", lga="Kano Municipal")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        # Test limit
        response = client.get("/api/facilities?limit=2", headers=headers)
        data = assert_success(response)
        assert len(data) <= 2

        # Test skip
        response = client.get("/api/facilities?skip=2&limit=2", headers=headers)
        data = assert_success(response)
        assert len(data) <= 2

    def test_list_without_auth(self, client, db_session):
        """Test that listing facilities requires authentication"""
        response = client.get("/api/facilities")
        assert_forbidden(response)


@pytest.mark.integration
class TestGetFacility:
    """Tests for getting a single facility"""

    def test_get_facility_success(self, client, db_session):
        """Test getting a single facility"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session, code="FAC1", name="Test Hospital")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/facilities/{facility.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(facility.id)
        assert data["code"] == "FAC1"
        assert data["name"] == "Test Hospital"

    def test_get_nonexistent_facility(self, client, db_session):
        """Test getting a facility that doesn't exist"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        response = client.get(f"/api/facilities/{fake_id}", headers=headers)
        assert_not_found(response)

    def test_get_facility_without_auth(self, client, db_session):
        """Test that getting a facility requires authentication"""
        facility = create_test_facility(db_session)

        response = client.get(f"/api/facilities/{facility.id}")
        assert_forbidden(response)


@pytest.mark.integration
class TestCreateFacility:
    """Tests for creating facilities"""

    def test_create_facility_as_admin(self, client, db_session):
        """Test that admins can create facilities"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        facility_data = {
            "code": "NEW001",
            "name": "New Hospital",
            "state": "Kano",
            "lga": "Kano Municipal",
            "facility_type": "Hospital",
            "location": "123 Main Street"
        }

        response = client.post("/api/facilities", json=facility_data, headers=headers)
        data = assert_success(response, 201)

        assert data["code"] == "NEW001"
        assert data["name"] == "New Hospital"
        assert data["state"] == "Kano"

    def test_create_facility_duplicate_code(self, client, db_session):
        """Test that duplicate facility codes are rejected"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        create_test_facility(db_session, code="DUP001")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        facility_data = {
            "code": "DUP001",
            "name": "Duplicate Hospital",
            "state": "Kano",
            "lga": "Kano Municipal"
        }

        response = client.post("/api/facilities", json=facility_data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_facility_as_supervisor(self, client, db_session):
        """Test that supervisors cannot create facilities"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        facility_data = {
            "code": "NEW001",
            "name": "New Hospital",
            "state": "Kano",
            "lga": "Kano Municipal"
        }

        response = client.post("/api/facilities", json=facility_data, headers=headers)
        assert_forbidden(response)

    def test_create_facility_as_mentor(self, client, db_session):
        """Test that mentors cannot create facilities"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        facility_data = {
            "code": "NEW001",
            "name": "New Hospital",
            "state": "Kano",
            "lga": "Kano Municipal"
        }

        response = client.post("/api/facilities", json=facility_data, headers=headers)
        assert_forbidden(response)

    def test_create_facility_without_auth(self, client, db_session):
        """Test that creating facilities requires authentication"""
        facility_data = {
            "code": "NEW001",
            "name": "New Hospital",
            "state": "Kano",
            "lga": "Kano Municipal"
        }

        response = client.post("/api/facilities", json=facility_data)
        assert_forbidden(response)


@pytest.mark.integration
class TestUpdateFacility:
    """Tests for updating facilities"""

    def test_update_facility_as_admin(self, client, db_session):
        """Test that admins can update facilities"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session, code="FAC1", name="Old Name")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {
            "name": "Updated Name",
            "location": "New Location"
        }

        response = client.put(f"/api/facilities/{facility.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["name"] == "Updated Name"
        assert data["location"] == "New Location"
        assert data["code"] == "FAC1"  # Code unchanged

    def test_update_facility_code(self, client, db_session):
        """Test updating facility code"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session, code="OLD001")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {"code": "NEW001"}

        response = client.put(f"/api/facilities/{facility.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["code"] == "NEW001"

    def test_update_facility_duplicate_code(self, client, db_session):
        """Test that updating to duplicate code is rejected"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility1 = create_test_facility(db_session, code="FAC1")
        facility2 = create_test_facility(db_session, code="FAC2")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {"code": "FAC1"}  # Try to use existing code

        response = client.put(f"/api/facilities/{facility2.id}", json=update_data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_nonexistent_facility(self, client, db_session):
        """Test updating a facility that doesn't exist"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/facilities/{fake_id}", json=update_data, headers=headers)
        assert_not_found(response)

    def test_update_facility_as_supervisor(self, client, db_session):
        """Test that supervisors cannot update facilities"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session, code="FAC1")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/facilities/{facility.id}", json=update_data, headers=headers)
        assert_forbidden(response)

    def test_update_facility_as_mentor(self, client, db_session):
        """Test that mentors cannot update facilities"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session, code="FAC1")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/facilities/{facility.id}", json=update_data, headers=headers)
        assert_forbidden(response)


@pytest.mark.integration
class TestDeleteFacility:
    """Tests for deleting facilities"""

    def test_delete_facility_as_admin(self, client, db_session):
        """Test that admins can delete facilities"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session, code="FAC1")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/facilities/{facility.id}", headers=headers)
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/facilities/{facility.id}", headers=headers)
        assert_not_found(response)

    def test_delete_facility_with_logs(self, client, db_session):
        """Test that facilities with mentorship logs cannot be deleted"""
        from tests.helpers import create_test_mentorship_log

        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session, code="FAC1")

        # Create a mentorship log for this facility
        create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/facilities/{facility.id}", headers=headers)
        assert response.status_code == 400
        assert "mentorship logs" in response.json()["detail"]

    def test_delete_nonexistent_facility(self, client, db_session):
        """Test deleting a facility that doesn't exist"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        response = client.delete(f"/api/facilities/{fake_id}", headers=headers)
        assert_not_found(response)

    def test_delete_facility_as_supervisor(self, client, db_session):
        """Test that supervisors cannot delete facilities"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session, code="FAC1")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/facilities/{facility.id}", headers=headers)
        assert_forbidden(response)

    def test_delete_facility_as_mentor(self, client, db_session):
        """Test that mentors cannot delete facilities"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session, code="FAC1")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/facilities/{facility.id}", headers=headers)
        assert_forbidden(response)
