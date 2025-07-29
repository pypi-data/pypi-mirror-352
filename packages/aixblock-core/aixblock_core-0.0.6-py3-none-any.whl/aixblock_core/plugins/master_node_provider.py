import json

import requests

from core.utils.params import get_env
from asgiref.sync import sync_to_async

from core.utils.convert_memory_to_byte import convert_gb_to_byte


class MasterNodeProvider:

    @property
    def access_token(self):
        return get_env("MASTER_TOKEN", "")

    @property
    def endpoint(self):
        return get_env("MASTER_NODE", "")

    @property
    def headers(self):
        return {f"Authorization": f"Token {self.access_token}"}

    def checkout_order(self, payload):
        if not self.endpoint or not self.access_token:
            return False
        try:
            response = requests.post(
                f"{self.endpoint}/api/compute_marketplace/rent/", headers=self.headers, json=payload,
            )

            if response.status_code != 200:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    def get_compute(self):
        try:
            response = requests.get(f"{self.endpoint}/api/compute_marketplace/list-rented-card", headers=self.headers, params={
                "page": 1,
                "page_size": 1000,
                "fieldSearch": "all",
            })

            if response.status_code != 200:
                return []
            data = response.json()
            results = data.get('results')
            for item in results:
                item["is_from_master_node"] = True
            return results
        except Exception as e:
            print(e)
            return []

    def delete_compute(self, infrastructure_id):
        try:
            response = requests.delete(f"{self.endpoint}/api/compute_marketplace/list-rented-card/{infrastructure_id}", headers=self.headers)
            return response.ok
        except Exception as e:
            print(e)
            return False


@sync_to_async
def update_vast_info_for_self_host(data):
    from users.models import User
    from compute_marketplace.api import ComputeMarketplaceRentV2API

    """This function will be triggered after "compute" finished installation from master node"""
    print('data vastai', data)
    user_email = data.get("email")
    compute_vast_hours = data.get("compute_vast_hours")
    status_install = data.get("status_install")
    response = data.get("response")
    port_tem = data.get("port_tem")
    status = data.get("status")
    errors = data.get("errors")
    compute_vast_id = data.get("compute_vast_id")
    price = data.get("price")

    user = User.objects.filter(email=user_email).first()
    if not user:
        return

    compute_marketplace_rent_v2 = ComputeMarketplaceRentV2API()
    compute_marketplace_rent_v2.update_compute_vast(
        user=user,
        status_install=status_install,
        user_id=user.id,
        user_uuid=user.uuid,
        price=price,
        compute_vast_id=compute_vast_id,
        errors=errors,
        response=response,
        payer_email=user_email,
        compute_vast_hours=compute_vast_hours,
        port_tem=port_tem,
        publish_installed_message=False
    )
    
@sync_to_async
def update_exabit_info_for_self_host(data):
    from users.models import User
    from compute_marketplace.api import ComputeMarketplaceRentV2API

    """This function will be triggered after "compute" finished installation from master node"""
    print('data exabit', data)
    user_email = data.get("email")
    compute_exabit_hours = data.get("compute_exabit_hours")
    status_install = data.get("status_install")
    response = data.get("response")
    port_tem = data.get("port_tem")
    status = data.get("status")
    errors = data.get("errors")
    compute_exabit_id = data.get("compute_exabit_id")
    price = data.get("price")

    user = User.objects.filter(email=user_email).first()
    if not user:
        return
    compute_marketplace_rent_v2 = ComputeMarketplaceRentV2API()
    compute_marketplace_rent_v2.update_compute_exabit(
        user=user,
        status_install=status_install,
        user_id=user.id,
        user_uuid=user.uuid,
        price=price,
        compute_exabit_id=compute_exabit_id,
        errors=errors,
        response=response,
        payer_email=user_email,
        compute_exabit_hours=compute_exabit_hours,
        port_tem=port_tem,
        publish_installed_message=False
    )

@sync_to_async
def delete_compute(data):
    from users.models import User
    from compute_marketplace.models import History_Rent_Computes, ComputeMarketplace, ComputeGPU, ComputeGpuPrice
    from compute_marketplace.api import HistoryRentComputeDeleteAPI
    print("data delete compute", data)
    infrastructure_id = data.get("infrastructure_id")
    compute_marketplace = ComputeMarketplace.objects.filter(infrastructure_id=infrastructure_id).first()
    instance = History_Rent_Computes.objects.filter(compute_marketplace_id=compute_marketplace.id).first()
    if not instance:
        return
    compute_marketplace = ComputeMarketplace.objects.filter(infrastructure_id=infrastructure_id).first()
    user_id = compute_marketplace.author_id
    user = User.objects.filter(id=user_id).first()
    history_rent_compute_api_view = HistoryRentComputeDeleteAPI()
    history_rent_compute_api_view.delete_compute(instance=instance, user_id=user.id, user_uuid=user.uuid)
