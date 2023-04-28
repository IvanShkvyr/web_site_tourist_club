from django.shortcuts import render, redirect, get_object_or_404

from .forms import EquipmentsForm, EquipmentsCategoriesForm
from .models import Equipments, EquipmentsCategories


def checker(request):
    return render(
        request,
        "equipment_accounting/checker.html",
        context={"msg": "Good news!!! It is working)"},
    )


def get_category(request):
    categories = EquipmentsCategories.objects.all()
    return render(
                    request,
                    "equipment_accounting/category.html",
                    context={"categories": categories}
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


def get_equipments(request):
    equipments = Equipments.objects.all()
    return render(
                    request,
                    "equipment_accounting/equipment.html",
                    context={"equipments": equipments}
                )


def add_equipment(request):
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST)
        if form.is_valid():
            equipments = form.save()
            choise_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist("categories"))
            for category in choise_categories:
                equipments.equipment_category.add(category)

            return redirect(to="equipment:get_equipments")
        else:
            return render(request, "equipment_accounting/add_equipment.html", context={'form': form, 'categories': categories})
    return render(request, "equipment_accounting/add_equipment.html", context={'form': EquipmentsForm(), 'categories': categories})


def detail_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    return render(request, 'equipment_accounting/detail.html', context={'equipment': equipment})


def change_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    if request.method == "POST":
        form = EquipmentsForm(request.POST)
        if form.is_valid():

            Equipments.objects.filter(pk=equipment_id).update(
                equipment_name=request.POST["equipment_name"],
                weight_of_equipment_kg=request.POST["weight_of_equipment_kg"],
                photo_of_equipment=request.POST["photo_of_equipment"],
                now_booked=request.POST["now_booked"],
                )
            return redirect(to="equipment:get_equipments")
        else:
            return render(
                request, "equipment_accounting/change_equipment.html", context={"form": form}
            )
    return render(request, "equipment_accounting/change_equipment.html", context={"equipment": equipment})


def delete_equipment(request, equipment_id):
    if request.method == "POST":
        Equipments.objects.filter(pk=equipment_id).delete()
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/delete_equipment.html")



