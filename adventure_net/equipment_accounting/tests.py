from django.test import TestCase
from django.urls import reverse
from .models import Equipments, EquipmentsCategories

class CheckerVeiwTest(TestCase):

    def test_checker(self):
        response = self.client.get("/equipment/checker/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Good news!!! It is working)", response.content.decode())


class EquipmentViewTest(TestCase):

    def test_get_equipments(self):
        response = self.client.get("/equipment/")
        self.assertEqual(response.status_code, 200)

    def test_add_equipment(self):
        response = self.client.get("/equipment/add_equipment/")
        self.assertEqual(response.status_code, 200)




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





