from django_filters import Filter
from django_filters.constants import EMPTY_VALUES
from django.db.models import Q
from django.db import models
from compute_marketplace.models import ComputeMarketplace
from model_marketplace.models import History_Build_And_Deploy_Model
from ml.models import MLBackend
class ListFilter(Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        value_list = value.split(",")
        qs = super().filter(qs, value_list)
        return qs


# n-level filter
def filterModel(self, queryset, model):
    # Search processing
    search = self.request.GET.get("search")
    if search:
        field_search = self.request.GET.get("fieldSearch")
        if field_search == "all":
            q_objects = Q()
            for field in model._meta.fields:
                if isinstance(field, (models.CharField, models.TextField)):
                    q_objects |= Q(**{f"{field.name}__icontains": search})
            queryset = queryset.filter(q_objects)
        elif field_search:
            q_objects = Q()
            for field in field_search.split(","):
                q_objects |= build_query(field, search)
            queryset = queryset.filter(q_objects)

    # Field Query processing
    field_query = self.request.GET.get("fieldQuery")
    value_query = self.request.GET.get("valueQuery")

    if field_query and value_query:
        field_queries = field_query.split(",")
        value_queries = value_query.split(",")

        # Ensure both arrays have the same length
        if len(field_queries) == len(value_queries):
            q_objects = Q()
            for field, value in zip(field_queries, value_queries):
                q_objects &= build_query(field, value)
            queryset = queryset.filter(q_objects)

    # Sort processing
    type_filter = self.request.GET.get("type")
    if type_filter:
        if model == ComputeMarketplace:
            queryset = queryset.filter(compute_type=type_filter)
        elif model == History_Build_And_Deploy_Model:
            queryset = queryset
        else:
            queryset = queryset.filter(type=type_filter)

    status_filter = self.request.GET.get("status")
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    sort = self.request.GET.get("sort")
    if sort:
        sort_params = sort.split(",")
        for sort_param in sort_params:
            field_name, order = sort_param.split("-")
            queryset = queryset.order_by(f"{'' if order == 'asc' else '-'}{field_name}")

    return queryset


def build_query(field, value):
    fields = field.split(".")
    q_objects = Q()

    if len(fields) > 1:
        # Assuming the first part is the JSONField and the rest are keys within the JSON
        field_path = fields[0]
        json_keys = fields[1:]

        # Construct the JSON field lookup
        json_lookup = "__".join(json_keys)
        q_objects &= Q(**{f"{field_path}__{json_lookup}__icontains": value})
    else:
        # Normal field lookup
        q_objects &= Q(**{f"{field}__icontains": value})

    return q_objects
