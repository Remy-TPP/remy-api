from rest_framework import serializers

from apps.products.models import Unit, Amount, Product


class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'


class AmountSerializer(serializers.ModelSerializer):
    unit = serializers.SlugRelatedField(slug_field='name', queryset=Unit.objects.all())

    class Meta:
        model = Amount
        fields = '__all__'


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'