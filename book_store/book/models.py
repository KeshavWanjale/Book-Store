from django.db import models
from django.conf import settings

class Book(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    author = models.CharField(max_length=255, null=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=False)
    stock = models.PositiveIntegerField(null=False)

    def __str__(self):
        return self.name