from django.db import models

class Locations(models.Model): #Производственный участок
    name = models.CharField(max_length=100, null=False, primary_key=True)

class Equipment(models.Model): #Оборудование
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    locations = models.ForeignKey(Locations, on_delete=models.CASCADE)
