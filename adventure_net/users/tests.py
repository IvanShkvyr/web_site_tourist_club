from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from users.models import UserPositions
from adventure_net.messages import MSG_USER_DATA_ADDED


class UsersViewsTest(TestCase):
    def setUp(self):
        User = get_user_model()

        # user_member Authentication
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

        # user_head authentication
        self.client_user_head = Client()
        username_head = 'testuser_Head'
        password_head = 'testpassword_Head'
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

    def test_signup_user(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/signup/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/signup/')

        # Check access for an authorized user 'user_head'
        response_head = self.client_user_head.get(reverse('users:signup'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "users/signup.html")

        new_record = {
            "username": "test_user_name",
            "password1": "test_password",
            "password2": "test_password",
        }

        # Creating new instance User, and checking it
        amount_users_records_instance = User.objects.count()
        new_reverse = reverse("users:signup")
        response_add_record_norm = self.client_user_head.post(new_reverse, new_record)
        self.assertEqual(User.objects.count(), amount_users_records_instance + 1)
        self.assertEqual(response_add_record_norm.status_code, 302)
        self.assertRedirects(response_add_record_norm, reverse("users:main"))

        # Checking user records values
        new_user_records = User.objects.get(username="test_user_name")
        self.assertEqual(new_user_records.username, "test_user_name")

        storage = get_messages(response_add_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_USER_DATA_ADDED, messages)

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'username' field
        record_less_char = {
            "username": "te",
            "password1": "test_password",
            "password2": "test_password",
        }
        amount_users_records_instance_2 = User.objects.count()
        response_wrong_less_name = self.client_user_head.post(new_reverse, record_less_char)
        self.assertEqual(User.objects.count(), amount_users_records_instance_2)
        self.assertEqual(response_wrong_less_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_name, "users/signup.html")

        # Attempt to add an instance of the class with data containing a character count more
        # than the maximum value in the 'username' field
        long_name = "x" * 31
        record_more_char = {
            "username": long_name,
            "password1": "test_password",
            "password2": "test_password",
        }
        amount_users_records_instance_3 = User.objects.count()
        response_wrong_big_name = self.client_user_head.post(new_reverse, record_more_char)
        self.assertEqual(User.objects.count(), amount_users_records_instance_3)
        self.assertEqual(response_wrong_big_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_big_name, "users/signup.html")

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'password' field
        record_less_password = {
            "username": "normal_name",
            "password1": "test",
            "password2": "test",
        }
        amount_users_records_instance_4 = User.objects.count()
        response_wrong_less_password = self.client_user_head.post(new_reverse, record_less_password)
        self.assertEqual(User.objects.count(), amount_users_records_instance_4)
        self.assertEqual(response_wrong_less_password.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_password, "users/signup.html")

        # Attempt to add an instance of the class with data containing a character count more
        # than the maximum value in the 'password' field
        long_password = "x" * 31
        record_more_password = {
            "username": "normal_name",
            "password1": long_password,
            "password2": long_password,
        }
        amount_users_records_instance_5 = User.objects.count()
        response_wrong_big_password = self.client_user_head.post(new_reverse, record_more_password)
        self.assertEqual(User.objects.count(), amount_users_records_instance_5)
        self.assertEqual(response_wrong_big_password.status_code, 200)
        self.assertTemplateUsed(response_wrong_big_password, "users/signup.html")

        # Attempting to add an instance of a class with incorrect passwords.
        record_more_password = {
            "username": "normal_name",
            "password1": "normal_password_1",
            "password2": "normal_password_2",
        }
        amount_users_records_instance_6 = User.objects.count()
        response_wrong_password = self.client_user_head.post(new_reverse, record_more_password)
        self.assertEqual(User.objects.count(), amount_users_records_instance_6)
        self.assertEqual(response_wrong_password.status_code, 200)
        self.assertTemplateUsed(response_wrong_password, "users/signup.html")

        # дублюються імена

        # Attempting to add an instance of a class with an already existing name
        duplication_record = {
            "username": "test_user_name",
            "password1": "test_password",
            "password2": "test_password",
        }
        amount_users_records_instance_7 = User.objects.count()
        response_duplication_record = self.client_user_head.post(new_reverse, duplication_record)
        self.assertEqual(User.objects.count(), amount_users_records_instance_7)
        self.assertEqual(response_duplication_record.status_code, 200)
        self.assertTemplateUsed(response_duplication_record, "users/signup.html")


# login_user

# logout_user

# recover_login_password

# reset_password

# password_reset_success

# profile_user

# get_users

# change_profile

# delete_profile

# get_user_position

# add_user_position

# change_user_position

# delete_user_position

# update_account_information

# permissions_signup_checker


