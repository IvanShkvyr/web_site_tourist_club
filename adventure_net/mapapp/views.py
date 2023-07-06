from django.shortcuts import render

def map_view(request):
    # Ваш код для відображення карти з використанням OpenLayers та шарів у форматі shp
    return render(request, 'mapapp/map.html')
