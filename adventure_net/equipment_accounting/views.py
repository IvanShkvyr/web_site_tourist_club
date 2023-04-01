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


def get_equipments(request):
    pass


def add_equipment(request):
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST)
        print("3-----------------")
        print(form)
        print("4-----------------")
        if form.is_valid():

            print(form)
            print("5-----------------")
            data_equipment = form.save(commit=False)
            data_equipment.save()
            # choice_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist('categories'))
            # for category in choice_categories:
            #     data_equipment.equipment_category.add(category)

            return redirect(to='equipment:get_equipments')
        else:
            return render(
                            request,
                            "equipment_accounting/add_equipment.html",
                            context={"form": form, "categories": categories}
                        )
    return render(
                    request,
                    "equipment_accounting/add_equipment.html",
                    context={"form": EquipmentsForm(), "categories": categories}
                 )

    #         data_equipment_categorie = form.save(commit=False)
    #         data_equipment_categorie.save()
    #         return redirect(to='equipment:get_category')
    #     else:




def detail_equipment(request, category_id):
    pass


def change_equipment(request, category_id):
    pass


def delete_equipment(request, category_id):
    pass

