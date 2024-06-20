from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.CharField(max_length=50)
    categorie = models.CharField(max_length=100, default='Uncategorized')

    def __str__(self):
        return self.name