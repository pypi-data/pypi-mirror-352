from .serializers import (
    ComputeGpuSerializer, TradeResourceSerializer, ComputeGpuPriceSerializer, BulkComputeGpuSerializer,GpuPriceDataSerializer, CpuPriceDataSerializer, PriceSerializer, RecommendPriceSerializer
)
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from .models import ComputeGPU, Trade, Portfolio, ComputeGpuPrice, ComputeMarketplace, History_Rent_Computes, ComputeMarketplace, Recommend_Price
from core.permissions import ViewClassPermission, all_permissions
from core.utils.paginate import SetPagination
import drf_yasg.openapi as openapi
from core.swagger_parameters import page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter, status_parameter, infrastructure_id, compute_gpu_id_parameter, token_symbol_parameter, price_parameter
from core.filters import filterModel
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from django.db.models import Prefetch
from datetime import datetime
import threading
from django.conf import settings

from rest_framework.views import APIView
from orders.models import Order, OrderComputeGPU
from core.utils.convert_memory_to_byte import (
    convert_mb_to_gb,
    convert_to_bytes,
    convert_mb_to_byte,
    convert_gb_to_byte,
)
from .system_info import update_compute_marketplace

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='List Compute Gpu',
    manual_parameters=[page_parameter, search_parameter, field_search_parameter, sort_parameter, type_parameter, status_parameter, infrastructure_id]
    
)) 
class ListComputeGpuApi(generics.ListAPIView):
    serializer_class = ComputeGpuSerializer
    pagination_class = SetPagination

    def get_queryset(self):
        queryset = ComputeGPU.objects.select_related('infrastructure_id').prefetch_related(
            Prefetch('prices', queryset=ComputeGpuPrice.objects.all(), to_attr='gpu_prices')
        )
        if settings.DJANGO_DB == "sqlite":
            queryset = queryset.distinct("infrastructure_id")
        else:
            # SQLite không hỗ trợ distinct('field'), nên loại trùng bằng set()
            queryset = list({obj["infrastructure_id"]: obj for obj in queryset.values("infrastructure_id")}.values())
        
        infrastructure_id_value = self.request.query_params.get('infrastructure_id')

        if infrastructure_id_value:
            queryset = queryset.filter(infrastructure_id=infrastructure_id_value)

        # Áp dụng bộ lọc thông qua hàm filterModel
        return filterModel(self, queryset, ComputeGPU)

    def get(self, request, *args, **kwargs):
        return super(ListComputeGpuApi, self).get(request, *args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Create Compute Gpu',
))
class CreateComputeGpuApi(generics.CreateAPIView):
    serializer_class = ComputeGpuSerializer
    queryset = ComputeGPU.objects.all()
    def post(self, request, *args, **kwargs):
        infrastructure_id = self.request.data.get('infrastructure_id')
        gpu_index = self.request.data.get('gpu_index')
        gpu_card = ComputeGPU.objects.filter(infrastructure_id=infrastructure_id, gpu_index=gpu_index).first()
        if gpu_card:
            return Response({'error': 'Gpu Card is existed'}, status=400)
        return super(CreateComputeGpuApi, self).post(request, *args, **kwargs)

