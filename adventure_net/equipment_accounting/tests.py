from datetime import datetime, timedelta
import unittest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from .models import Equipments, EquipmentsCategories, EquipmentBooking
from .views import permissions_equipment_checker, check_equipment_booking
from users.models import UserPositions
from .forms import EquipmentsCategoriesForm, EquipmentsForm, BookingEquipmentsForm
from adventure_net.messages import MSG_INVALID_START_DATE,\
    MSG_INVALID_END_DATE, MSG_INVALID_BOOKING_DURATION, MSG_INVALID_BOOKING_PERIOD_OVERLAP,\
    MSG_EQUIPMENT_RESERVED_SUCCESSFULLY, MSG_BOOKING_PERIOD_DELETED


class EquipmentViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

        # user_member Authentication
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

        category = EquipmentsCategories.objects.create(equipment_category_name="Category_1")
        equipment = Equipments.objects.create(
            equipment_name="new_equipment_1",
            weight_of_equipment_kg=120,
            equipment_description="new_equipment_1_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment.equipment_category.add(category)

        # user_head authentication
        self.client_user_head = Client()
        username_head = 'testuser_Head'
        password_head = 'testpassword_Head'
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

        # user_equipment_manager authentication
        self.client_equipment_manager = Client()
        username_equipment_manager = 'testuser_Equipment_manager'
        password_equipment_manager = 'testpassword_Equipment_manager'
        self.user_equipment_manager = User.objects.create_user(
                                                          username=username_equipment_manager,
                                                          password=password_equipment_manager
                                                         )
        self.client_equipment_manager.force_login(self.user_equipment_manager)

        position_name_equipment_manager = "Equipment manager"
        position_equipment_manager, created = UserPositions.objects.get_or_create(positions_category=position_name_equipment_manager)
        self.user_equipment_manager.profile.user_position.add(position_equipment_manager)

    @unittest.skip
    def test_get_equipments(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:get_equipments'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('equipment:get_equipments'))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/equipment.html")

        # Check the existence of equipment
        equipment = Equipments.objects.get(equipment_name="new_equipment_1")
        self.assertEqual(Equipments.objects.count(), 1)
        self.assertIsNotNone(equipment)
        self.assertEqual(equipment.equipment_name, "new_equipment_1")

        # Checking an authenticated user
        self.assertEqual(response_member.context['user'], self.user_member)

    # @unittest.skip
    def test_add_equipment(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:add_equipment'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/add_equipment/')

        # Check access for an authorized user 'user_member' without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Check access for an authorized user with 'Head' permission
        response_head = self.client_user_head.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/add_equipment.html")

        # Check access for an authorized user with 'Equipment_manager' permission
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/add_equipment.html")

        equipment_category_test_2 = [EquipmentsCategories.objects.get(equipment_category_name="Category_1")]
        
        new_data = {
            "equipment_name": "NeW_EqUiPmEnT_2",
            "weight_of_equipment_kg": 120.2,
            "equipment_description": "new_equipment_2_description",
            "photo_of_equipment": "default_tool.png",
            "current_user": self.user_head.id,
            "equipment_category": equipment_category_test_2,
        }

        # Creating new equipment and checking for case sensitivity in the entered data
        response_add_eq = self.client_user_head.post(reverse("equipment:add_equipment"), new_data)
        self.assertEqual(Equipments.objects.count(), 2)
        self.assertEqual(response_add_eq.status_code, 302)
        self.assertRedirects(response_add_eq, reverse("equipment:get_equipments"))

        # Checking for the name "NeW_EqUiPmEnT_2"
        new_equipment_wrong = Equipments.objects.filter(equipment_name="NeW_EqUiPmEnT_2").first()
        self.assertIsNone(new_equipment_wrong)

        # Fetching the equipment object "New_equipment_2" from the database
        new_equipment = Equipments.objects.get(equipment_name="New_equipment_2")

        # Checking equipment values
        self.assertEqual(new_equipment.equipment_name, "New_equipment_2")  
        self.assertEqual(new_equipment.weight_of_equipment_kg, 120.2)
        self.assertEqual(new_equipment.equipment_description, "new_equipment_2_description")
        self.assertEqual(new_equipment.photo_of_equipment, "default_tool.png")

        # Attempt to add an instance of the class with data containing a character count less than the minimum value in the 'equipment_name' field
        data_less_min_name = {
                            "equipment_name": "Ne",
                            "weight_of_equipment_kg": 120.2,
                            "equipment_description": "new_equipment_2_description",
                            "photo_of_equipment": "default_tool.png",
                            "current_user": self.user_head.id,
                            "equipment_category": equipment_category_test_2,
                            }

        count_equipments_before = Equipments.objects.count()
        form_less_min_name = EquipmentsForm(data=data_less_min_name)
        self.assertFalse(form_less_min_name.is_valid())
        
        response_add_less_min_name = self.client_user_head.post(reverse("equipment:add_equipment"), data_less_min_name)
        self.assertEqual(response_add_less_min_name.status_code, 200)
        self.assertTemplateUsed(response_add_less_min_name, "equipment_accounting/add_equipment.html")
        self.assertEqual(count_equipments_before, Equipments.objects.count())

        # Attempt to create an instance of the class with invalid data in the booking_date_from field
        long_value = "x" * 51
        data_greater_max_name = {
                            "equipment_name": long_value,
                            "weight_of_equipment_kg": 120.2,
                            "equipment_description": "new_equipment_2_description",
                            "photo_of_equipment": "default_tool.png",
                            "current_user": self.user_head.id,
                            "equipment_category": equipment_category_test_2,
                            }

        count_equipments_before = Equipments.objects.count()
        form_greater_max_name = EquipmentsForm(data=data_greater_max_name)
        self.assertFalse(form_greater_max_name.is_valid())
        
        response_add_greater_max_name = self.client_user_head.post(reverse("equipment:add_equipment"), data_greater_max_name)
        self.assertEqual(response_add_greater_max_name.status_code, 200)
        self.assertTemplateUsed(response_add_greater_max_name, "equipment_accounting/add_equipment.html")
        self.assertEqual(count_equipments_before, Equipments.objects.count())

        # Attempt to add an instance of the class with data less than 0 in the weight_of_equipment_kg field
        data_negative_value_weight = {
                            "equipment_name": "New_equipment_test",
                            "weight_of_equipment_kg": -10,
                            "equipment_description": "new_equipment_2_description",
                            "photo_of_equipment": "default_tool.png",
                            "current_user": self.user_head.id,
                            "equipment_category": equipment_category_test_2,
                            }

        count_equipments_before = Equipments.objects.count()
        form_negative_value_weight = EquipmentsForm(data=data_negative_value_weight)
        self.assertFalse(form_negative_value_weight.is_valid())
        
        response_add_negative_value_weight = self.client_user_head.post(reverse("equipment:add_equipment"), data_negative_value_weight)
        self.assertEqual(response_add_negative_value_weight.status_code, 200)
        self.assertTemplateUsed(response_add_negative_value_weight, "equipment_accounting/add_equipment.html")
        self.assertEqual(count_equipments_before, Equipments.objects.count())

        # Attempt to add an instance of a class with data containing a character count less than the minimum in the 'equipment_description' field
        data_less_min_des = {
                            "equipment_name": "New_equipment_test",
                            "weight_of_equipment_kg": 10,
                            "equipment_description": "ne",
                            "photo_of_equipment": "default_tool.png",
                            "current_user": self.user_head.id,
                            "equipment_category": equipment_category_test_2,
                            }

        count_equipments_before = Equipments.objects.count()
        form_less_min_des = EquipmentsForm(data=data_less_min_des)
        self.assertFalse(form_less_min_des.is_valid())
        
        response_less_min_des = self.client_user_head.post(reverse("equipment:add_equipment"), data_less_min_des)
        self.assertEqual(response_less_min_des.status_code, 200)
        self.assertTemplateUsed(response_less_min_des, "equipment_accounting/add_equipment.html")
        self.assertEqual(count_equipments_before, Equipments.objects.count())

        # Attempt to add an instance of the class with data exceeding the maximum character limit in the equipment_description field
        long_value_2 = "x" * 151
        data_greater_max_des = {
                            "equipment_name": "New_equipment_test",
                            "weight_of_equipment_kg": 10,
                            "equipment_description": long_value_2,
                            "photo_of_equipment": "default_tool.png",
                            "current_user": self.user_head.id,
                            "equipment_category": equipment_category_test_2,
                            }

        count_equipments_before = Equipments.objects.count()
        form_greater_max_des = EquipmentsForm(data=data_greater_max_des)
        self.assertFalse(form_greater_max_des.is_valid())
        
        response_greater_max_des = self.client_user_head.post(reverse("equipment:add_equipment"), data_greater_max_des)
        self.assertEqual(response_greater_max_des.status_code, 200)
        self.assertTemplateUsed(response_greater_max_des, "equipment_accounting/add_equipment.html")
        self.assertEqual(count_equipments_before, Equipments.objects.count())

    # @unittest.skip
    def test_delete_equipment(self):

        # Creating an instance of the Equipments class
        category = EquipmentsCategories.objects.create(equipment_category_name="Category_2")
        equipment_del = Equipments.objects.create(
            equipment_name="New_equipment_3",
            weight_of_equipment_kg=120.3,
            equipment_description="new_equipment_3_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment_del.equipment_category.add(category)

        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/delete_equipment/{equipment_del.id}')

        # Check access for an authenticated user user_member without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Check access for an authenticated user with permission from 'Head'
        response_head = self.client_user_head.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/delete_equipment.html")

        # Checking access for an authorized user with permission from 'Equipment_manager'
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/delete_equipment.html")

        # Check if the equipment to be deleted exists in the database
        looking_for_equipment_first = Equipments.objects.get(equipment_name="New_equipment_3")
        self.assertIsNotNone(looking_for_equipment_first)
        
        # Delete the equipment from the database
        response_del = self.client_equipment_manager.post(reverse("equipment:delete_equipment", args=[equipment_del.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("equipment:get_equipments"))

        # Check if the equipment to be deleted does not exist in the database
        deleted_equipment = Equipments.objects.filter(equipment_name="New_equipment_3").first()
        self.assertIsNone(deleted_equipment)

    # @unittest.skip
    def test_change_equipment(self):
        
        # Creating an instance of the Equipments class
        category = EquipmentsCategories.objects.create(equipment_category_name="Category_2")
        equipment_old = Equipments.objects.create(
            equipment_name="New_equipment_4",
            weight_of_equipment_kg=120.4,
            equipment_description="new_equipment_4_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment_old.equipment_category.add(category)

        change_data = {
            "equipment_name": "New_equipment_5",
            "weight_of_equipment_kg": 120.5,
            "equipment_description": "new_equipment_4_description",
            "equipment_category": [EquipmentsCategories.objects.get(equipment_category_name="Category_1")],
            }
        
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/change_equipment/{equipment_old.id}')

        # Checking access for an authorized user, user_member, without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Checking access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/change_equipment.html")

        # Checking access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/change_equipment.html")
        
        # Changing equipment in the database
        response_che = self.client_equipment_manager.post(reverse("equipment:change_equipment", args=[equipment_old.id]), change_data)
        self.assertEqual(response_che.status_code, 302)
        self.assertRedirects(response_che, reverse("equipment:get_equipments"))

        # Checking the database for changes
        equipment_updated = Equipments.objects.get(id=equipment_old.id)
        self.assertEqual(equipment_updated.equipment_name, "New_equipment_5")
        self.assertEqual(equipment_updated.weight_of_equipment_kg, 120.5)
        self.assertEqual(equipment_updated.equipment_description, "new_equipment_4_description")

        # Attempting to make changes with data containing fewer characters than the min in the equipment_name field
        change_data_less_min_name = {"equipment_name": "Ne"}

        form_less_min_name = EquipmentsForm(data=change_data_less_min_name)
        self.assertFalse(form_less_min_name.is_valid())

        # Attempting to make changes with data containing more characters than the max in the equipment_name field
        long_value = "x" * 51
        change_data_greater_max_name = {"equipment_name": long_value}

        form_greater_max_name = EquipmentsForm(data=change_data_greater_max_name)
        self.assertFalse(form_greater_max_name.is_valid())

        # Attempting to make changes with data less than 0 in the weight_of_equipment_kg field
        change_data_negative_value_weight = {"weight_of_equipment_kg": -10}

        form_negative_value_weight = EquipmentsForm(data=change_data_negative_value_weight)
        self.assertFalse(form_negative_value_weight.is_valid())
        
        # Attempting to make changes with data containing fewer characters than the min in the equipment_description field
        change_data_less_min_des = {"equipment_description": "Ne"}

        form_less_min_des = EquipmentsForm(data=change_data_less_min_des)
        self.assertFalse(form_less_min_des.is_valid())

        # Attempt to make changes with data containing more characters than the max limit in the equipment_description field
        long_value_2 = "x" * 151
        change_data_greater_max_des = {"equipment_description": long_value_2}

        form_greater_max_des = EquipmentsForm(data=change_data_greater_max_des)
        self.assertFalse(form_greater_max_des.is_valid())

    # @unittest.skip
    def test_detail_equipment(self):

        # Fetching equipment data
        equipment_det = Equipments.objects.get(equipment_name="new_equipment_1")

        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/detail/{equipment_det.id}')

        # Checking access for an authenticated user "user_member" without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/detail.html")

        # Checking access for an authenticated user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/detail.html")

        # Checking access to a page with non-existent equipment
        response_wrong = self.client_user_member.get(reverse("equipment:detail_equipment", args=[1000]))
        self.assertEqual(response_wrong.status_code, 404)

        # Checking the presence of correct data in the response
        self.assertContains(response_member, "new_equipment_1")
        self.assertContains(response_member, "120")
        self.assertContains(response_member, "new_equipment_1_description")
        self.assertContains(response_member, "default_tool.png")


class CategoruViewTest(TestCase):

    # @unittest.skip
    def setUp(self):
        User = get_user_model()

        # Authentication of user_member
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

        # Authentication of user_head
        self.client_user_head = Client()
        username_head = 'testuser_Head'
        password_head = 'testpassword_Head'
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

        # Authentication of user_equipment_manager
        self.client_equipment_manager = Client()
        username_equipment_manager = 'testuser_Equipment_manager'
        password_equipment_manager = 'testpassword_Equipment_manager'
        self.user_equipment_manager = User.objects.create_user(
                                                          username=username_equipment_manager,
                                                          password=password_equipment_manager
                                                         )
        self.client_equipment_manager.force_login(self.user_equipment_manager)
        position_name_equipment_manager = "Equipment manager"
        position_equipment_manager, created = UserPositions.objects.get_or_create(positions_category=position_name_equipment_manager)
        self.user_equipment_manager.profile.user_position.add(position_equipment_manager)

        # Creating an instance of the EquipmentsCategories class
        EquipmentsCategories.objects.create(equipment_category_name="Category_1")

    # @unittest.skip
    def test_get_category(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:get_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/')

        # Checking access for an authorized user user_member without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:get_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Checking access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:get_category'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/category.html")

        # Checking access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:get_category'))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/category.html")

        # Checking the presence of an instance of the EquipmentsCategories class
        category = EquipmentsCategories.objects.get(equipment_category_name="Category_1")
        self.assertEqual(EquipmentsCategories.objects.count(), 1)
        self.assertIsNotNone(category)
        self.assertEqual(category.equipment_category_name, "Category_1")
 
    # @unittest.skip
    def test_add_category(self):
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:add_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/add_category')

        # Check access for an authorized user (user_member) without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:add_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Check access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:add_category'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/add_category.html")

        # Check access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:add_category'))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/add_category.html")
        
        # Create an instance of the class with satisfactory data and check for case sensitivity in the entered data
        data = {"equipment_category_name": "CaTeGoRy2"}
        response_add = self.client_user_head.post(reverse("equipment:add_category"), data)
        self.assertEqual(response_add.status_code, 302)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertRedirects(response_add, reverse("equipment:get_category"))
        
        data = {"equipment_category_name": "Category3"}
        form = EquipmentsCategoriesForm(data=data)
        self.assertTrue(form.is_valid())

        # Attempt to create an instance of a class with duplicate data
        data_twin = {"equipment_category_name": "Category2"}
        response_add_twin = self.client_user_head.post(reverse("equipment:add_category"), data_twin)
        self.assertEqual(response_add_twin.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_twin, "equipment_accounting/add_category.html")

        # Attempt to create an instance of a class with data length less than min
        data_less_min = {"equipment_category_name": "Ca"}

        form_less_min = EquipmentsCategoriesForm(data=data_less_min)
        self.assertFalse(form_less_min.is_valid())

        response_add_less_min = self.client_user_head.post(reverse("equipment:add_category"), data_less_min)
        self.assertEqual(response_add_less_min.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_less_min, "equipment_accounting/add_category.html")

        # Attempt to create an instance of the class with data that exceeds the maximum character limit
        data_greater_max = {"equipment_category_name": "this_value_is_greater_than_twenty_symbols"}

        form_greater_max = EquipmentsCategoriesForm(data=data_greater_max)
        self.assertFalse(form_greater_max.is_valid())

        response_add_greater_max = self.client_user_head.post(reverse("equipment:add_category"), data_greater_max)
        self.assertEqual(response_add_greater_max.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_greater_max, "equipment_accounting/add_category.html")

    # @unittest.skip
    def test_change_category(self):
        # Getting an instance of the EquipmentsCategories class
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category_1")
        
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/change_category/1')

        # Checking access for an authorized user "user_member" without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Checking access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/change_category.html")

        # Checking access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/change_category.html")

        # Modifying an instance of the class with satisfactory data
        change_data = {"equipment_category_name": "Change_Category1"}
        response_change = self.client_equipment_manager.post(reverse("equipment:change_category", args=[category1.id]), change_data)
        self.assertEqual(response_change.status_code, 302)
        self.assertRedirects(response_change, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "Change_Category1")

        # Changing instance data with duplicated data
        change_data_twin = {"equipment_category_name": "Change_Category1"}
        response_change_twin = self.client_equipment_manager.post(reverse(
                                                                            "equipment:change_category",
                                                                            args=[category1.id]
                                                                            ), change_data_twin)
        self.assertEqual(response_change_twin.status_code, 200)
        self.assertTemplateUsed(response_change_twin, "equipment_accounting/change_category.html")

        # Changing instance data with a number of characters less than min
        change_data_less_min = {"equipment_category_name": "Ch"}
        response_change_less_min = self.client_equipment_manager.post(reverse(
                                                                            "equipment:change_category",
                                                                            args=[category1.id]
                                                                            ), change_data_less_min)
        self.assertEqual(response_change_less_min.status_code, 200)
        self.assertTemplateUsed(response_change_less_min, "equipment_accounting/change_category.html")
        self.assertNotEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "Ch")

        # Changing instance data with a number of characters greater than max
        change_data_greater_max = {"equipment_category_name": "this_value_is_greater_than_twenty_symbols"}
        response_change_greater_max = self.client_equipment_manager.post(reverse(
                                                                                "equipment:change_category",
                                                                                args=[category1.id]
                                                                                ), change_data_greater_max)
        self.assertEqual(response_change_greater_max.status_code, 200)
        self.assertTemplateUsed(response_change_greater_max, "equipment_accounting/change_category.html")
        self.assertNotEqual(
                            EquipmentsCategories.objects.get(id=category1.id).equipment_category_name,
                            "this_value_is_greater_than_twenty_symbols"
                            )

    # @unittest.skip
    def test_delete_category(self):
        # Creating an instance of the EquipmentsCategories class
        category_for_del = EquipmentsCategories.objects.create(equipment_category_name="Category_del")
        category_for_del_id = category_for_del.id
        
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/category/delete_category/{category_for_del_id}')

        # Checking access for an authorized user "user_member" without permission to add equipment
        response_member = self.client_user_member.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Checking access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/delete_category.html")

        # Checking access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/delete_category.html")
        
        # Checking deletion of a category by an authorized user with permission from "Equipment_manager"
        count_categorys = EquipmentsCategories.objects.count()
        response_del = self.client_equipment_manager.post(reverse("equipment:delete_category", args=[category_for_del.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.count(), count_categorys-1)


class EquipmentBookingViewTest(TestCase):

    # @unittest.skip
    def setUp(self):
        User = get_user_model()

        # Authentication of user_member
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

        # Authentication of user_member_2
        self.client_user_member_2 = Client()
        username_member_2 = 'testuser_Member_2'
        password_member_2 = 'testpassword_Member_2'
        self.user_member_2 = User.objects.create_user(username=username_member_2, password=password_member_2)
        self.client_user_member_2.force_login(self.user_member_2)

        # Authentication of user_head
        self.client_user_head = Client()
        username_head = 'testuser_Head'
        password_head = 'testpassword_Head'
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

        # Authentication of user_equipment_manager
        self.client_equipment_manager = Client()
        username_equipment_manager = 'testuser_Equipment_manager'
        password_equipment_manager = 'testpassword_Equipment_manager'
        self.user_equipment_manager = User.objects.create_user(
                                                          username=username_equipment_manager,
                                                          password=password_equipment_manager
                                                         )
        self.client_equipment_manager.force_login(self.user_equipment_manager)

        position_name_equipment_manager = "Equipment manager"
        position_equipment_manager, created = UserPositions.objects.get_or_create(positions_category=position_name_equipment_manager)
        self.user_equipment_manager.profile.user_position.add(position_equipment_manager)

        # Creating an instance of the Equipments class 
        category = EquipmentsCategories.objects.create(equipment_category_name="Category_1")
        equipment = Equipments.objects.create(
            equipment_name="New_equipment_1",
            weight_of_equipment_kg=120,
            equipment_description="new_equipment_1_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment.equipment_category.add(category)


        equipment_2 = Equipments.objects.create(
            equipment_name="New_equipment_2",
            weight_of_equipment_kg=120,
            equipment_description="new_equipment_2_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment_2.equipment_category.add(category)

        # Creating an instance of the EquipmentBooking class
        EquipmentBooking.objects.create(
            club_member=self.user_member,
            reserved_equipment=equipment,
            booking_date_from=datetime.now() + timedelta(days=7),
            booking_date_to=datetime.now() + timedelta(days=10),
        )

    # @unittest.skip
    def test_get_book_equipment(self):

        # Getting an instance of the EquipmentBooking class
        equipment_booking_1 = EquipmentBooking.objects.get(pk=1)
        self.assertIsNotNone(equipment_booking_1)
        
        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:get_book_equipment', args=[equipment_booking_1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/get_book_equipment/1')

        # Check access for an authorized user, user_member
        response_member = self.client_user_member.get(reverse('equipment:get_book_equipment', args=[equipment_booking_1.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/get_book_equipment.html")

        # Checking the value of permission for the user_member user
        context_member = response_member.context
        permission_member = context_member['permission']
        self.assertFalse(permission_member)

        # Checking access for an authorized user with permission from "Head"
        response_head = self.client_user_head.get(reverse('equipment:get_book_equipment', args=[equipment_booking_1.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/get_book_equipment.html")

        # Checking the value of permission for user_head
        context_head = response_head.context
        permission_head = context_head['permission']
        self.assertTrue(permission_head)

        # Check access for an authorized user with permission from "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:get_book_equipment', args=[equipment_booking_1.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/get_book_equipment.html")

        # Checking the value of permission for the equipment_manager user
        context_equipment_manager = response_equipment_manager.context
        permission_equipment_manager = context_equipment_manager['permission']
        self.assertTrue(permission_equipment_manager)

    # @unittest.skip
    def test_book_equipment(self):

        # Getting an instance of the Equipments class
        equipment_book = Equipments.objects.get(equipment_name="New_equipment_1")
        equipment_book_2 = Equipments.objects.get(equipment_name="New_equipment_2")

        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:book_equipment', args=[equipment_book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/book_equipment/1')

        # Checking access for an authenticated user, user_member
        response_member = self.client_user_member.get(reverse('equipment:book_equipment', args=[equipment_book.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/book_equipment.html")


        # Creating an instance of the class with satisfactory data
        booking_date_from_1 = datetime.now().date() + timedelta(days=2)
        booking_date_to_1 = datetime.now().date() + timedelta(days=3)

        data = {
                'booking_date_from': booking_date_from_1,
                'booking_date_to': booking_date_to_1
                }

        count_bookings = EquipmentBooking.objects.count()
        response_add = self.client_user_member.post(reverse('equipment:book_equipment', args=[equipment_book.id]), data)
        self.assertEqual(response_add.status_code, 302)

        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings+1)
        self.assertRedirects(response_add, reverse("equipment:get_equipments"))

        storage = get_messages(response_add.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_EQUIPMENT_RESERVED_SUCCESSFULLY, messages)

        # Attempt to create an instance of the class with invalid data, the start date is earlier than the end date
        booking_date_from_2 = datetime.now().date() + timedelta(days=15)
        booking_date_to_2 = datetime.now().date() + timedelta(days=10)

        data_start_less_finish = {
                                'booking_date_from': booking_date_from_2,
                                'booking_date_to': booking_date_to_2
                                }
        count_bookings = EquipmentBooking.objects.count()
        response_wrong_start = self.client_user_member.post(reverse('equipment:book_equipment', args=[equipment_book.id]), data_start_less_finish)

        self.assertEqual(response_wrong_start.status_code, 200)
        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings)
        self.assertTemplateUsed(response_wrong_start, "equipment_accounting/book_equipment.html")

        storage = get_messages(response_wrong_start.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_INVALID_START_DATE, messages)

        # Attempt to create an instance of the class with invalid data, where the start date is earlier than the current date
        booking_date_from_3 = datetime.now().date() - timedelta(days=1)
        booking_date_to_3 = datetime.now().date() + timedelta(days=1)

        data_start_less = {
                                'booking_date_from': booking_date_from_3,
                                'booking_date_to': booking_date_to_3
                                }
        count_bookings = EquipmentBooking.objects.count()
        response_wrong_start_2 = self.client_user_member.post(reverse('equipment:book_equipment', args=[equipment_book.id]), data_start_less)

        self.assertEqual(response_wrong_start_2.status_code, 200)
        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings)
        self.assertTemplateUsed(response_wrong_start_2, "equipment_accounting/book_equipment.html")

        storage = get_messages(response_wrong_start_2.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_INVALID_END_DATE, messages)

        # Attempt to create an instance of the class with invalid data, booking period exceeds 30 days
        booking_date_from_4 = datetime.now().date() + timedelta(days=10)
        booking_date_to_4 = datetime.now().date() + timedelta(days=45)

        data_more_30_days = {
                                'booking_date_from': booking_date_from_4,
                                'booking_date_to': booking_date_to_4
                                }
        count_bookings = EquipmentBooking.objects.count()
        response_more_30_days = self.client_user_member.post(reverse('equipment:book_equipment', args=[equipment_book.id]), data_more_30_days)

        self.assertEqual(response_more_30_days.status_code, 200)
        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings)
        self.assertTemplateUsed(response_more_30_days, "equipment_accounting/book_equipment.html")

        storage = get_messages(response_more_30_days.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_INVALID_BOOKING_DURATION, messages)

        # Attempt to create an instance of the class with invalid data, the booking period overlaps
        booking_date_from_4 = datetime.now().date() + timedelta(days=1)
        booking_date_to_4 = datetime.now().date() + timedelta(days=10)

        data_overlap = {
                                'booking_date_from': booking_date_from_4,
                                'booking_date_to': booking_date_to_4
                                }
        count_bookings = EquipmentBooking.objects.count()
        response_overlap = self.client_user_member.post(reverse(
                                                                'equipment:book_equipment',
                                                                args=[equipment_book.id]
                                                                ), data_overlap)

        self.assertEqual(response_overlap.status_code, 200)
        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings)
        self.assertTemplateUsed(response_overlap, "equipment_accounting/book_equipment.html")

        storage = get_messages(response_overlap.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_INVALID_BOOKING_PERIOD_OVERLAP, messages)

        # Creating an instance of the class with satisfactory data for a period that overlaps with another equipment
        booking_date_from_1 = datetime.now().date() + timedelta(days=2)
        booking_date_to_1 = datetime.now().date() + timedelta(days=3)

        data = {
                'booking_date_from': booking_date_from_1,
                'booking_date_to': booking_date_to_1
                }

        count_bookings = EquipmentBooking.objects.count()
        response_add = self.client_user_member.post(reverse('equipment:book_equipment', args=[equipment_book_2.id]), data)
        self.assertEqual(response_add.status_code, 302)

        form_norm = BookingEquipmentsForm(data=data)
        self.assertTrue(form_norm.is_valid())

        self.assertEqual(EquipmentBooking.objects.count(), count_bookings+1)
        self.assertRedirects(response_add, reverse("equipment:get_equipments"))

        storage = get_messages(response_add.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_EQUIPMENT_RESERVED_SUCCESSFULLY, messages)

    # @unittest.skip
    def test_cancel_equipment_reservation(self):

        # Getting an instance of the Equipments class
        equipment_book = Equipments.objects.get(equipment_name="New_equipment_1")

        # Check access for an unauthorized user
        response = self.client.get(reverse('equipment:cancel_equipment_reservation', args=[equipment_book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/cancel_equipment_reservation/1')

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('equipment:cancel_equipment_reservation', args=[equipment_book.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/cancel_equipment_reservation.html")


        # Check the correctness of deleting own booking
        EquipmentBooking.objects.create(
            club_member=self.user_member,
            reserved_equipment=equipment_book,
            booking_date_from=datetime.now() + timedelta(days=50),
            booking_date_to=datetime.now() + timedelta(days=53),
        )
        equipment_book_del_1 = EquipmentBooking.objects.get(booking_date_from=datetime.now() + timedelta(days=50))

        count_bookings = EquipmentBooking.objects.count()
        response_del = self.client_user_member.post(reverse('equipment:cancel_equipment_reservation', args=[equipment_book_del_1.id]))
        self.assertEqual(EquipmentBooking.objects.count(), count_bookings-1)
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("equipment:get_equipments"))

        storage = get_messages(response_del.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_BOOKING_PERIOD_DELETED, messages)

        # Check access for an authorized user 'user_member'
        response_member = self.client_user_member.get(reverse('equipment:cancel_equipment_reservation', args=[equipment_book.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/cancel_equipment_reservation.html")


        # Checking the correctness of deleting a non-owned booking by a user with Head status
        EquipmentBooking.objects.create(
            club_member=self.user_member,
            reserved_equipment=equipment_book,
            booking_date_from=datetime.now() + timedelta(days=50),
            booking_date_to=datetime.now() + timedelta(days=53),
        )
        equipment_book_del_1 = EquipmentBooking.objects.get(booking_date_from=datetime.now() + timedelta(days=50))

        count_bookings = EquipmentBooking.objects.count()
        response_del_head = self.client_user_head.post(reverse('equipment:cancel_equipment_reservation', args=[equipment_book_del_1.id]))
        self.assertEqual(EquipmentBooking.objects.count(), count_bookings-1)
        self.assertEqual(response_del_head.status_code, 302)
        self.assertRedirects(response_del_head, reverse("equipment:get_equipments"))

        storage = get_messages(response_del_head.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_BOOKING_PERIOD_DELETED, messages)

        # Check the correctness of deleting a non-owned booking by a user with the Equipment manager status
        EquipmentBooking.objects.create(
            club_member=self.user_member,
            reserved_equipment=equipment_book,
            booking_date_from=datetime.now() + timedelta(days=50),
            booking_date_to=datetime.now() + timedelta(days=53),
        )
        equipment_book_del_1 = EquipmentBooking.objects.get(booking_date_from=datetime.now() + timedelta(days=50))

        count_bookings = EquipmentBooking.objects.count()
        response_del_equipment_manager = self.client_equipment_manager.post(reverse('equipment:cancel_equipment_reservation', args=[equipment_book_del_1.id]))
        self.assertEqual(EquipmentBooking.objects.count(), count_bookings-1)
        self.assertEqual(response_del_equipment_manager.status_code, 302)
        self.assertRedirects(response_del_equipment_manager, reverse("equipment:get_equipments"))

        storage = get_messages(response_del_equipment_manager.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn(MSG_BOOKING_PERIOD_DELETED, messages)    

    # @unittest.skip
    def test_permissions_equipment_checker(self):

        # Checking permissions_equipment_checker
        request_member = self.client_user_member.request().wsgi_request
        request_head = self.client_user_head.request().wsgi_request
        request_equipment_manager = self.client_equipment_manager.request().wsgi_request

        # Checking user_member
        has_permissions_member = permissions_equipment_checker(request_member)
        self.assertFalse(has_permissions_member)

        # Checking user_head
        has_permissions_head = permissions_equipment_checker(request_head)
        self.assertTrue(has_permissions_head)

        # Checking user_equipment_manager
        has_permissions_equipment_manager = permissions_equipment_checker(request_equipment_manager)
        self.assertTrue(has_permissions_equipment_manager)

    # @unittest.skip
    def test_check_equipment_booking(self):
        # Create an instance of the EquipmentBooking class with a past date
        equipment = Equipments.objects.get(pk=1)
        equipment_booking = EquipmentBooking.objects.create(
            club_member=self.user_member,
            reserved_equipment=equipment,
            booking_date_from=datetime.now() - timedelta(days=10),
            booking_date_to=datetime.now() - timedelta(days=5),
        )

        # Call the check_equipment_booking function
        count_bookings_before = EquipmentBooking.objects.count()
        check_equipment_booking()
        self.assertEqual(EquipmentBooking.objects.count(), count_bookings_before - 1)

        # Check if the correct record was deleted
        with self.assertRaises(EquipmentBooking.DoesNotExist):
            EquipmentBooking.objects.get(pk=equipment_booking.id)
