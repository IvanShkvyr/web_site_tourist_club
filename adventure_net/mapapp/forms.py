from django import forms


class KMLUploadForm(forms.Form):
    kml_file = forms.FileField(label="Завантажити KML файл")
    name_spot = forms.CharField(max_length=100, min_length=3, required=True)
    water_access = forms.BooleanField(label='Доступ до води')
    description = forms.CharField(widget=forms.Textarea)

