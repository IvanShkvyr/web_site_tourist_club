import unittest

from django.test import TestCase
from django.urls import reverse
from .models import Equipments, EquipmentsCategories
from .forms import EquipmentsCategoriesForm

class CheckerVeiwTest(TestCase):

    def test_checker(self):
        response = self.client.get("/equipment/checker/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Good news!!! It is working)", response.content.decode())


class EquipmentViewTest(TestCase):

    def setUp(self):
        category = EquipmentsCategories.objects.create(equipment_category_name="Category1")
        equipment = Equipments.objects.create(
            equipment_name="new_equipment",
            weight_of_equipment_kg=120,
            photo_of_equipment="new_photo",
            now_booked=True,
        )
        equipment.equipment_category.add(category)

    def test_get_equipments(self):
        response = self.client.get("/equipment/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment_accounting/equipment.html")
        self.assertEqual(Equipments.objects.count(), 1)

        equipment = Equipments.objects.get(equipment_name="new_equipment")

        self.assertIsNotNone(equipment)
        self.assertEqual(equipment.equipment_name, "new_equipment")

    # @unittest.skip
    def test_add_equipment(self):

        response = self.client.get("/equipment/add_equipment/")
        data = {
            "equipment_name": "new_equipment_2",
            "weight_of_equipment_kg": 123,
            "photo_of_equipment": "new_photo_2",
            "equipment_category": [EquipmentsCategories.objects.get(equipment_category_name="Category1")],
            "now_booked":True,
            }
        
        self.assertEqual(response.status_code, 200)

        new_response = self.client.post(reverse("equipment:add_equipment"), data)

        self.assertEqual(new_response.status_code, 302)
        self.assertEqual(Equipments.objects.count(), 2)
        self.assertRedirects(new_response, reverse("equipment:get_equipments"))

        equipment = Equipments.objects.get(equipment_name="new_equipment_2")

        self.assertEqual(equipment.equipment_name, "new_equipment_2")
        self.assertEqual(equipment.weight_of_equipment_kg, 123)
        self.assertEqual(equipment.photo_of_equipment, "new_photo_2")
        self.assertEqual(equipment.now_booked, True)

    # @unittest.skip
    def test_delete_equipment(self):

        equipment_category = EquipmentsCategories.objects.get(equipment_category_name="Category1")
        equipment = Equipments.objects.create(
                                           equipment_name="new_equipment_3",
                                           weight_of_equipment_kg=100,
                                           photo_of_equipment="new_photo_3",
                                           now_booked=True
                                           )
        equipment.equipment_category.set([equipment_category])

        looking_for_equipment_first = Equipments.objects.get(equipment_name="new_equipment_3")
        self.assertIsNotNone(looking_for_equipment_first)
        
        response = self.client.post(reverse("equipment:delete_equipment", args=[equipment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_equipments"))

        deleted_equipment = Equipments.objects.filter(equipment_name="new_equipment_3").first()
        self.assertIsNone(deleted_equipment)

        with self.assertRaises(Equipments.DoesNotExist):
            Equipments.objects.get(equipment_name="new_equipment_3")

    def test_change_equipment(self):
        pass

    def test_detail_equipment(self):
        pass

    # def detail_equipment(request, equipment_id):
    # equipment = get_object_or_404(Equipments, pk=equipment_id)
    # return render(request, 'equipment_accounting/detail.html', context={'equipment': equipment})


class CategoruViewTest(TestCase):

    def setUp(self):
        EquipmentsCategories.objects.create(equipment_category_name="Category1")

    def test_get_category(self):
        response = self.client.get("/equipment/category/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment_accounting/category.html")
 
    def test_add_category(self):
        data = {"equipment_category_name": "Category2"}
        response = self.client.post(reverse("equipment:add_category"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EquipmentsCategories.objects.count(), 2)
        self.assertRedirects(response, reverse("equipment:get_category"))

    def test_valid_form(self):
        data = {"equipment_category_name": "valid_value"}
        form = EquipmentsCategoriesForm(data=data)
        self.assertTrue(form.is_valid())

    def test_max_length_of_category_name(self):
        data = {"equipment_category_name": "this_value_is_greater_than_twenty_symbols"}
        form = EquipmentsCategoriesForm(data=data)
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse("equipment:add_category"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment_accounting/add_category.html")

    def test_min_length_of_category_name(self):
        data = {"equipment_category_name": "ab"}
        form = EquipmentsCategoriesForm(data=data)
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse("equipment:add_category"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment_accounting/add_category.html")

    def test_change_category(self):
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
        change_data = {"equipment_category_name": "ChangeCategory1"}
        response = self.client.post(reverse("equipment:change_category", args=[category1.id]), change_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "ChangeCategory1")

    def test_delete_category(self):
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
        response = self.client.post(reverse("equipment:delete_category", args=[category1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.count(), 0)



# # cd adventure_net
# # python manage.py test equipment_accounting





