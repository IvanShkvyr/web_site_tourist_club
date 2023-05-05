from django.test import TestCase
from django.urls import reverse
from .models import EquipmentsCategories


class EquipmentsCategoriesTests(TestCase):
    def setUp(self):
        EquipmentsCategories.objects.create(equipment_category_name="Category1")
        EquipmentsCategories.objects.create(equipment_category_name="Category2")

    def test_get_category(self):
        response = self.client.get(reverse("equipment:get_category"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["categories"], 
            ["<EquipmentsCategories: Category1>", "<EquipmentsCategories: Category2>"]
        )
        self.assertTemplateUsed(response, "equipment_accounting/category.html")

    def test_add_category(self):
        data = {"equipment_category_name": "Category3"}
        response = self.client.post(reverse("equipment:add_category"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.count(), 3)

    def test_change_category(self):
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
        data = {"equipment_category_name": "ChangedCategory1"}
        response = self.client.post(reverse("equipment:change_category", args=[category1.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.get(id=category1.id).equipment_category_name, "ChangedCategory1")

    def test_delete_category(self):
        category1 = EquipmentsCategories.objects.get(equipment_category_name="Category1")
        response = self.client.post(reverse("equipment:delete_category", args=[category1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("equipment:get_category"))
        self.assertEqual(EquipmentsCategories.objects.count(), 1)
