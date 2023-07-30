from datetime import datetime
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import OperationCategory, OperationType, ClubTreasury
from users.models import UserPositions

class OperationCategoryTest(TestCase):
    
    def setUp(self):
        User = get_user_model()

        # Authentication of user_member
        self.client_user_member = Client()
        username_member = "testuser_member"
        password_member = "testpassword_member"
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

        # Authentication of user_head
        self.client_user_head = Client()
        username_head = "testuser_head"
        password_head = "testpassword_head"
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

        # Authentication of accountant
        self.client_user_accountant = Client()
        username_accountant = "testuser_accountant"
        password_accountant = "testpassword_accountant"
        self.user_accountant = User.objects.create_user(username=username_accountant, password=password_accountant)
        self.client_user_accountant.force_login(self.user_accountant)

        position_name_accountant = "Accountant"
        position_accountant, created = UserPositions.objects.get_or_create(positions_category=position_name_accountant)
        self.user_accountant.profile.user_position.add(position_accountant)

        # Creating an instance of the OperationCategory class 
        current_operation_category = OperationCategory.objects.create(category_name="Category_1", category_info="Test_info_category")
        current_operation_type = OperationType.objects.create(type_name="Type_1", type_info="Test_info_type")
        accounting_record = ClubTreasury.objects.create(
            amount=100,
            operation_date_time=datetime.now(),
            info="Test_info_accounting_record",
            performed_by=self.user_member,
            operation_category=current_operation_category,
            operation_type=current_operation_type,
        )



    # @unittest.skip
    def test_add_club_treasury(self):
        pass


    # @unittest.skip
    def test_get_club_treasury(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:get_club_treasury'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:get_club_treasury'))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "accounting/get_club_treasury.html")

        # Check the existence of accounting record
        accounting_record = ClubTreasury.objects.get(info="Test_info_accounting_record")
        self.assertIsNotNone(accounting_record)
        self.assertEqual(accounting_record.amount, 100)

        # "Checking an authenticated user
        self.assertEqual(response_member.context['user'], self.user_member)




    @unittest.skip
    def test_chenge_club_treasury(self):
        pass


    @unittest.skip
    def test_permissions_checker(self):
        pass


    @unittest.skip
    def test_add_operation_category(self):
        pass


    # @unittest.skip
    def test_get_operation_category(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:get_operation_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_category/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:get_operation_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:get_operation_category'))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/get_operation_category.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:get_operation_category'))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/get_operation_category.html")

        # Check the existence of operation category
        operation_category_record = OperationCategory.objects.get(category_name="Category_1")
        self.assertIsNotNone(operation_category_record)
        self.assertEqual(operation_category_record.category_info, "Test_info_category")


    @unittest.skip
    def test_chenge_operation_category(self):
        pass


    @unittest.skip
    def test_delete_operation_category(self):
        pass


    @unittest.skip
    def test_add_operation_type(self):
        pass


    # @unittest.skip
    def test_get_operation_type(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:get_operation_type'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_type/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:get_operation_type'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:get_operation_type'))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/get_operation_types.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:get_operation_type'))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/get_operation_types.html")

        # Check the existence of operation type
        operation_type_record = OperationType.objects.get(type_name="Type_1")
        self.assertIsNotNone(operation_type_record)
        self.assertEqual(operation_type_record.type_info, "Test_info_type")


    @unittest.skip
    def test_chenge_operation_type(self):
        pass


    @unittest.skip
    def test_delete_operation_type(self):
        pass










