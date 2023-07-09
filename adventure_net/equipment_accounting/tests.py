import unittest
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from .models import Equipments, EquipmentsCategories, EquipmentBooking
from users.models import UserPositions
from .forms import EquipmentsCategoriesForm


class EquipmentViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

        # 


        # Авторизація користувача user_member
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

        # Авторизація користувача user_head
        self.client_user_head = Client()
        username_head = 'testuser_Head'
        password_head = 'testpassword_Head'
        self.user_head = User.objects.create_user(username=username_head, password=password_head)
        self.client_user_head.force_login(self.user_head)

        position_name_head = "Head"
        position_head, created = UserPositions.objects.get_or_create(positions_category=position_name_head)
        self.user_head.profile.user_position.add(position_head)

        # Авторизація користувача user_equipment_manager
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

        # 
        # booking = EquipmentBooking.objects.create(
        #     club_member=user,
        #     reserved_equipment=equipment,
        #     booking_date_from=datetime.now().date(),
        #     booking_date_to=datetime.now().date() + timedelta(days=7),
        #     )


    def test_get_equipments(self):
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:get_equipments'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/')

        # Перевірка доступу авторизованого користувача user_member
        response_member = self.client_user_member.get(reverse('equipment:get_equipments'))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/equipment.html")

        # Перевірка наявності обладнання
        equipment = Equipments.objects.get(equipment_name="new_equipment_1")
        self.assertEqual(Equipments.objects.count(), 1)
        self.assertIsNotNone(equipment)
        self.assertEqual(equipment.equipment_name, "new_equipment_1")

        # Перевірка користувача, який був авторизований
        self.assertEqual(response_member.context['user'], self.user_member)


    # @unittest.skip
    def test_add_equipment(self):
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:add_equipment'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/add_equipment/')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:add_equipment'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/add_equipment.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
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
            "equipment_category": [category.id for category in equipment_category_test_2],
        }
        
        # Створення нового обладнання
        # функція перевіряє регістр і повертає назву малими літерами з першою великою
        response_add_eq = self.client_user_head.post(reverse("equipment:add_equipment"), new_data)
        self.assertEqual(Equipments.objects.count(), 2)
        self.assertEqual(response_add_eq.status_code, 302)
        self.assertRedirects(response_add_eq, reverse("equipment:get_equipments"))

        # Перевірка на ім'я NeW_EqUiPmEnT_2 
        new_equipment_wrong = Equipments.objects.filter(equipment_name="NeW_EqUiPmEnT_2").first()
        self.assertIsNone(new_equipment_wrong)

        # Отримання об'єкта обладнання New_equipment_2 з бази даних
        new_equipment = Equipments.objects.get(equipment_name="New_equipment_2")

        # Перевірка значень обладнання
        self.assertEqual(new_equipment.equipment_name, "New_equipment_2")  
        self.assertEqual(new_equipment.weight_of_equipment_kg, 120.2)
        self.assertEqual(new_equipment.equipment_description, "new_equipment_2_description")
        self.assertEqual(new_equipment.photo_of_equipment, "default_tool.png")


#     @unittest.skip
#     def test_delete_equipment(self):

#         equipment_category = EquipmentsCategories.objects.get(equipment_category_name="Category1")
#         equipment = Equipments.objects.create(
#                                            equipment_name="new_equipment_3",
#                                            weight_of_equipment_kg=100,
#                                            photo_of_equipment="new_photo_3",
#                                            now_booked=True
#                                            )
#         equipment.equipment_category.set([equipment_category])

#         looking_for_equipment_first = Equipments.objects.get(equipment_name="new_equipment_3")
#         self.assertIsNotNone(looking_for_equipment_first)
        
#         response = self.client.post(reverse("equipment:delete_equipment", args=[equipment.id]))
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse("equipment:get_equipments"))

#         deleted_equipment = Equipments.objects.filter(equipment_name="new_equipment_3").first()
#         self.assertIsNone(deleted_equipment)

#         with self.assertRaises(Equipments.DoesNotExist):
#             Equipments.objects.get(equipment_name="new_equipment_3")

#     @unittest.skip
#     def test_change_equipment(self):
        
