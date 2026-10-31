"""
Comprehensive Authentication & Identity Verification Suite for Raahi.
Tests registration, duplicate protection, password policies, salted bcrypt hashing,
JWT token lifecycle, HttpOnly cookies, protected endpoints, and password reset.
"""
import unittest
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.mongodb.connection import get_sync_db
from backend.auth.security import verify_password


class TestRaahiAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = get_sync_db()
        cls.test_email = f"test_{uuid.uuid4().hex[:8]}@raahi.in"
        cls.test_password = "SecurePassword2026!"
        cls.test_name = "Kavita Rao"

    def test_01_signup_success(self):
        """Verify successful user registration and MongoDB persistence."""
        payload = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        }
        res = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()

        self.assertIn("user", data)
        self.assertIn("token", data)
        user = data["user"]
        self.assertEqual(user["email"], self.test_email.lower())
        self.assertEqual(user["name"], self.test_name)
        # Ensure password hash is NEVER leaked in API responses
        self.assertNotIn("password", user)
        self.assertNotIn("password_hash", user)

        # Check session cookie
        self.assertIn("raahi_session", res.cookies)

        # Verify MongoDB persistence directly
        doc = self.db.users.find_one({"_id": user["id"]})
        self.assertIsNotNone(doc)
        self.assertEqual(doc["email_normalized"], self.test_email.lower())
        # Verify stored password is a valid bcrypt hash
        self.assertTrue(doc["password_hash"].startswith("$2b$"))
        self.assertTrue(verify_password(self.test_password, doc["password_hash"]))
        print("[PASS] User registration & bcrypt MongoDB storage verified")

    def test_02_signup_duplicate_email(self):
        """Verify duplicate email registration is rejected with 409 Conflict."""
        payload = {
            "name": "Duplicate User",
            "email": self.test_email.upper(),  # Test case-insensitivity
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
        res = self.client.post("/api/auth/signup", json=payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("already exists", res.json()["detail"].lower())
        print("[PASS] Duplicate email registration rejected (409)")

    def test_03_signup_weak_password(self):
        """Verify weak passwords lacking digits or short length are rejected."""
        # Too short (< 8 chars)
        res1 = self.client.post("/api/auth/signup", json={
            "name": "Short Pass",
            "email": f"short_{uuid.uuid4().hex[:6]}@raahi.in",
            "password": "pass1",
            "confirm_password": "pass1"
        })
        self.assertEqual(res1.status_code, 422)

        # No digits
        res2 = self.client.post("/api/auth/signup", json={
            "name": "No Digit",
            "email": f"nodigit_{uuid.uuid4().hex[:6]}@raahi.in",
            "password": "onlylettersandnosymbols",
            "confirm_password": "onlylettersandnosymbols"
        })
        self.assertEqual(res2.status_code, 422)
        print("[PASS] Password policy enforcement verified (422)")

    def test_04_signup_mismatched_password(self):
        """Verify mismatched password confirmation is rejected."""
        res = self.client.post("/api/auth/signup", json={
            "name": "Mismatch Pass",
            "email": f"mismatch_{uuid.uuid4().hex[:6]}@raahi.in",
            "password": "ValidPassword123",
            "confirm_password": "DifferentPassword123"
        })
        self.assertEqual(res.status_code, 422)
        print("[PASS] Mismatched password rejected (422)")

    def test_05_signin_success(self):
        """Verify user authentication with correct credentials."""
        payload = {
            "email": self.test_email,
            "password": self.test_password,
            "remember_me": True
        }
        res = self.client.post("/api/auth/signin", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["name"], self.test_name)
        self.assertIn("raahi_session", res.cookies)
        print("[PASS] User sign in successful (200)")

    def test_06_signin_invalid_password(self):
        """Verify sign in with wrong password returns 401 without detail leakage."""
        payload = {
            "email": self.test_email,
            "password": "IncorrectPassword999!"
        }
        res = self.client.post("/api/auth/signin", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("invalid email or password", res.json()["detail"].lower())
        print("[PASS] Invalid password rejected with generic 401")

    def test_07_signin_nonexistent_email(self):
        """Verify non-existent email returns generic 401 (prevent enumeration)."""
        payload = {
            "email": "ghost_commuter_does_not_exist@raahi.in",
            "password": "AnyPassword123!"
        }
        res = self.client.post("/api/auth/signin", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("invalid email or password", res.json()["detail"].lower())
        print("[PASS] Non-existent email returns identical 401")

    def test_08_me_endpoint_with_bearer(self):
        """Verify /api/auth/me resolves current user via Authorization header."""
        signin_res = self.client.post("/api/auth/signin", json={
            "email": self.test_email,
            "password": self.test_password
        })
        token = signin_res.json()["token"]

        res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], self.test_email.lower())
        print("[PASS] /api/auth/me verified via Bearer token")

    def test_09_me_endpoint_with_cookie(self):
        """Verify /api/auth/me resolves current user via HttpOnly cookie."""
        # Use a fresh test client to simulate browser session cookies
        session_client = TestClient(app)
        session_client.post("/api/auth/signin", json={
            "email": self.test_email,
            "password": self.test_password
        })
        res = session_client.get("/api/auth/me")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], self.test_email.lower())
        print("[PASS] /api/auth/me verified via session cookie")

    def test_10_me_endpoint_unauthorized(self):
        """Verify /api/auth/me returns 401 when no token or cookie provided."""
        unauthed_client = TestClient(app)
        res = unauthed_client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)
        print("[PASS] Unauthenticated access properly rejected (401)")

    def test_11_logout(self):
        """Verify logout clears session cookie."""
        session_client = TestClient(app)
        session_client.post("/api/auth/signin", json={
            "email": self.test_email,
            "password": self.test_password
        })
        logout_res = session_client.post("/api/auth/logout")
        self.assertEqual(logout_res.status_code, 200)
        # Verify subsequent /me is unauthorized
        me_res = session_client.get("/api/auth/me")
        self.assertEqual(me_res.status_code, 401)
        print("[PASS] Logout clears session & prevents subsequent access")

    def test_12_forgot_and_reset_password(self):
        """Verify complete password recovery lifecycle."""
        # Step 1: Request reset
        forgot_res = self.client.post("/api/auth/forgot-password", json={
            "email": self.test_email
        })
        self.assertEqual(forgot_res.status_code, 200)
        data = forgot_res.json()
        token = data.get("demo_reset_token")
        self.assertIsNotNone(token, "Reset token should be provided in dev/test environment")

        # Step 2: Reset password with token
        new_pass = "NewAwesomePassword2026!"
        reset_res = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": new_pass,
            "confirm_password": new_pass
        })
        self.assertEqual(reset_res.status_code, 200)

        # Step 3: Sign in with old password (must fail)
        old_login = self.client.post("/api/auth/signin", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(old_login.status_code, 401)

        # Step 4: Sign in with new password (must succeed)
        new_login = self.client.post("/api/auth/signin", json={
            "email": self.test_email,
            "password": new_pass
        })
        self.assertEqual(new_login.status_code, 200)
        print("[PASS] Complete password recovery & reset flow verified")


if __name__ == "__main__":
    unittest.main()

