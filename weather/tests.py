from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class SignalTest(TestCase):
    """Check: making a new user automatically creates an OTPCode for them."""

    def test_creating_a_user_auto_creates_an_otpcode(self):
        user = User.objects.create_user(username="testuser", password="pw123456")
        self.assertTrue(hasattr(user, "otp"))     # an OTPCode got attached
        self.assertIsNotNone(user.otp.secret)     # and it has a secret


class OTPModelTest(TestCase):
    """Check: the OTP code we generate actually verifies correctly."""

    def test_a_freshly_generated_code_is_valid(self):
        user = User.objects.create_user(username="otpuser", password="pw123456")
        code = user.otp.generate_otp()            # make a code
        self.assertTrue(user.otp.verify_otp(code))  # the same code should pass

    def test_a_wrong_code_is_rejected(self):
        user = User.objects.create_user(username="otpuser2", password="pw123456")
        self.assertFalse(user.otp.verify_otp("000000"))  # a bad code should fail


class DashboardViewTest(TestCase):
    """Check: the dashboard page opens without crashing."""

    def test_dashboard_page_loads(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)   # 200 = page loaded OK