#         equipment_category = EquipmentsCategories.objects.get(equipment_category_name="Category1")
#         equipment_old = Equipments.objects.create(
#                                            equipment_name="new_equipment_old",
#                                            weight_of_equipment_kg=200,
#                                            photo_of_equipment="new_photo_old",
#                                            now_booked=True
#                                            )
#         equipment_old.equipment_category.set([equipment_category])

#         change_data = {
#             "equipment_name": "new_equipment_new",
#             "weight_of_equipment_kg": 202,
#             "photo_of_equipment": "new_photo_new",
#             "equipment_category": [EquipmentsCategories.objects.get(equipment_category_name="Category1")],
#             "now_booked":False,
#             }
        
#         response = self.client.post(reverse("equipment:change_equipment", args=[equipment_old.id]), change_data)

#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse("equipment:get_equipments"))

#         equipment_updated = Equipments.objects.get(id=equipment_old.id)

#         self.assertEqual(equipment_updated.equipment_name, "new_equipment_new")
#         self.assertEqual(equipment_updated.weight_of_equipment_kg, 202)
#         self.assertEqual(equipment_updated.photo_of_equipment, "new_photo_new")
#         self.assertEqual(equipment_updated.now_booked, False)

#     @unittest.skip
#     def test_detail_equipment(self):
#         equipment_category = EquipmentsCategories.objects.get(equipment_category_name="Category1")
#         equipment = Equipments.objects.create(
#                                            equipment_name="new_equipment_5",
#                                            weight_of_equipment_kg=104,
#                                            photo_of_equipment="new_photo_5",
#                                            now_booked=True
#                                            )
#         equipment.equipment_category.set([equipment_category])

#         response = self.client.post(reverse("equipment:detail_equipment", args=[equipment.id]))
#         response_wrong = self.client.post(reverse("equipment:detail_equipment", args=[1000]))

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response_wrong.status_code, 404)

#         self.assertContains(response, "new_equipment_5")
#         self.assertContains(response, "104")
#         self.assertContains(response, "new_photo_5")
#         self.assertContains(response, "True")

# class CategoruViewTest(TestCase):

#     @unittest.skip
#     def setUp(self):
#         EquipmentsCategories.objects.create(equipment_category_name="Category1")

#     @unittest.skip
#     def test_get_category(self):
#         response = self.client.get("/equipment/category/")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "equipment_accounting/category.html")
 
#     @unittest.skip
#     def test_add_category(self):
#         data = {"equipment_category_name": "Category2"}
#         response = self.client.post(reverse("equipment:add_category"), data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(EquipmentsCategories.objects.count(), 2)
#         self.assertRedirects(response, reverse("equipment:get_category"))

#     @unittest.skip
#     def test_valid_form(self):
#         data = {"equipment_category_name": "valid_value"}
#         form = EquipmentsCategoriesForm(data=data)
#         self.assertTrue(form.is_valid())

#     @unittest.skip
#     def test_max_length_of_category_name(self):
#         data = {"equipment_category_name": "this_value_is_greater_than_twenty_symbols"}
#         form = EquipmentsCategoriesForm(data=data)
#         self.assertFalse(form.is_valid())
#         response = self.client.post(reverse("equipment:add_category"), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "equipment_accounting/add_category.html")

#     @unittest.skip
#     def test_min_length_of_category_name(self):
#         data = {"equipment_category_name": "ab"}
#         form = EquipmentsCategoriesForm(data=data)
#         self.assertFalse(form.is_valid())
#         response = self.client.post(reverse("equipment:add_category"), data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "equipment_accounting/add_category.html")

#     @unittest.skip
#     def test_change_category(self):
#         category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
#         change_data = {"equipment_category_name": "ChangeCategory1"}
#         response = self.client.post(reverse("equipment:change_category", args=[category1.id]), change_data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse("equipment:get_category"))
#         self.assertEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "ChangeCategory1")

#     @unittest.skip
#     def test_delete_category(self):
#         category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
#         response = self.client.post(reverse("equipment:delete_category", args=[category1.id]))
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse("equipment:get_category"))
#         self.assertEqual(EquipmentsCategories.objects.count(), 0)









