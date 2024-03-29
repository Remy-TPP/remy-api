from distutils.util import strtobool

from requests.exceptions import RequestException
from django.shortcuts import get_object_or_404
from django.db.models import prefetch_related_objects
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.inventories.utils import get_place_or_default
from apps.inventories.models import InventoryItem
from apps.profiles.models import Event
from apps.recommendations.models import RecipeRecommendation
from apps.recommendations.serializers import RecipeRecommendationSerializer
from apps.recommendations.services import RemyRSService
from apps.recommendations.utils import ComparableInventory


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecipeRecommendationSerializer
    search_fields = ['recipe__title', 'recipe__description']

    # TODO: probably needs to call self.filter_queryset() to actually search
    def get_queryset(self, profile_ids=None):
        # TODO: actually returns a list, fix wording?
        if not profile_ids:
            recommendations = RemyRSService.get_recommendations_for_user(
                profile_id=self.request.user.profile.id,
                n='all',
            )
        else:
            recommendations = RemyRSService.get_recommendations_for_group(
                profile_ids=profile_ids,
                n='all',
            )

        recommendations = [
            RecipeRecommendation(
                recipe_id=r['recipe_id'],
                rating=r['rating'],
                rating_is_real=r['real']
            )
            for r in recommendations
        ]
        return recommendations

    def filter_on_users_restrictions(self, recommendations, profiles):
        """ Exclude recommendations that have a forbidden ingredient or not in users' categories. """
        filtered_recs = []

        # TODO: maybe another prefetch (for the forbidden_products & profiletypes) would be a good idea
        forbidden_products_pks = {product.pk for profile in profiles for product in profile.forbidden_products.all()}
        restrictions = {profiletype.name.lower() for profile in profiles for profiletype in profile.profiletypes.all()}

        for recommendation in recommendations:
            recipe_product_pks_set = {product.pk for product in recommendation.recipe.ingredients.all()}
            # check if there's any forbidden product in recipe
            if any(ppk in recipe_product_pks_set for ppk in forbidden_products_pks):
                continue
            if recommendation.recipe.dish:
                dish_categories = {category.name.lower() for category in recommendation.recipe.dish.categories.all()}
            else:
                dish_categories = set()
            # check all profile types are respected
            if not all(restriction in dish_categories for restriction in restrictions):
                continue
            filtered_recs.append(recommendation)

        return filtered_recs

    def filter_on_ingredients(self, recommendations, inventory):
        user_inventory = inventory.all().prefetch_related('product', 'unit')
        inv = ComparableInventory(inventory_items=user_inventory)

        return [rec for rec in recommendations if inv.can_make(rec.recipe)]

    def postprocess_recommendations(self, recommendations, inventory, profiles=None,
                                    need_all_ingredients=False, ignore_restrictions=False):
        if not profiles:
            profiles = [self.request.user.profile]

        # TODO: more optimization can be made here
        prefetch_related_objects(
            recommendations,
            'recipe__dish__categories', 'recipe__ingredients',
            'recipe__ingredient_set__product', 'recipe__ingredient_set__unit')

        filtered_recs = (recommendations
                         if ignore_restrictions
                         else self.filter_on_users_restrictions(recommendations, profiles))

        filtered_recs = (filtered_recs
                         if not need_all_ingredients
                         else self.filter_on_ingredients(filtered_recs, inventory))

        return filtered_recs

    def _send_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_summary='Get recommended recipes for current user',
        manual_parameters=[
            openapi.Parameter(
                'place_id',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default is used.',
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'need_all_ingredients',
                in_=openapi.IN_QUERY,
                description="Whether place must have all of a recipe's ingredients for the recipe to be recommended.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
                default=False,
            ),
            openapi.Parameter(
                'ignore_restrictions',
                in_=openapi.IN_QUERY,
                description="Whether to ignore user's restrictions, i.e. profile types and forbidden ingredients.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
                default=False,
            ),
        ],
    )
    @action(detail=False, methods=['GET'], url_path='recommend/recipes/me', url_name='recommend-recipes-me')
    def recommend_recipes_me(self, request):
        need_all_ingredients = strtobool(self.request.query_params.get('need_all_ingredients', 'false'))
        ignore_restrictions = strtobool(self.request.query_params.get('ignore_restrictions', 'false'))
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place_id'))

        if need_all_ingredients and not place:
            return Response({"error": "You don't have a place"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = self.get_queryset()
        except (RequestException, RemyRSService.RecSysException) as rs_error:
            return Response({"error": repr(rs_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        queryset = self.postprocess_recommendations(
            queryset,
            place.inventory.all() if (place and place.inventory) else None,
            need_all_ingredients=need_all_ingredients,
            ignore_restrictions=ignore_restrictions,
        )
        return self._send_queryset(queryset)

    @swagger_auto_schema(
        method='get',
        operation_summary='Get recommended recipes for event',
        manual_parameters=[
            openapi.Parameter(
                'id',
                in_=openapi.IN_QUERY,
                description='Id of event for whose users to generate recommendations.',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                'need_all_ingredients',
                in_=openapi.IN_QUERY,
                description="Whether must have all of a recipe's ingredients for the recipe to be recommended.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
                default=False,
            ),
            openapi.Parameter(
                'ignore_restrictions',
                in_=openapi.IN_QUERY,
                description="Whether to ignore attendees' restrictions, i.e. profile types & forbidden ingredients.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
                default=False,
            ),

        ],
    )
    @action(detail=False, methods=['GET'], url_path='recommend/recipes/event', url_name='recommend-recipes-event')
    def recommend_recipes_event(self, request):
        event_id = request.query_params.get('id', None)
        need_all_ingredients = strtobool(request.query_params.get('need_all_ingredients', 'false'))
        ignore_restrictions = strtobool(self.request.query_params.get('ignore_restrictions', 'false'))

        event = get_object_or_404(Event.objects.all(), id=event_id)

        if need_all_ingredients and not event.place:
            return Response({"error": "Event doesn't have a place"}, status=status.HTTP_400_BAD_REQUEST)

        # always include event's place's inventory (which should be the host's)
        places_pk = set([event.place.pk])
        if not event.only_host_inventory:
            # add each non-host member's inventory, without duplicates
            for attendee in event.attendees.all():
                # TODO: assumes event's place is from the host so that we can ignore them here; is this right?
                if attendee != event.host:
                    places_pk.add(attendee.default_place.pk)
        event_inventory = InventoryItem.objects.filter(place__in=places_pk)

        try:
            queryset = self.get_queryset(profile_ids=[attendee.pk for attendee in event.attendees.all()])
        except (RequestException, RemyRSService.RecSysException) as rs_error:
            return Response({"error": repr(rs_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        queryset = self.postprocess_recommendations(
            queryset,
            event_inventory,
            profiles=event.attendees.all(),
            need_all_ingredients=need_all_ingredients,
            ignore_restrictions=ignore_restrictions,
        )
        return self._send_queryset(queryset)