@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Update Compute Gpu',
))
class UpdateComputeGpuApi(generics.UpdateAPIView):
    serializer_class = ComputeGpuSerializer
    queryset = ComputeGPU.objects.all()
    permission_required = ViewClassPermission(
        PATCH=all_permissions.projects_change,
    )
    redirect_kwarg = 'pk'
    def patch(self, request, *args, **kwargs):
        computegpu = ComputeGPU.objects.filter(pk=kwargs['pk']).first()
        if not computegpu:
            return Response({'error': 'Compute Gpu not found'}, status=404)
        return super(UpdateComputeGpuApi, self).patch(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(UpdateComputeGpuApi, self).put(request, *args, **kwargs)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Trade/Rent Compute Gpu',
))
class RentComputeByGpuCardApi(generics.CreateAPIView):
    serializer_class = TradeResourceSerializer
    queryset = Trade.objects.all()

    def post(self, request, *args, **kwargs):
        compute_gpu_id = self.request.data.get('compute_gpu_id')
        compute_id = self.request.data.get('compute_id')

        compute = ComputeMarketplace.objects.filter(id=compute_id).first()
        user_id = self.request.user.id
        token_symbol = self.request.data.get('token_symbol')
        portfolio = Portfolio.objects.filter(account_id=user_id, token_symbol=token_symbol).first()

        if not portfolio:
            return Response({'error': 'Portfolio not found'}, status=404)

        if compute and compute.is_using_cpu:
            compute_gpu_trade = Trade.objects.filter(resource='compute_cpu', resource_id=compute_id, status='renting').first()
            if compute_gpu_trade:
                return Response({'error': 'Compute CPU is already rented'}, status=400)

            computeGpuPrice = ComputeGpuPrice.objects.filter(compute_marketplace_id=compute_id, token_symbol=token_symbol).first()

            if computeGpuPrice:
                compute_gpu = ComputeGPU.objects.filter(id = compute_gpu_id).first()
                order_instance = Order.objects.create(
                    total_amount=1,
                    price=computeGpuPrice.price,
                    unit=token_symbol,
                    status="completed",
                    user_id=user_id
                )
                OrderComputeGPU.objects.create(
                    order_id=order_instance.id, compute_gpu_id=compute_gpu.id
                )
                price = computeGpuPrice.price
                # amount = price * 0.9 if (timezone.now() - compute.created_at) < timedelta(days=30) else price
                amount = price
                portfolio.amount_holding -= amount
                portfolio.save()

                request.data["resource_id"] = compute_gpu_id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=False)
                serializer.validated_data['price'] = price
                serializer.validated_data['amount'] = amount
                serializer.validated_data['account_id'] = user_id
                serializer.validated_data['resource'] = 'compute_marketplace' #with cpu
                serializer.validated_data['resource_id'] = compute_id #with cpu
                serializer.orders = order_instance.id
                self.perform_create(serializer)
                order_instance.status = "completed"
                order_instance.save()

                ComputeMarketplace.objects.filter(pk=compute.id).update(status="rented_bought")
                History_Rent_Computes.objects.create(account_id=user_id, compute_marketplace_id=compute.id,  status="renting")

                return Response(serializer.data, status=201)
            else:
                return Response({'error': 'ComputeGpuPrice not found'}, status=404)
        else:
            compute_gpu_trade = Trade.objects.filter(resource='compute_gpu', resource_id=compute_gpu_id, status='renting').first()
            if compute_gpu_trade:
                return Response({'error': 'Compute GPU is already rented'}, status=400)

            compute_gpu = ComputeGPU.objects.filter(id=compute_gpu_id).first()
            if compute_gpu:
                if ComputeMarketplace.objects.filter(id=compute_gpu.compute_marketplace_id, owner_id=user_id).exists():
                    return Response({'error': 'You cannot rent your own compute'}, status=status.HTTP_403_FORBIDDEN)

                compute_gpu.status = "renting"
                computeGpuPrice = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id, token_symbol=token_symbol).first()
                if computeGpuPrice:
                    order_instance = Order.objects.create(price = computeGpuPrice.price, total_amount=computeGpuPrice.price, unit=token_symbol, status="completed",
                                                        compute_marketplace_id=compute_gpu.compute_marketplace_id, user_id=user_id)
                    price = computeGpuPrice.price
                    amount = price * 0.9 if (timezone.now() - compute_gpu.created_at) < timedelta(days=30) else price

                    portfolio.amount_holding -= amount
                    portfolio.save()
                    compute_gpu.save()

                    request.data["resource_id"] = compute_gpu_id
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=False)
                    serializer.validated_data['price'] = price
                    serializer.validated_data['amount'] = amount
                    serializer.validated_data['account_id'] = user_id
                    serializer.validated_data['resource'] = 'compute_gpu'
                    serializer.validated_data['resource_id'] = compute_gpu_id
                    self.perform_create(serializer)

                    order_instance.status = "completed"
                    order_instance.save()

                    ComputeMarketplace.objects.filter(pk=compute_gpu.compute_marketplace_id).update(status="rented_bought")
                    History_Rent_Computes.objects.create(account_id=user_id, compute_marketplace_id=compute_gpu.compute_marketplace_id, compute_gpu_id=compute_gpu_id, status="renting")

                    return Response(serializer.data, status=201)
                else:
                    return Response({'error': 'ComputeGpuPrice not found'}, status=404)
            else:
                return Response({'error': 'Compute GPU not found'}, status=404)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Create Compute Gpu Price',
))

class ComputeGpuPriceCreateApi(generics.CreateAPIView):
    serializer_class = ComputeGpuPriceSerializer
    queryset = ComputeGpuPrice.objects.all()
    def post(self, request, *args, **kwargs):
        compute_gpu_id = self.request.data.get('compute_gpu_id')
        compute_marketplace_id = self.request.data.get('compute_marketplace_id')
        token_symbol = self.request.data.get('token_symbol')
        computeGpuPrice = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id, token_symbol=token_symbol).first()
        if computeGpuPrice:
            return Response({'error': 'compute gpu price is existed'}, status=400)
        return super(ComputeGpuPriceCreateApi, self).post(request, *args, **kwargs)


