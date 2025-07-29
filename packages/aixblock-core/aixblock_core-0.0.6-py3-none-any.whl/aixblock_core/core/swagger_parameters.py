from drf_yasg import openapi

page_parameter = openapi.Parameter(name='page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY)
search_parameter = openapi.Parameter(name='search', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY, description="Search query")
field_search_parameter = openapi.Parameter(
    name="fieldSearch",
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING),
    in_=openapi.IN_QUERY,
    description="Fields to search (e.g:compute_marketplace.config.name,compute_gpu.name )",
)
field_query_parameter = openapi.Parameter(
    name="fieldQuery",
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING),
    in_=openapi.IN_QUERY,
    description="Fields to filter by. Example format: ['compute_marketplace.config.name', 'compute_gpu.name']",
)

query_value_parameter = openapi.Parameter(
    name="valueQuery",
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING),
    in_=openapi.IN_QUERY,
    description="Values corresponding to the fields in fieldQuery. Example format: ['GTX 1080', 'RTX 3090']",
)

sort_parameter = openapi.Parameter(name='sort', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), in_=openapi.IN_QUERY, description="Sorting criteria (e.g., name-desc,ml_id-asc)")
type_parameter =  openapi.Parameter(name='type', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY)
status_parameter =  openapi.Parameter(name='status', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY)
infrastructure_id =  openapi.Parameter(name='infrastructure_id', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY)
compute_gpu_id_parameter = openapi.Parameter(
    name='compute_gpu_id',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    required=True,
    description='ID of the compute GPU.'
)

token_symbol_parameter = openapi.Parameter(
    name='token_symbol',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    required=True,
    description='Token symbol for the price.'
)

price_parameter = openapi.Parameter(
    name='price',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_NUMBER,
    required=True,
    description='Price of the compute GPU.'
)
