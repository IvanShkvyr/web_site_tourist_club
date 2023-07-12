import unittest
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from .models import Equipments, EquipmentsCategories, EquipmentBooking
from users.models import UserPositions
from .forms import EquipmentsCategoriesForm, EquipmentsForm


class EquipmentViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

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
            "equipment_category": equipment_category_test_2,
        }

        # Створення нового обладнання
        #  та перевірку на зміну регістру введених даних
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

        # Спроба додати екземпляр класу з даними з кількістю знаків менше min в полі equipment_name
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

        # Спроба додати екземпляр класу з даними з кількістю знаків більше max в полі equipment_name
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

        # Спроба додати екземпляр класу з даними менше 0 в полі weight_of_equipment_kg
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

        # Спроба додати екземпляр класу з даними з кількістю знаків менше min в полі equipment_description
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

        # Спроба додати екземпляр класу з даними з кількістю знаків більше max в полі equipment_description
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

        # Створення запису спорядження яке необхідно видалити
        category = EquipmentsCategories.objects.create(equipment_category_name="Category_2")
        equipment_del = Equipments.objects.create(
            equipment_name="New_equipment_3",
            weight_of_equipment_kg=120.3,
            equipment_description="new_equipment_3_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment_del.equipment_category.add(category)

        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/delete_equipment/{equipment_del.id}')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/delete_equipment.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:delete_equipment', args=[equipment_del.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/delete_equipment.html")

        # Перевірка чи спорядження яке необхідно видалити міститься в базі даних
        looking_for_equipment_first = Equipments.objects.get(equipment_name="New_equipment_3")
        self.assertIsNotNone(looking_for_equipment_first)
        
        # Видалення спорядження з бази даних
        response_del = self.client_equipment_manager.post(reverse("equipment:delete_equipment", args=[equipment_del.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("equipment:get_equipments"))

        # Перевірка чи спорядження яке видалити не міститься в базі даних
        deleted_equipment = Equipments.objects.filter(equipment_name="New_equipment_3").first()
        self.assertIsNone(deleted_equipment)

    # @unittest.skip
    def test_change_equipment(self):
        
        # Створення запису спорядження яке необхідно змінити
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
        
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/change_equipment/{equipment_old.id}')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/change_equipment.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:change_equipment', args=[equipment_old.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/change_equipment.html")
        
        # Зміна спорядження з базі даних
        response_che = self.client_equipment_manager.post(reverse("equipment:change_equipment", args=[equipment_old.id]), change_data)
        self.assertEqual(response_che.status_code, 302)
        self.assertRedirects(response_che, reverse("equipment:get_equipments"))

        # Перевірка змін в базі даних
        equipment_updated = Equipments.objects.get(id=equipment_old.id)
        self.assertEqual(equipment_updated.equipment_name, "New_equipment_5")
        self.assertEqual(equipment_updated.weight_of_equipment_kg, 120.5)
        self.assertEqual(equipment_updated.equipment_description, "new_equipment_4_description")

        # Спроба внесення змін з даними з кількістю знаків менше min в полі equipment_name
        change_data_less_min_name = {"equipment_name": "Ne"}

        form_less_min_name = EquipmentsForm(data=change_data_less_min_name)
        self.assertFalse(form_less_min_name.is_valid())

        # Спроба внесення змін з даними з кількістю знаків більше max в полі equipment_name
        long_value = "x" * 51
        change_data_greater_max_name = {"equipment_name": long_value}

        form_greater_max_name = EquipmentsForm(data=change_data_greater_max_name)
        self.assertFalse(form_greater_max_name.is_valid())

        # Спроба внесення змін з даними менше 0 в полі weight_of_equipment_kg
        change_data_negative_value_weight = {"weight_of_equipment_kg": -10}

        form_negative_value_weight = EquipmentsForm(data=change_data_negative_value_weight)
        self.assertFalse(form_negative_value_weight.is_valid())
        
        # Спроба внесення змін з даними з кількістю знаків менше min в полі equipment_description
        change_data_less_min_des = {"equipment_description": "Ne"}

        form_less_min_des = EquipmentsForm(data=change_data_less_min_des)
        self.assertFalse(form_less_min_des.is_valid())

        # Спроба внесення змін з даними з кількістю знаків більше max в полі equipment_description
        long_value_2 = "x" * 151
        change_data_greater_max_des = {"equipment_description": long_value_2}

        form_greater_max_des = EquipmentsForm(data=change_data_greater_max_des)
        self.assertFalse(form_greater_max_des.is_valid())

    # @unittest.skip
    def test_detail_equipment(self):

        # Отримання даних спорядження
        equipment_det = Equipments.objects.get(equipment_name="new_equipment_1")

        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/detail/{equipment_det.id}')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response_member.status_code, 200)
        self.assertTemplateUsed(response_member, "equipment_accounting/detail.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:detail_equipment', args=[equipment_det.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/detail.html")

        # Перевірка доступу до сторінки з неіснуючим обладнанням
        response_wrong = self.client_user_member.get(reverse("equipment:detail_equipment", args=[1000]))
        self.assertEqual(response_wrong.status_code, 404)

        # Перевірка на наявність правильних даних в відповіді
        self.assertContains(response_member, "new_equipment_1")
        self.assertContains(response_member, "120")
        self.assertContains(response_member, "new_equipment_1_description")
        self.assertContains(response_member, "default_tool.png")


class CategoruViewTest(TestCase):

    # @unittest.skip
    def setUp(self):
        User = get_user_model()

        # Авторизація користувача user_member
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

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

        # Створення екземпляра класа EquipmentsCategories
        EquipmentsCategories.objects.create(equipment_category_name="Category_1")

    # @unittest.skip
    def test_get_category(self):
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:get_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:get_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:get_category'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/category.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:get_category'))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/category.html")

        # Перевірка наявності екземпляру класа EquipmentsCategories
        category = EquipmentsCategories.objects.get(equipment_category_name="Category_1")
        self.assertEqual(EquipmentsCategories.objects.count(), 1)
        self.assertIsNotNone(category)
        self.assertEqual(category.equipment_category_name, "Category_1")
 
    # @unittest.skip
    def test_add_category(self):
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:add_category'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/add_category')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:add_category'))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:add_category'))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/add_category.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:add_category'))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/add_category.html")
        
        # Створення екземпляру класу з задовільними даними та перевірку на зміну регістру введених даних
        data = {"equipment_category_name": "CaTeGoRy2"}
        response_add = self.client_user_head.post(reverse("equipment:add_category"), data)
        self.assertEqual(response_add.status_code, 302)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertRedirects(response_add, reverse("equipment:get_category"))
        
        data = {"equipment_category_name": "Category3"}
        form = EquipmentsCategoriesForm(data=data)
        self.assertTrue(form.is_valid())

        # Спроба створення екземпляру класу з дублюванням даних
        data_twin = {"equipment_category_name": "Category2"}
        response_add_twin = self.client_user_head.post(reverse("equipment:add_category"), data_twin)
        self.assertEqual(response_add_twin.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_twin, "equipment_accounting/add_category.html")

        # Спроба створення екземпляру класу з даними з кількістю знаків менше min
        data_less_min = {"equipment_category_name": "Ca"}

        form_less_min = EquipmentsCategoriesForm(data=data_less_min)
        self.assertFalse(form_less_min.is_valid())

        response_add_less_min = self.client_user_head.post(reverse("equipment:add_category"), data_less_min)
        self.assertEqual(response_add_less_min.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_less_min, "equipment_accounting/add_category.html")

        # Спроба створення екземпляру класу з даними з кількістю знаків бідьше за max
        data_greater_max = {"equipment_category_name": "this_value_is_greater_than_twenty_symbols"}

        form_greater_max = EquipmentsCategoriesForm(data=data_greater_max)
        self.assertFalse(form_greater_max.is_valid())

        response_add_greater_max = self.client_user_head.post(reverse("equipment:add_category"), data_greater_max)
        self.assertEqual(response_add_greater_max.status_code, 200)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertTemplateUsed(response_add_greater_max, "equipment_accounting/add_category.html")

    # @unittest.skip
    def test_change_category(self):
        # Отримання екземпляру класу EquipmentsCategories
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category_1")
        
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/equipment/category/change_category/1')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/change_category.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:change_category', args=[category1.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/change_category.html")

        # Зміна даних екземпляру класу з задовільними даними
        change_data = {"equipment_category_name": "Change_Category1"}
        response_change = self.client_equipment_manager.post(reverse("equipment:change_category", args=[category1.id]), change_data)
        self.assertEqual(response_change.status_code, 302)
        self.assertRedirects(response_change, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "Change_Category1")

        # Зміна даних екземпляру класу з дублюванням даними
        change_data_twin = {"equipment_category_name": "Change_Category1"}
        response_change_twin = self.client_equipment_manager.post(reverse(
                                                                            "equipment:change_category",
                                                                            args=[category1.id]
                                                                            ), change_data_twin)
        self.assertEqual(response_change_twin.status_code, 200)
        self.assertTemplateUsed(response_change_twin, "equipment_accounting/change_category.html")

        # Зміна даних екземпляру класу з даними з кількістю знаків менше min
        change_data_less_min = {"equipment_category_name": "Ch"}
        response_change_less_min = self.client_equipment_manager.post(reverse(
                                                                            "equipment:change_category",
                                                                            args=[category1.id]
                                                                            ), change_data_less_min)
        self.assertEqual(response_change_less_min.status_code, 200)
        self.assertTemplateUsed(response_change_less_min, "equipment_accounting/change_category.html")
        self.assertNotEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "Ch")

        # Зміна даних екземпляру класу з даними з кількістю знаків більше max
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
        # Створення екземпляра класа EquipmentsCategories
        category_for_del = EquipmentsCategories.objects.create(equipment_category_name="Category_del")
        category_for_del_id = category_for_del.id
        
        # Перевірка доступу неавторизованого користувача
        response = self.client.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/equipment/category/delete_category/{category_for_del_id}')

        # Перевірка доступу авторизованого користувача user_member без дозволу додавати обладнання
        response_member = self.client_user_member.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_member.status_code, 302)
        self.assertRedirects(response_member, "/equipment/")

        # Перевірка доступу авторизованого користувача з дозволом від "Head"
        response_head = self.client_user_head.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_head.status_code, 200)
        self.assertTemplateUsed(response_head, "equipment_accounting/delete_category.html")

        # Перевірка доступу авторизованого користувача з дозволом від "Equipment_manager"
        response_equipment_manager = self.client_equipment_manager.get(reverse('equipment:delete_category', args=[category_for_del.id]))
        self.assertEqual(response_equipment_manager.status_code, 200)
        self.assertTemplateUsed(response_equipment_manager, "equipment_accounting/delete_category.html")
        
        # Перевірка видалення категорії авторизованим користувачем з дозволом від "Equipment_manager"
        count_categorys = EquipmentsCategories.objects.count()
        response_del = self.client_equipment_manager.post(reverse("equipment:delete_category", args=[category_for_del.id]))
        self.assertEqual(response_del.status_code, 302)
        self.assertRedirects(response_del, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.count(), count_categorys-1)


class EquipmentBookingViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

        # Авторизація користувача user_member
        self.client_user_member = Client()
        username_member = 'testuser_Member'
        password_member = 'testpassword_Member'
        self.user_member = User.objects.create_user(username=username_member, password=password_member)
        self.client_user_member.force_login(self.user_member)

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

        # створення екземпляра класу Equipments
        category = EquipmentsCategories.objects.create(equipment_category_name="Category_1")
        equipment = Equipments.objects.create(
            equipment_name="new_equipment_1",
            weight_of_equipment_kg=120,
            equipment_description="new_equipment_1_description",
            photo_of_equipment="default_tool.png",
            current_user=self.user_member,
        )
        equipment.equipment_category.add(category)

        # створення екземпляра класу EquipmentBooking
        equipment_booking_1 = EquipmentBooking.objects.create(
            booking_date_from = datetime.now(),
            booking_date_to = datetime.now() + timedelta(days=7)
        )

        equipment_booking_1.club_member.add(self.user_member)
        equipment_booking_1.reserved_equipment.add(equipment)