@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Update Compute Gpu Price',
))
class ComputeGpuPriceUpdateApi(generics.UpdateAPIView):
    serializer_class = ComputeGpuPriceSerializer
    queryset = ComputeGpuPrice.objects.all()

    def put(self, request, *args, **kwargs):
        compute_gpu_id = self.kwargs.get('pk') 
        token_symbol = self.request.data.get('token_symbol')
        price = self.request.data.get('price')

        if not token_symbol or not price:
            return Response({'error': 'token_symbol and price are required'}, status=status.HTTP_400_BAD_REQUEST)

        compute_gpu_price = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id, token_symbol=token_symbol).first()

        if not compute_gpu_price:
            return Response({'error': 'Compute GPU price not found'}, status=status.HTTP_404_NOT_FOUND)

        compute_gpu_price.price = price
        compute_gpu_price.save()

        return Response({'message': 'Compute GPU price updated successfully'}, status=status.HTTP_200_OK)


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Bulk Create Compute Gpu',
))
class BulkCreateComputeGpuApi(generics.CreateAPIView):
    serializer_class = BulkComputeGpuSerializer
    queryset = ComputeGPU.objects.all()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        cuda_data = request.data.get("cuda", [])
        compute_gpus = request.data.get("compute_gpus", [])
        compute_marketplace_id= None
        created_compute_gpus = []
        def sum_disk_info(all_disk_info):
            total_size = 0
            total_used = 0
            total_avail = 0

            for disk_info in all_disk_info:
                total_size += convert_to_bytes(disk_info["size"])
                total_used += convert_to_bytes(disk_info["used"])
                total_avail += convert_to_bytes(disk_info["avail"])

            return {
                "total_size": total_size,
                "total_used": total_used,
                "total_avail": total_avail
            }

        provided_gpu_ids = [
                compute_gpu_data.get("gpu_id") for compute_gpu_data in compute_gpus
            ]

        for compute_gpu_data in compute_gpus:
            gpu_id = compute_gpu_data.get('gpu_id')
            machine_options = compute_gpu_data["machine_options"]
            location_id = compute_gpu_data.get("location_id")
            location_alpha2 = compute_gpu_data.get("location_alpha2")
            location_name = compute_gpu_data.get("location_name")
            compute_marketplace_instance = ComputeMarketplace.objects.filter(
                id=compute_gpu_data["compute_marketplace"]
            ).first()
            compute_marketplace_id = compute_marketplace_instance.id

            compute_gpu = ComputeGPU.objects.filter(
                gpu_id=gpu_id, deleted_at__isnull=True
            ).first()
            if  compute_gpu is None:
                compute_gpu_data["machine_options"] = "physical-machines"
                created_compute_gpu = ComputeGPU.objects.create(
                    location_id=location_id,
                    location_alpha2=location_alpha2,
                    location_name=location_name,
                    machine_options="physical-machines",
                    infrastructure_id=compute_marketplace_instance,
                    gpu_name=compute_gpu_data["gpu_name"],
                    gpu_index=compute_gpu_data["gpu_index"],
                    compute_marketplace=compute_marketplace_instance,
                    gpu_id=compute_gpu_data["gpu_id"],
                )
                created_compute_gpus.append(created_compute_gpu)
            else:
                compute_gpu.location_id = location_id
                compute_gpu.location_alpha2 = location_alpha2
                compute_gpu.location_name = location_name
                compute_gpu.machine_options = "physical-machines"
                compute_gpu.save()

            # Update status for ComputeGPU records not in the provided list
            list_gpu = (
                ComputeGPU.objects.filter(
                    deleted_at__isnull=True,
                    infrastructure_id=compute_marketplace_instance.infrastructure_id,
                )
                .exclude(gpu_id__in=provided_gpu_ids)
                .all()
            )
            for gpu in list_gpu:
                gpu.status = "been_removed"
                gpu.deleted_at = datetime.now()
                gpu.save()

        gpus_machine = ComputeGPU.objects.filter(
            compute_marketplace_id=compute_marketplace_id, deleted_at__isnull=True
        ).exclude(status="been_removed").count()
        for cuda in cuda_data:
            ram_info = cuda["ram_info"]
            all_disk_info = cuda["all_disk_info"]
            disk_info = sum_disk_info(all_disk_info)
            print("disk_info", disk_info)
            compute_gpu = ComputeGPU.objects.filter(gpu_id=cuda["uuid"], deleted_at__isnull=True).first()
            compute_gpu.gpu_tflops = cuda["tflops"]
            compute_gpu.gpu_memory = str(convert_mb_to_byte(cuda["total_mem_mb"]))
            compute_gpu.memory = str(convert_mb_to_byte(cuda["total_mem_mb"]))
            compute_gpu.gpu_memory_used = str(convert_mb_to_byte(float(cuda["total_mem_mb"]) - float(
                cuda["free_mem_mb"]
            )))
            compute_gpu.gpu_memory_bandwidth = str(
                convert_gb_to_byte(cuda["mem_bandwidth_gb_per_s"])
            )
            compute_gpu.cores = str(cuda["cores"])
            compute_gpu.cuda_cores = str(cuda["cuda_cores"])
            compute_gpu.gpu_clock_mhz = str(cuda["gpu_clock_mhz"])
            compute_gpu.mem_clock_mhz = str(cuda["mem_clock_mhz"])
            compute_gpu.memory_bus_width = str(cuda["memory_bus_width"])
            compute_gpu.max_cuda_version = str(cuda["cuda_version"])
            compute_gpu.number_of_pcie_per_gpu = (
                str(cuda["pcie_link_gen_max"]) + "," + str(cuda["pcie_link_width_max"])
            )
            compute_gpu.ubuntu_version = str(cuda["ubuntu_version"])
            compute_gpu.eff_out_of_total_nu_of_cpu_virtual_cores = str(
                str(cuda["used_cores"]) + "/" + str(cuda["cpu_cores"])
            )
            compute_gpu.eff_out_of_total_system_ram = str(
                str(convert_mb_to_gb(ram_info["used_ram_mb"]))
                + "/"
                + str(convert_mb_to_gb(ram_info["total_ram_mb"]))
            )
            compute_gpu.disk = disk_info["total_size"]
            compute_gpu.disk_used = disk_info["total_used"]
            compute_gpu.disk_free = disk_info["total_avail"]
            compute_gpu.gpus_machine = str(gpus_machine)
            compute_gpu.save()

        # call update_system_info
        thread = threading.Thread(
            target=update_compute_marketplace, args=(compute_marketplace_id)
        )
        thread.start()

        return Response(ComputeGpuSerializer(created_compute_gpus, many=True).data, status=status.HTTP_201_CREATED)


