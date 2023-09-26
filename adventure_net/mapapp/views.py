from django.shortcuts import render, redirect
from .models import ClubbingSpot
from .forms import KMLUploadForm


def map_view(request):
    if request.method == "POST":
        form = KMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            kml_file = form.cleaned_data["kml_file"]
            name_place = form.changed_data["name_spot"]
            water_access = form.cleaned_data["water_access"]
            description = form.cleaned_data["description"]

            club_place = ClubbingSpot.objects.create(
                name=name_place,
                water_access=water_access,
                description=description,
                kml_file=kml_file
            )
            club_place.save()

            return redirect('map_view')
    else:
        form = KMLUploadForm()

    club_places = ClubbingSpot.objects.all()

    return render(request, 'mapapp/map.html', {'form': form, 'club_places': club_places})


# def map_view(request):
#     return render(request, 'mapapp/map.html')