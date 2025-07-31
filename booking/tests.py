import datetime

from django.test import TestCase, Client as DjangoClient
from django.urls import reverse
from django.contrib.auth.models import User

from booking.models import Shop, Client, Appointment, DAYS_OF_WEEK
from booking.forms import AppointmentForm, ShopRegisterForm


class BookingAppTest(TestCase):
    # -------------------------------------------------------------------------
    # Model tests
    # -------------------------------------------------------------------------
    def test_days_of_week_choices(self):
        self.assertEqual(len(DAYS_OF_WEEK), 7)
        for code, label in DAYS_OF_WEEK:
            self.assertIsInstance(code, str)
            self.assertIsInstance(label, str)

    def test_shop_str_and_defaults(self):
        owner = User.objects.create_user("u1", "u1@example.com", "pass")
        shop = Shop.objects.create(
            owner=owner,
            name="Test Shop",
            address="123 Main",
            opening_hours=datetime.time(8, 0),
            closing_hours=datetime.time(17, 0),
            opening_day="mon",
            closing_day="fri"
        )
        self.assertEqual(str(shop), "Test Shop")

    def test_client_and_appointment_str(self):
        client = Client.objects.create(name="Alice", email="a@a.com", phone="555")
        owner = User.objects.create_user("u2", "u2@example.com", "pass")
        shop = Shop.objects.create(
            owner=owner,
            name="Test Shop 2",
            address="456 Elm",
            opening_hours=datetime.time(9, 0),
            closing_hours=datetime.time(18, 0),
            opening_day="tue",
            closing_day="sat"
        )
        appt = Appointment.objects.create(
            client=client,
            shop=shop,
            start_time=datetime.datetime(2025, 8, 1, 10, 0),
            duration=datetime.timedelta(minutes=45),
            note="Checkup"
        )
        self.assertIn("Alice", str(appt))
        self.assertIn("2025-08-01 10:00", str(appt))

    # -------------------------------------------------------------------------
    # Form tests
    # -------------------------------------------------------------------------
    def setUp(self):
        # shared shop for form & view tests
        self.shop = Shop.objects.create(
            owner=User.objects.create_user("u3", "u3@example.com", "pass"),
            name="Form/View Shop",
            address="789 Oak",
            opening_hours=datetime.time(9, 0),
            closing_hours=datetime.time(17, 0),
            opening_day="mon",
            closing_day="fri"
        )
        self.client = DjangoClient()

    def test_valid_appointment_form_without_shop(self):
        data = {
            "name": "Bob",
            "email": "b@b.com",
            "phone": "123",
            "start_time": "2025-08-04T10:00",  # Monday
            "duration": 30,
            "note": "No shop"
        }
        form = AppointmentForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_day_outside_opening(self):
        sunday = datetime.datetime(2025, 8, 3, 10, 0)
        data = {
            "name": "Bob",
            "email": "b@b.com",
            "phone": "123",
            "shop": self.shop.id,
            "start_time": sunday.strftime("%Y-%m-%dT%H:%M"),
            "duration": 30,
            "note": ""
        }
        form = AppointmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("closed on that day", form.errors["__all__"][0])

    def test_invalid_time_outside_hours(self):
        early = datetime.datetime(2025, 8, 4, 8, 0)
        data = {
            "name": "Bob",
            "email": "b@b.com",
            "phone": "123",
            "shop": self.shop.id,
            "start_time": early.strftime("%Y-%m-%dT%H:%M"),
            "duration": 45,
            "note": ""
        }
        form = AppointmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("closed at that time", form.errors["__all__"][0])

    def test_shop_register_form_creates_user_and_shop(self):
        form_data = {
            "username": "newshop",
            "password1": "complexpass123",
            "password2": "complexpass123",
            "shop_name": "My Shop",
            "opening_hours": "08:00",
            "closing_hours": "16:00",
            "address": "111 Pine",
            "opening_day": DAYS_OF_WEEK[0][0],
            "closing_day": DAYS_OF_WEEK[4][0],
        }
        form = ShopRegisterForm(form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(hasattr(user, "shop"))
        self.assertEqual(user.shop.name, "My Shop")

    # -------------------------------------------------------------------------
    # View tests
    # -------------------------------------------------------------------------
    def test_get_schedule_page(self):
        resp = self.client.get(reverse("booking:schedule"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<form")

    def test_post_valid_appointment_creates_client_and_appt(self):
        data = {
            "name": "Zed",
            "email": "z@z.com",
            "phone": "999",
            "shop": self.shop.id,
            "start_time": "2025-08-04T11:00",
            "duration": 45,
            "note": "Test note"
        }
        resp = self.client.post(reverse("booking:schedule"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "confirm.html")
        # the confirmation page includes this static message:
        self.assertContains(resp, "Your appointment has been scheduled.")
        # and the DB should have the new client and appointment
        self.assertTrue(Client.objects.filter(email="z@z.com").exists())
        self.assertTrue(Appointment.objects.filter(client__email="z@z.com").exists())

    def test_post_missing_name_shows_error(self):
        data = {
            "name": "",
            "email": "e@e.com",
            "phone": "123",
            "start_time": "2025-08-04T11:00",
            "duration": 30,
            "note": ""
        }
        resp = self.client.post(reverse("booking:schedule"), data)
        self.assertEqual(resp.status_code, 200)
        # check that the form error appears on page
        self.assertContains(resp, "This field is required.")


        # Some edge cases to consider for more test cases
            
    def test_appointment_ends_after_closing(self):
        data = {
            "name": "Late Client",
            "email": "late@example.com",
            "phone": "111",
            "shop": self.shop.id,
            "start_time": "2025-08-04T16:45",  # Shop closes at 17:00
            "duration": 30,
            "note": "Too late"
        }
        form = AppointmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("closed at that time", form.errors["__all__"][0])

    def test_appointment_invalid_email_format(self):
        data = {
            "name": "Bad Email",
            "email": "not-an-email",
            "phone": "123",
            "shop": self.shop.id,
            "start_time": "2025-08-04T10:00",
            "duration": 30,
            "note": "Invalid email"
        }
        form = AppointmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_shop_register_duplicate_username(self):
        User.objects.create_user(username="dupeuser", password="pass")
        form_data = {
            "username": "dupeuser",
            "password1": "complexpass123",
            "password2": "complexpass123",
            "shop_name": "New Shop",
            "opening_hours": "08:00",
            "closing_hours": "16:00",
            "address": "100 New Rd",
            "opening_day": "mon",
            "closing_day": "fri"
        }
        form = ShopRegisterForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_shop_register_password_mismatch(self):
        form_data = {
            "username": "testuser",
            "password1": "abc123",
            "password2": "xyz123",
            "shop_name": "Mismatch Shop",
            "opening_hours": "08:00",
            "closing_hours": "16:00",
            "address": "222 Wrong Rd",
            "opening_day": "mon",
            "closing_day": "fri"
        }
        form = ShopRegisterForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_post_invalid_shop_id(self):
        data = {
            "name": "Ghost Shop",
            "email": "ghost@example.com",
            "phone": "000",
            "shop": 9999,  # Non-existent ID
            "start_time": "2025-08-04T10:00",
            "duration": 30,
            "note": ""
        }
        resp = self.client.post(reverse("booking:schedule"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Select a valid choice")

    def test_direct_access_confirm_page(self):
        resp = self.client.get(reverse("booking:confirm"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "confirmation")  