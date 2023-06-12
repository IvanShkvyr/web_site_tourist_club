from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import EquipmentsForm, EquipmentsCategoriesForm
from .models import Equipments, EquipmentsCategories


@login_required(login_url='/login/')
def checker(request):
    return render(
        request,
        "equipment_accounting/checker.html",
        context={"msg": "Good news!!! It is working)"},
    )


@login_required(login_url='/login/')
def get_category(request):
    categories = EquipmentsCategories.objects.all()
    return render(
                    request,
                    "equipment_accounting/category.html",
                    context={"categories": categories}
                )


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def delete_category(request, category_id):
    if request.method == "POST":
        EquipmentsCategories.objects.filter(pk=category_id).delete()
        return redirect(to="equipment:get_category")
    return render(request, "equipment_accounting/delete_category.html")


@login_required(login_url='/login/')
def get_equipments(request):
    equipments = Equipments.objects.all()
    return render(
                    request,
                    "equipment_accounting/equipment.html",
                    context={"equipments": equipments}
                )



@login_required(login_url='/login/')
def add_equipment(request):
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.save()

            choise_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist("categories"))
            for category in choise_categories:
                equipment.equipment_category.set([category])


            return redirect(to="equipment:get_equipments")
        else:
            return render(request, "equipment_accounting/add_equipment.html", context={'form': form, 'categories': categories})
    return render(request, "equipment_accounting/add_equipment.html", context={'form': EquipmentsForm(), 'categories': categories})


@login_required(login_url='/login/')
def detail_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    return render(request, 'equipment_accounting/detail.html', context={'equipment': equipment})


@login_required(login_url='/login/')
def change_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipments, pk=equipment_id)
    categories = EquipmentsCategories.objects.all()
    if request.method == "POST":
        form = EquipmentsForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():

            equipment = form.save(commit=False)
            equipment.save()

            choise_categories = EquipmentsCategories.objects.filter(equipment_category_name__in=request.POST.getlist("categories"))
            for category in choise_categories:
                equipment.equipment_category.set([category])


            return redirect(to="equipment:get_equipments")
        else:
            return render(
                request, "equipment_accounting/change_equipment.html", context={"form": form, 'categories': categories}
            )
    return render(request, "equipment_accounting/change_equipment.html", context={"equipment": equipment, 'categories': categories})


@login_required(login_url='/login/')
def delete_equipment(request, equipment_id):
    if request.method == "POST":
        Equipments.objects.filter(pk=equipment_id).delete()
        return redirect(to="equipment:get_equipments")
    return render(request, "equipment_accounting/delete_equipment.html")




@login_required(login_url='/login/')
def book_equipment(request, equipment_id):
    return render(
        request,
        "equipment_accounting/book_equipment.html",
        context={"msg": "Good news!!! Book equipment is working)"},
    )


@login_required(login_url='/login/')
def cancel_equipment_reservation(request, equipment_id):
    return render(
        request,
        "equipment_accounting/cancel_equipment_reservation.html",
        context={"msg": "Good news!!! Сancel equipment reservation is working)"},
        )



