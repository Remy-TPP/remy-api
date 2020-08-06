from django.db import models

from apps.products.utils import sub_quantities_with_units


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=50, unique=True, null=True)

    def __str__(self):
        return self.name

    # TODO: revisit later
    @property
    def pluralized_name(self):
        return self.name + 's'


def unit_default():
    return Unit.objects.get_or_create(name='unit', short_name='')[0].pk


class Amount(models.Model):
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=unit_default)

    def __str__(self):
        return f'{self.displayable_quantity}{self.displayable_unit}'

    def __sub__(self, other):
        """Decrease own quantity with other's.

        Returns True if this amount is no longer usable.
        """
        quantity_result = sub_quantities_with_units(self.quantity, self.unit.name, other.quantity, other.unit.name)
        self.quantity = quantity_result
        self.save()
        return quantity_result <= 0

    @property
    def displayable_unit(self):
        if self.unit.short_name is None:
            return f' {self.unit.name if self.quantity == 1.0 else self.unit.pluralized_name}'

        if self.unit.short_name == '':
            return ''

        return f' {self.unit.short_name}'

    @property
    def displayable_quantity(self):
        return self.quantity


class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name