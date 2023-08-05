from datetime import datetime
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from .models import OperationCategory, OperationType, ClubTreasury
from users.models import UserPositions
from adventure_net.messages import MSG_TYPE_OPERATION_DELETE, MSG_TYPE_OPERATION_ADDED, \
    MSG_CAT_OPERATION_ADDED, MSG_AMOUNT_ADDED, MSG_TYPE_OPERATION_DELETE_ERR, \
    MSG_CAT_OPERATION_DELETE, MSG_CAT_OPERATION_DELETE_ERR, MSG_TYPE_OPERATION_UPDATED, \
    MSG_CAT_OPERATION_UPDATED, MSG_AMOUNT_UPDATED
from .views import permissions_checker

class AccountingRecordTest(TestCase):
    
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
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:add_club_treasury'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/add_club_treasury/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:add_club_treasury'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:add_club_treasury'))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/add_club_treasury.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:add_club_treasury'))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/add_club_treasury.html")

        # Creating a data of the ClubTreasury class 
        selected_operation_category = OperationCategory.objects.get(category_name="Category_1")
        selected_operation_type = OperationType.objects.get(type_name="Type_1")
        performed_by_user = User.objects.get(username="testuser_accountant")

        new_accounting_record = {
            "amount": 102.0,
            "info": "test_add_club_treasury",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }

        # Creating new instance Club Treasury, and checking it
        amount_accounting_records_instance = ClubTreasury.objects.count()
        new_reverse = reverse("accounting:add_club_treasury")
        response_add_accounting_record_norm = self.client_user_accountant.post(new_reverse, new_accounting_record)
        self.assertEqual(ClubTreasury.objects.count(), amount_accounting_records_instance + 1)
        self.assertEqual(response_add_accounting_record_norm.status_code, 302)
        self.assertRedirects(response_add_accounting_record_norm, reverse("accounting:get_club_treasury"))

        new_accounting_records = ClubTreasury.objects.get(info="test_add_club_treasury")

        # Checking accounting records values
        self.assertEqual(new_accounting_records.amount, 102.0)  
        self.assertEqual(new_accounting_records.info, "test_add_club_treasury")
        self.assertEqual(new_accounting_records.performed_by, performed_by_user)
        self.assertEqual(new_accounting_records.operation_category, selected_operation_category)
        self.assertEqual(new_accounting_records.operation_type, selected_operation_type)

        storage = get_messages(response_add_accounting_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_AMOUNT_ADDED, messages)

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'info' field
        record_less_char = {
            "amount": 102.0,
            "info": "less",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        amount_instance_2 = ClubTreasury.objects.count()
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, record_less_char)
        self.assertEqual(ClubTreasury.objects.count(), amount_instance_2)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/add_club_treasury.html")

        # Attempt to add an instance of the class with data containing a character count more
        # than the maximum value in the 'info' field
        long_value = "x" * 51
        record_more_char = {
            "amount": 102.0,
            "info": long_value,
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        amount_instance_3 = ClubTreasury.objects.count()
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, record_more_char)
        self.assertEqual(ClubTreasury.objects.count(), amount_instance_3)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/add_club_treasury.html")

        # Attempt to add an instance of the class without data "performed_by"
        record_without_performed_by = {
            "amount": 102.0,
            "info": "test_add_club_treasury",
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        amount_instance_4 = ClubTreasury.objects.count()
        response_wrong_without_performed_by = self.client_user_accountant.post(new_reverse, record_without_performed_by)
        self.assertEqual(ClubTreasury.objects.count(), amount_instance_4)
        self.assertEqual(response_wrong_without_performed_by.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_performed_by, "accounting/add_club_treasury.html")

        # Attempt to add an instance of the class without data "operation_category"
        record_without_operation_category = {
            "amount": 102.0,
            "info": "test_add_club_treasury",
            "performed_by": performed_by_user.id,
            "operation_type": selected_operation_type.id,
        }
        amount_instance_5 = ClubTreasury.objects.count()
        response_wrong_without_operation_category = self.client_user_accountant.post(new_reverse, record_without_operation_category)
        self.assertEqual(ClubTreasury.objects.count(), amount_instance_5)
        self.assertEqual(response_wrong_without_operation_category.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_operation_category, "accounting/add_club_treasury.html")


        # Attempt to add an instance of the class without data "operation_type"
        record_without_operation_type = {
            "amount": 102.0,
            "info": "test_add_club_treasury",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
        }
        amount_instance_6 = ClubTreasury.objects.count()
        response_wrong_without_operation_type = self.client_user_accountant.post(new_reverse, record_without_operation_type)
        self.assertEqual(ClubTreasury.objects.count(), amount_instance_6)
        self.assertEqual(response_wrong_without_operation_type.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_operation_type, "accounting/add_club_treasury.html")

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

    # @unittest.skip
    def test_change_club_treasury(self):
        # Creating an instance of the OperationCategory class 
        new_operation_category = OperationCategory.objects.create(category_name="Cat_c", category_info="Test_info_category")
        new_operation_type = OperationType.objects.create(type_name="Type_c", type_info="Test_info_type")
        ClubTreasury.objects.create(
            amount=120,
            operation_date_time=datetime.now(),
            info="Test_accounting_record_for_changing",
            performed_by=self.user_member,
            operation_category=new_operation_category,
            operation_type=new_operation_type,
        )
        accounting_record = ClubTreasury.objects.get(info="Test_accounting_record_for_changing")
        new_reverse = reverse('accounting:change_club_treasury', args=[accounting_record.id])

        # Check access for an unauthorized user
        response = self.client.get(new_reverse)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/accounting/change_club_treasury/{accounting_record.id}/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(new_reverse)
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(new_reverse)
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/change_club_treasury.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(new_reverse)
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/change_club_treasury.html")

        # Creating a data of the ClubTreasury class 
        selected_operation_category = OperationCategory.objects.get(category_name="Category_1")
        selected_operation_type = OperationType.objects.get(type_name="Type_1")
        performed_by_user = User.objects.get(username="testuser_accountant")
        change_accounting_record = {
            "amount": 102.0,
            "info": "test_change_club_treasury",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }

        # Creating new instance Club Treasury, and checking it
        amount_accounting_records_instance = ClubTreasury.objects.count()
        response_change_accounting_record_norm = self.client_user_accountant.post(new_reverse, change_accounting_record)
        self.assertEqual(ClubTreasury.objects.count(), amount_accounting_records_instance)
        self.assertEqual(response_change_accounting_record_norm.status_code, 302)
        self.assertRedirects(response_change_accounting_record_norm, reverse("accounting:get_club_treasury"))
        new_accounting_records = ClubTreasury.objects.get(info="test_change_club_treasury")

        # Checking accounting records values
        self.assertEqual(new_accounting_records.amount, 102.0)  
        self.assertEqual(new_accounting_records.performed_by, performed_by_user)
        self.assertEqual(new_accounting_records.operation_category, selected_operation_category)
        self.assertEqual(new_accounting_records.operation_type, selected_operation_type)

        storage = get_messages(response_change_accounting_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_AMOUNT_UPDATED, messages)

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'info' field
        record_less_char = {
            "amount": 101.0,
            "info": "less",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, record_less_char)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/change_club_treasury.html")

        # Attempt to change an instance of the class with data containing a character count more
        # than the maximum value in the 'info' field
        long_value = "x" * 51
        record_more_char = {
            "amount": 102.0,
            "info": long_value,
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, record_more_char)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/change_club_treasury.html")

        # Attempt to change an instance of the class without data "performed_by"
        record_without_performed_by = {
            "amount": 102.0,
            "info": "test_change_club_treasury_2",
            "operation_category": selected_operation_category.id,
            "operation_type": selected_operation_type.id,
        }
        response_wrong_without_performed_by = self.client_user_accountant.post(new_reverse, record_without_performed_by)
        self.assertEqual(response_wrong_without_performed_by.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_performed_by, "accounting/change_club_treasury.html")

        # Attempt to change an instance of the class without data "operation_category"
        record_without_operation_category = {
            "amount": 102.0,
            "info": "test_change_club_treasury_2",
            "performed_by": performed_by_user.id,
            "operation_type": selected_operation_type.id,
        }
        response_wrong_without_operation_category = self.client_user_accountant.post(new_reverse, record_without_operation_category)
        self.assertEqual(response_wrong_without_operation_category.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_operation_category, "accounting/change_club_treasury.html")

        # Attempt to change an instance of the class without data "operation_type"
        record_without_operation_type = {
            "amount": 102.0,
            "info": "test_change_club_treasury_2",
            "performed_by": performed_by_user.id,
            "operation_category": selected_operation_category.id,
        }
        response_wrong_without_operation_type = self.client_user_accountant.post(new_reverse, record_without_operation_type)
        self.assertEqual(response_wrong_without_operation_type.status_code, 200)
        self.assertTemplateUsed(response_wrong_without_operation_type, "accounting/change_club_treasury.html")

    # @unittest.skip
    def test_permissions_checker(self):
        # Checking permissions_equipment_checker
        request_member = self.client_user_member.request().wsgi_request
        request_head = self.client_user_head.request().wsgi_request
        request_accountant = self.client_user_accountant.request().wsgi_request

        # Checking user_member
        has_permissions_member = permissions_checker(request_member)
        self.assertFalse(has_permissions_member)

        # Checking user_head
        has_permissions_head = permissions_checker(request_head)
        self.assertTrue(has_permissions_head)

        # Checking user_accountant
        has_permissions_accountant = permissions_checker(request_accountant)
        self.assertTrue(has_permissions_accountant)


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
        OperationCategory.objects.create(category_name="Category_1", category_info="Test_info_category")

    # @unittest.skip
    def test_add_operation_category(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:add_operation_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_category/add_opr_category/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:add_operation_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:add_operation_category'))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/add_operation_category.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:add_operation_category'))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/add_operation_category.html")

        # Creating a data of the OperationCategory class 
        data_new_operation_category = {
            "category_name":"Category_2",
            "category_info":"test_add_operation_category",
        }
        
        # Creating new instance OperationCategory, and checking it
        amount_category_records_instance = OperationCategory.objects.count()
        new_reverse = reverse("accounting:add_operation_category")
        response_add_category_record_norm = self.client_user_accountant.post(new_reverse, data_new_operation_category)
        self.assertEqual(OperationCategory.objects.count(), amount_category_records_instance + 1)
        self.assertEqual(response_add_category_record_norm.status_code, 302)
        self.assertRedirects(response_add_category_record_norm, reverse('accounting:get_club_treasury'))
        # Checking accounting records values
        new_category_records = OperationCategory.objects.get(category_name="Category_2")
        self.assertEqual(new_category_records.category_info, "test_add_operation_category")

        storage = get_messages(response_add_category_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_CAT_OPERATION_ADDED, messages)

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'category_name' field
        data_wrong_category_name_less = {
            "category_name":"Ca",
            "category_info":"test_add_operation_category",
        }
        amount_instance_2 = OperationCategory.objects.count()
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(OperationCategory.objects.count(), amount_instance_2)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/add_operation_category.html")

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'category_name' field
        long_value = "x" * 51
        data_wrong_category_name_more = {
            "category_name":long_value,
            "category_info":"test_add_operation_category",
        }
        amount_instance_3 = OperationCategory.objects.count()
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_more)
        self.assertEqual(OperationCategory.objects.count(), amount_instance_3)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/add_operation_category.html")

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'category_info' field
        data_wrong_category_name_less = {
            "category_name":"Category_3",
            "category_info":"test",
        }
        amount_instance_4 = OperationCategory.objects.count()
        response_wrong_info_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(OperationCategory.objects.count(), amount_instance_4)
        self.assertEqual(response_wrong_info_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_less_char, "accounting/add_operation_category.html")

        # Attempt to add an instance of the class with data containing a character count more
        # than the minimum value in the 'category_info' field
        long_value_info = "x" * 101
        data_wrong_category_name_more = {
            "category_name":"Category_4",
            "category_info":long_value_info,
        }
        amount_instance_5 = OperationCategory.objects.count()
        response_wrong_info_more_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_more)
        self.assertEqual(OperationCategory.objects.count(), amount_instance_5)
        self.assertEqual(response_wrong_info_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_more_char, "accounting/add_operation_category.html")

        # Attempt to add an instance of the class with data containing duplicate category_name data
        data_wrong_duplicate_category_name = {
            "category_name":"Category_1",
            "category_info":"test_add_operation_category",
        }
        amount_instance_6 = OperationCategory.objects.count()
        response_wrong_duplicate_category_name = self.client_user_accountant.post(new_reverse, data_wrong_duplicate_category_name)
        self.assertEqual(OperationCategory.objects.count(), amount_instance_6)
        self.assertEqual(response_wrong_duplicate_category_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_duplicate_category_name, "accounting/add_operation_category.html")

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

    # @unittest.skip
    def test_change_operation_category(self):
        # Creating an instance of the OperationCategory class 
        OperationCategory.objects.create(category_name="Cat_cha", category_info="Test_info_category")
        cha_operation_category = OperationCategory.objects.get(category_name="Cat_cha")

        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:change_operation_category', args=[cha_operation_category.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_category/change_opr_category/2/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:change_operation_category', args=[cha_operation_category.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:change_operation_category', args=[cha_operation_category.id]))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/change_operation_category.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:change_operation_category', args=[cha_operation_category.id]))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/change_operation_category.html")

        # Creating a data of the OperationCategory class 
        data_change_operation_category = {
            "category_name":"Cat_change",
            "category_info":"test_change_operation_category",
        }
        
        # Chanhe instance OperationCategory, and checking it
        amount_category_records_instance = OperationCategory.objects.count()
        new_reverse = reverse('accounting:change_operation_category', args=[cha_operation_category.id])
        response_change_category_record_norm = self.client_user_accountant.post(new_reverse, data_change_operation_category)
        self.assertEqual(OperationCategory.objects.count(), amount_category_records_instance)
        self.assertEqual(response_change_category_record_norm.status_code, 302)
        self.assertRedirects(response_change_category_record_norm, reverse('accounting:get_operation_category'))
        # Checking accounting records values
        new_category_records = OperationCategory.objects.get(category_name="Cat_change")
        self.assertEqual(new_category_records.category_info, "test_change_operation_category")

        storage = get_messages(response_change_category_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_CAT_OPERATION_UPDATED, messages)

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'category_name' field
        data_wrong_category_name_less = {
            "category_name":"Ca",
            "category_info":"test_change_operation_category",
        }
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/change_operation_category.html")

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'category_name' field
        long_value = "x" * 51
        data_wrong_category_name_more = {
            "category_name":long_value,
            "category_info":"test_change_operation_category",
        }
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_more)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/change_operation_category.html")

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'category_info' field
        data_wrong_category_name_less = {
            "category_name":"Cat_cha_2",
            "category_info":"test",
        }
        response_wrong_info_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(response_wrong_info_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_less_char, "accounting/change_operation_category.html")

        # Attempt to change an instance of the class with data containing a character count more
        # than the minimum value in the 'category_info' field
        long_value_info = "x" * 101
        data_wrong_category_name_more = {
            "category_name":"Cat_cha_2",
            "category_info":long_value_info,
        }
        response_wrong_info_more_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_more)
        self.assertEqual(response_wrong_info_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_more_char, "accounting/change_operation_category.html")

        # Attempt to change an instance of the class with data containing duplicate category_name data
        data_wrong_duplicate_category_name = {
            "category_name":"Category_1",
            "category_info":"test_change_operation_category",
        }
        response_wrong_duplicate_category_name = self.client_user_accountant.post(new_reverse, data_wrong_duplicate_category_name)
        self.assertEqual(response_wrong_duplicate_category_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_duplicate_category_name, "accounting/change_operation_category.html")

    # @unittest.skip
    def test_delete_operation_category(self):
        # Creating an instance of the OperationCategory class 
        OperationCategory.objects.create(category_name="Cat_del", category_info="Test_info_category")
        del_operation_category = OperationCategory.objects.get(category_name="Cat_del")

        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:delete_operation_category', args=[del_operation_category.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_category/delete_opr_category/2/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:delete_operation_category', args=[del_operation_category.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:delete_operation_category', args=[del_operation_category.id]))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/delete_operation_category.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:delete_operation_category', args=[del_operation_category.id]))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/delete_operation_category.html")

        # Checking deletion of a type by an authorized user with permission from "Accountant"
        count_categories = OperationCategory.objects.count()
        response_del = self.client_user_accountant.post(reverse("accounting:delete_operation_category", args=[del_operation_category.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("accounting:get_operation_category"))
        self.assertEqual(OperationCategory.objects.count(), count_categories-1) 

        storage = get_messages(response_del.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_CAT_OPERATION_DELETE, messages)

        # Attempt to delete operation_type wich conected with ClubTreasury object
        new_operation_category = OperationCategory.objects.create(category_name="Cat_del_2", category_info="Test_info_category")
        new_operation_type = OperationType.objects.create(type_name="Type_del_2", type_info="Test_info_type")
        ClubTreasury.objects.create(
            amount=100,
            operation_date_time=datetime.now(),
            info="Accounting_record_for_delete",
            performed_by=self.user_member,
            operation_category=new_operation_category,
            operation_type=new_operation_type,
        )
        operation_category_for_delete = OperationCategory.objects.get(category_name="Cat_del_2")

        count_categories_2 = OperationCategory.objects.count()
        response_del_wrong = self.client_user_accountant.post(reverse("accounting:delete_operation_category", args=[operation_category_for_delete.id]))
        self.assertEqual(response_del_wrong.status_code, 302)
        self.assertRedirects(response_del_wrong, reverse("accounting:get_operation_category"))
        self.assertEqual(OperationCategory.objects.count(), count_categories_2) 

        storage = get_messages(response_del_wrong.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_CAT_OPERATION_DELETE_ERR, messages)


class OperationTypeTest(TestCase):
    
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
        OperationType.objects.create(type_name="Type_1", type_info="Test_info_type")

    # @unittest.skip
    def test_add_operation_type(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:add_operation_type'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_type/add_operation_type/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:add_operation_type'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:add_operation_type'))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/add_operation_type.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:add_operation_type'))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/add_operation_type.html")

        # Creating new instance OperationType, and checking it
        data_new_operation_type = {
            "type_name":"type_2",
            "type_info":"test_add_operation_type",
        }
        amount_type_records_instance = OperationType.objects.count()
        new_reverse = reverse("accounting:add_operation_type")
        response_add_type_record_norm = self.client_user_accountant.post(new_reverse, data_new_operation_type)
        self.assertEqual(OperationType.objects.count(), amount_type_records_instance + 1)
        self.assertEqual(response_add_type_record_norm.status_code, 302)
        self.assertRedirects(response_add_type_record_norm, reverse('accounting:get_club_treasury'))
        # Checking accounting records values
        new_type_records = OperationType.objects.get(type_name="type_2")
        self.assertEqual(new_type_records.type_info, "test_add_operation_type")

        storage = get_messages(response_add_type_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_TYPE_OPERATION_ADDED, messages)

        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'type_name' field
        data_wrong_type_name_less = {
            "type_name":"ty",
            "type_info":"test_add_operation_type",
        }
        amount_instance_2 = OperationType.objects.count()
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, data_wrong_type_name_less)
        self.assertEqual(OperationType.objects.count(), amount_instance_2)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/add_operation_type.html")

        # # Attempt to add an instance of the class with data containing a character count less
        # # than the minimum value in the 'type_name' field
        long_value = "x" * 51
        data_wrong_type_name_more = {
            "type_name":long_value,
            "type_info":"test_add_operation_type",
        }
        amount_instance_3 = OperationType.objects.count()
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, data_wrong_type_name_more)
        self.assertEqual(OperationType.objects.count(), amount_instance_3)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/add_operation_type.html")


        # Attempt to add an instance of the class with data containing a character count less
        # than the minimum value in the 'type_info' field
        data_wrong_category_name_less = {
            "type_name":"type_3",
            "type_info":"test",
        }
        amount_instance_4 = OperationType.objects.count()
        response_wrong_info_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(OperationType.objects.count(), amount_instance_4)
        self.assertEqual(response_wrong_info_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_less_char, "accounting/add_operation_type.html")

        # Attempt to add an instance of the class with data containing a character count more
        # than the minimum value in the 'type_info' field
        long_value_info = "x" * 101
        data_wrong_category_name_more = {
            "type_name":"type_2",
            "type_info":long_value_info,
        }
        amount_instance_5 = OperationType.objects.count()
        response_wrong_info_more_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_more)
        self.assertEqual(OperationType.objects.count(), amount_instance_5)
        self.assertEqual(response_wrong_info_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_more_char, "accounting/add_operation_type.html")

        # Attempt to add an instance of the class with data containing duplicate type_name data
        data_wrong_duplicate_type_name = {
            "type_name":"Type_1",
            "type_info":"test_add_operation_type",
        }
        amount_instance_6 = OperationType.objects.count()
        response_wrong_duplicate_category_name = self.client_user_accountant.post(new_reverse, data_wrong_duplicate_type_name)
        self.assertEqual(OperationType.objects.count(), amount_instance_6)
        self.assertEqual(response_wrong_duplicate_category_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_duplicate_category_name, "accounting/add_operation_type.html")

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

    # @unittest.skip
    def test_change_operation_type(self):
        # Creating an instance of the OperationCategory class 
        OperationType.objects.create(type_name="Type_cha", type_info="Test_info_type")
        che_operation_type = OperationType.objects.get(type_name="Type_cha")

        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:change_operation_type', args=[che_operation_type.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_type/change_operation_type/2/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:change_operation_type', args=[che_operation_type.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:change_operation_type', args=[che_operation_type.id]))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/change_operation_type.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:change_operation_type', args=[che_operation_type.id]))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/change_operation_type.html")

        # New data for changing, and checking it
        data_cha_operation_type = {
            "type_name":"type_cha",
            "type_info":"test_change_operation_type",
        }
        amount_type_records_instance = OperationType.objects.count()
        new_reverse = reverse("accounting:change_operation_type", args=[che_operation_type.id])
        response_change_type_record_norm = self.client_user_accountant.post(new_reverse, data_cha_operation_type)
        self.assertEqual(OperationType.objects.count(), amount_type_records_instance)
        self.assertEqual(response_change_type_record_norm.status_code, 302)
        self.assertRedirects(response_change_type_record_norm, reverse('accounting:get_operation_type'))
        # Checking accounting records values
        changed_type_records = OperationType.objects.get(type_name="type_cha")
        self.assertEqual(changed_type_records.type_info, "test_change_operation_type")

        storage = get_messages(response_change_type_record_norm.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_TYPE_OPERATION_UPDATED, messages)


        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'type_name' field
        data_wrong_type_name_less = {
            "type_name":"ty",
            "type_info":"test_change_operation_type",
        }
        response_wrong_less_char = self.client_user_accountant.post(new_reverse, data_wrong_type_name_less)
        self.assertEqual(response_wrong_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_less_char, "accounting/change_operation_type.html")

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'type_name' field
        long_value = "x" * 51
        data_wrong_type_name_more = {
            "type_name":long_value,
            "type_info":"test_add_operation_type",
        }
        response_wrong_more_char = self.client_user_accountant.post(new_reverse, data_wrong_type_name_more)
        self.assertEqual(response_wrong_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_more_char, "accounting/change_operation_type.html")

        # Attempt to change an instance of the class with data containing a character count less
        # than the minimum value in the 'type_info' field
        data_wrong_category_name_less = {
            "type_name":"type_3",
            "type_info":"test",
        }
        response_wrong_info_less_char = self.client_user_accountant.post(new_reverse, data_wrong_category_name_less)
        self.assertEqual(response_wrong_info_less_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_less_char, "accounting/change_operation_type.html")

        # Attempt to change an instance of the class with data containing a character count more
        # than the minimum value in the 'type_info' field
        long_value_info = "x" * 101
        data_wrong_type_name_more = {
            "type_name":"type_2",
            "type_info":long_value_info,
        }
        response_wrong_info_more_char = self.client_user_accountant.post(new_reverse, data_wrong_type_name_more)
        self.assertEqual(response_wrong_info_more_char.status_code, 200)
        self.assertTemplateUsed(response_wrong_info_more_char, "accounting/change_operation_type.html")

        # Attempt to change an instance of the class with data containing duplicate type_name data
        data_wrong_duplicate_type_name = {
            "type_name":"Type_1",
            "type_info":"test_change_operation_type",
        }
        response_wrong_duplicate_category_name = self.client_user_accountant.post(new_reverse, data_wrong_duplicate_type_name)
        self.assertEqual(response_wrong_duplicate_category_name.status_code, 200)
        self.assertTemplateUsed(response_wrong_duplicate_category_name, "accounting/change_operation_type.html")

    # @unittest.skip
    def test_delete_operation_type(self):
        # Creating an instance of the OperationCategory class 
        OperationType.objects.create(type_name="Type_del", type_info="Test_info_type")
        del_operation_type = OperationType.objects.get(type_name="Type_del")

        # Check access for an unauthorized user
        response = self.client.get(reverse('accounting:delete_operation_type', args=[del_operation_type.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/accounting/operation_type/delete_operation_type/2/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('accounting:delete_operation_type', args=[del_operation_type.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, '/accounting/')

        # Check access for an authorized user 'user_head'
        response_user_head = self.client_user_head.get(reverse('accounting:delete_operation_type', args=[del_operation_type.id]))
        self.assertEqual(response_user_head.status_code, 200)
        self.assertTemplateUsed(response_user_head, "accounting/delete_operation_type.html")

        # Check access for an authorized user 'accountant'
        response_accountant = self.client_user_accountant.get(reverse('accounting:delete_operation_type', args=[del_operation_type.id]))
        self.assertEqual(response_accountant.status_code, 200)
        self.assertTemplateUsed(response_accountant, "accounting/delete_operation_type.html")

        # Checking deletion of a type by an authorized user with permission from "Accountant"
        count_types = OperationType.objects.count()
        response_del = self.client_user_accountant.post(reverse("accounting:delete_operation_type", args=[del_operation_type.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("accounting:get_operation_type"))
        self.assertEqual(OperationType.objects.count(), count_types-1) 

        storage = get_messages(response_del.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_TYPE_OPERATION_DELETE, messages)

        # Attempt to delete operation_type wich conected with ClubTreasury object
        new_operation_category = OperationCategory.objects.create(category_name="Category_del", category_info="Test_info_category")
        new_operation_type = OperationType.objects.create(type_name="Type_del_2", type_info="Test_info_type")
        ClubTreasury.objects.create(
            amount=100,
            operation_date_time=datetime.now(),
            info="Accounting_record_for_delete",
            performed_by=self.user_member,
            operation_category=new_operation_category,
            operation_type=new_operation_type,
        )
        operation_type_for_delete = OperationType.objects.get(type_name="Type_del_2")

        count_types_2 = OperationType.objects.count()
        response_del_wrong = self.client_user_accountant.post(reverse("accounting:delete_operation_type", args=[operation_type_for_delete.id]))
        self.assertEqual(response_del_wrong.status_code, 302)
        self.assertRedirects(response_del_wrong, reverse("accounting:get_operation_type"))
        self.assertEqual(OperationType.objects.count(), count_types_2) 

        storage = get_messages(response_del_wrong.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_TYPE_OPERATION_DELETE_ERR, messages)
