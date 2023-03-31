from django.shortcuts import render, redirect, get_object_or_404

from .forms import EquipmentsCategoriesForm
from .models import Equipments, EquipmentsCategories


def checker(request):
    return render(
        request,
        "equipment_accounting/checker.html",
        context={"msg": "Good news!!! It is working)"},
    )


def get_category(request):
    equipments = EquipmentsCategories.objects.all()
    return render(
                    request,
                    "equipment_accounting/category.html",
                    context={"equipments": equipments}
                )


def add_category(request):
    if request.method == "POST":
        form = EquipmentsCategoriesForm(request.POST)
        if form.is_valid():
            data_equipment_categorie = form.save(commit=False)
            data_equipment_categorie.save()
            return redirect(to='equipment:get_category')
        else:
            return render(
                            request,
                            "equipment_accounting/add_category.html",
                            context={"form": form}
                        )
    return render(
                    request,
                    "equipment_accounting/add_category.html",
                    context={"form": EquipmentsCategoriesForm()}
                 )


def change_category(request, category_id):
    category = get_object_or_404(EquipmentsCategories, pk=category_id)
    if request.method == "POST":
        form = EquipmentsCategoriesForm(request.POST)
        if form.is_valid():
            EquipmentsCategories.objects.filter(pk=category_id).update(
                equipment_category_name=request.POST["equipment_category_name"],
                )
            return redirect(to="equipment:get_category")
        else:
            return render(
                request, "equipment_accounting/change_category.html", context={"form": form}
            )
    return render(request, "equipment_accounting/change_category.html", context={"category": category})


def delete_category(request, category_id):
    if request.method == "POST":
        EquipmentsCategories.objects.filter(pk=category_id).delete()
        return redirect(to="equipment:get_category")
    return render(request, "equipment_accounting/delete_category.html")






