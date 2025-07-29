from rest_framework import serializers
from .models import Action_Point, User_Action_History, User_Point
import django_filters
from django.db.models import Q

class ActionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action_Point
        fields = '__all__'

class ActionPointFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Action_Point
        fields = ['search']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(activity__icontains=value) |
                Q(detail__icontains=value) |
                Q(customer__icontains=value) |
                Q(note__icontains=value)
            )
        return queryset

class UserActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Action_History
        fields = '__all__'

class UserActionHistoryFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user')
    action = django_filters.NumberFilter(field_name='action')
    order = django_filters.NumberFilter(field_name='order')
    point = django_filters.NumberFilter(field_name='point')
    status = django_filters.NumberFilter(field_name='status')
    created_by = django_filters.NumberFilter(field_name='created_by')
    note = django_filters.CharFilter(field_name='note')
    
    class Meta:
        model = User_Action_History
        fields = ['user', 'action', 'order', 'status', 'point', 'created_by', 'note']

    # def filter_search(self, queryset, name, value):
    #     if value:
    #         return queryset.filter(action__name__icontains=value)
    #     return queryset

class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Point
        fields = ['point']
