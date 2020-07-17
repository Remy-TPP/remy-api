from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=50, unique=True, null=True)

    def __str__(self):
        return self.name


def unit_default():
    return Unit.objects.get(name='unit')


class Amount(models.Model):
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=unit_default)

    def __str__(self):
        return f'{self.displayable_quantity()} {self.unit.short_name}'

    def displayable_quantity(self):
        return round(self.quantity, 2)


class Product(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name
