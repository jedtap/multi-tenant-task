from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='tenant_logos/',  blank=True, null=True)

    def __str__(self):
        return self.name