def create_bulk_gpu_prices(gpu_prices):
    from .models import ComputeTimeWorking

    errors = []

    for gpu_price_data in gpu_prices:
        compute_gpu_id = gpu_price_data.get('compute_gpu_id')
        token_symbol = gpu_price_data.get('token_symbol')
        price = gpu_price_data.get('price')
        if not compute_gpu_id or not token_symbol or price  is None:
            errors.append({'error': 'Invalid data provided'})
            continue

        computeGpuPrice = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id, token_symbol=token_symbol).first()
        if computeGpuPrice:
            compute_time_working = ComputeTimeWorking.objects.first(
                compute_id=computeGpuPrice.compute_marketplace_id,
                deleted_at__isnull = True
            ).first()
            
            if compute_time_working:
                compute_gpu = ComputeGPU.objects.filter(compute_marketplace_id = compute_gpu_id).first()
                compute_gpu.status = "in_marketplace"

        if computeGpuPrice:
            errors.append({'error': f'Compute GPU price for compute_gpu_id {compute_gpu_id} and token_symbol {token_symbol} already exists'})
            continue

        serializer = ComputeGpuPriceSerializer(data=gpu_price_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    return errors
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Create Bulk Compute Gpu Price',
    request_body=GpuPriceDataSerializer,
))
class ComputeGpuPriceBulkCreateApi(generics.CreateAPIView):
    serializer_class = ComputeGpuPriceSerializer
    queryset = ComputeGpuPrice.objects.all()

    def post(self, request, *args, **kwargs):
        gpu_prices_data = request.data.get('gpu_price', [])
        errors = create_bulk_gpu_prices(gpu_prices_data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Compute GPU prices created successfully'}, status=status.HTTP_201_CREATED)


@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Bulk Update Compute Gpu Prices',
    request_body=GpuPriceDataSerializer,
))
class ComputeGpuPriceBulkUpdateApi(generics.UpdateAPIView):
    serializer_class = ComputeGpuPriceSerializer
    queryset = ComputeGpuPrice.objects.all()

    def put(self, request, *args, **kwargs):
        gpu_prices_data = request.data.get('gpu_price', [])
        errors = []

        for gpu_price_data in gpu_prices_data:
            compute_gpu_id = gpu_price_data.get('compute_gpu_id')
            token_symbol = gpu_price_data.get('token_symbol')
            price = gpu_price_data.get('price')

            if not compute_gpu_id or not token_symbol or price is None:
                errors.append({'error': 'Invalid data provided'})
                continue

            compute_gpu_price = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id, token_symbol=token_symbol).first()

            if not compute_gpu_price:
                errors.append({'error': f'Compute GPU price for compute_gpu_id {compute_gpu_id} and token_symbol {token_symbol} does not exist'})
                continue

            compute_gpu_price.price = price
            compute_gpu_price.save()

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Compute GPU prices updated successfully'}, status=status.HTTP_200_OK)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Create / Update  Compute  Price for CPU',
    request_body=CpuPriceDataSerializer,
))
class ComputeCpuPriceApi(generics.CreateAPIView):
    serializer_class = CpuPriceDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        compute_marketplace_id = serializer.validated_data.get('compute_marketplace_id')
        token_symbol = serializer.validated_data.get('token_symbol')
        price = serializer.validated_data.get('price')
        
        # Check if a record with the given compute_marketplace_id and type CPU exists
        cpu_price_obj = ComputeGpuPrice.objects.filter(compute_marketplace_id=compute_marketplace_id, type='cpu').first()
        if cpu_price_obj:
            # Update the existing record
            cpu_price_obj.token_symbol = token_symbol
            cpu_price_obj.price = price
            cpu_price_obj.save()
        else:
            compute_marketplace = ComputeMarketplace.objects.filter(id=compute_marketplace_id).first() 
            ComputeGpuPrice.objects.create(
                compute_marketplace_id=compute_marketplace,
                token_symbol=token_symbol,
                price=price,
                type='cpu'
            )

        return Response({'message': 'Compute CPU prices updated/created successfully'}, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Get Compute  Price for CPU,GPU',
    manual_parameters=[
                           openapi.Parameter('compute_marketplace_id', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='compute_marketplace_id'),
                           openapi.Parameter('compute_gpu_id', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='compute_gpu_id', required=False),
                           openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='type: cpu, gpu')
                           ]
))
class ComputeGpuPriceRetrieveApi(generics.RetrieveAPIView):
    queryset = ComputeGpuPrice.objects.all()
    serializer_class = PriceSerializer

    def get(self, request, *args, **kwargs):
        compute_marketplace_id = request.query_params.get('compute_marketplace_id')
        compute_gpu_id = request.query_params.get('compute_gpu_id')
        price_type = request.query_params.get('type')

        if not all([compute_marketplace_id, price_type]):
            return Response({'message': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gpu_price_obj = ComputeGpuPrice.objects.get(
                compute_marketplace_id=compute_marketplace_id,
                compute_gpu_id=compute_gpu_id,
                type=price_type
            )
            serializer = self.get_serializer(gpu_price_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ComputeGpuPrice.DoesNotExist:
            return Response({'message': 'Price information not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Compute Marketplace'],
    operation_summary='Recomend set Price for CPU,GPU',
    manual_parameters=[
        openapi.Parameter('compute_gpu_id', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description='compute_gpu_id', required=False)
        ]
))
class RecommendPriceAPI(generics.RetrieveAPIView):
    serializer_class = RecommendPriceSerializer

    def get(self, request, *args, **kwargs):
        # from ml.api_connector import MLApi
        # from tasks.models import Task
        # from projects.models import Project
        # api = MLApi(url = 'http://69.197.168.145:8018/')
        # tasks = Task.objects.filter(project_id=8)
        # project = Project.objects.filter(id=8).first()
        # for task in tasks:
        #     from tasks.serializers import TaskSimpleSerializer, PredictionSerializer
        #     tasks_ser = TaskSimpleSerializer(tasks, many=True).data
        #     api.train(project=project)
        compute_gpu_id = request.query_params.get('compute_gpu_id')
        gpu_instance = ComputeGPU.objects.filter(id=compute_gpu_id).first()
        try:
            gpu_price_obj = Recommend_Price.objects.filter(name=gpu_instance.gpu_name).first()
            if gpu_price_obj:
                serializer = self.serializer_class(gpu_price_obj)
                return Response(serializer.data)
            else:
                return Response({"message": "No recommended price found for the specified GPU."}, status=404)
        except ComputeGPU.DoesNotExist:
            return Response({"message": "Compute GPU not found."}, status=404)
