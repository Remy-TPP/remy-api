from django.http import HttpResponse
from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q
from django.db.transaction import atomic, savepoint, savepoint_commit, savepoint_rollback
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import qrcode

from apps.inventories.utils import get_place_or_default

from apps.inventories.models import (Place,
                                     InventoryItem,
                                     PlaceMember,
                                     Purchase,
                                     )
from apps.inventories.serializers import (PlaceSerializer,
                                          InventoryItemSerializer,
                                          PurchaseSerializer,
                                          )


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all the places the user has.",
    operation_description="Returns places."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the place with id={id}..",
    operation_description="Returns place."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates a place for that user.",
    operation_description="Returns place."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates place with id={id}.",
    operation_description="Returns place."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates place with id={id}.",
    operation_description="Returns place."
))
class PlaceViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    serializer_class = PlaceSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Place.objects.filter(members=user.profile).order_by("id")


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all items that place has.",
    operation_description="Returns items.",
    manual_parameters=[
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER
        ),
    ]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the item with id={id}..",
    operation_description="Returns item."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes item with id={id}.",
    operation_description="Returns none."
))
class InventoryItemViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    serializer_class = InventoryItemSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        place = get_place_or_default(self.request.user.profile, self.kwargs.get('place_pk'))
        return InventoryItem.objects.filter(place=place).order_by('id')

    @swagger_auto_schema(
        operation_summary="Create an item for that place.",
        operation_description="Returns the item.",
        manual_parameters=[
            openapi.Parameter(
                'place_id',
                in_=openapi.IN_QUERY,
                description='ID of a place',
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        place = get_place_or_default(request.user.profile, kwargs.get('place_pk'))

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if place:
                # place_id is correct for this user or has default one
                serializer.save(place=place)
            else:
                # user does not have a place yet
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                'msg': "Cannot add Item!",
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_summary='Create a list of items for that place.',
        operation_description='Choose a place you are member as a default place',
        manual_parameters=[
            openapi.Parameter(
                'place_id',
                in_=openapi.IN_QUERY,
                description='ID of a place',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['POST'])
    @atomic
    def add_items(self, request):
        sid = savepoint()
        if 'items' not in request.data:
            return Response({'message': 'Should provide items key!'}, status=status.HTTP_400_BAD_REQUEST)

        for item in request.data.get('items'):
            # TODO: mejorar para que no tenga que pedir el place siempre
            place = get_place_or_default(request.user.profile, request.query_params.get('place_pk'))

            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                if place:
                    # place_id is correct for this user or has default one
                    serializer.save(place=place)
                else:
                    # user does not have a place yet
                    serializer.save()
            else:
                savepoint_rollback(sid)
                return Response(
                    {
                        'msg': "Cannot add Item!",
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        savepoint_commit(sid)
        return Response({'message': 'All the items were created!'}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_summary='Default place',
    operation_description='Choose a place you are member as a default place',
    manual_parameters=[
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@api_view(['POST'])
def default_place(request):
    place_id = request.query_params.get('place_id')

    if place_id:
        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(is_the_default_one=True)
        ).update(is_the_default_one=False)

        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(place_id=place_id)
        ).update(is_the_default_one=True)
        return Response({'message': 'Your place has changed!'}, status=status.HTTP_200_OK)
    return Response({'message': 'place_id must be provided!'}, status=status.HTTP_400_BAD_REQUEST)


# TODO: swagger schema
class PurchaseDetailView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field = 'pk'
    permission_classes = []


# TODO: swagger schema
class PurchaseCreateView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    lookup_field = 'pk'
    permission_classes = []

    # TODO: move to utils, no?
    def _url_to_qr_image(self, url_str):
        return qrcode.make(url_str)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            try:
                qr_img = self._url_to_qr_image(serializer.data['url'])
                image_response = HttpResponse(content_type="image/jpeg")
                qr_img.save(image_response, "JPEG")
                return image_response

            except KeyError:
                # TODO: error catch is too specific? lack of message too vague?
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
