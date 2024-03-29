from django.db import models

class ClubbingSpot(models.Model):
    name_spot = models.CharField(max_length=100, null=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    water_access = models.BooleanField()
    description = models.CharField(max_length=255)
    kml_file = models.FileField(upload_to="kml_files", null=False)

    def __str__(self):
        return self.name_spot