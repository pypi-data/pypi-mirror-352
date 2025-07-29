from django.db.models.signals import post_save
from django.dispatch import receiver
from compute_marketplace.models import ComputeGPU, ComputeGpuPrice, ComputeTimeWorking


@receiver(post_save, sender=ComputeGpuPrice)
@receiver(post_save, sender=ComputeTimeWorking)
def update_compute_gpu_status(sender, instance, **kwargs):
    # Determine the ComputeGPU ID based on the sender
    if sender == ComputeGpuPrice:
        compute_gpu_id = instance.compute_gpu_id_id
    elif sender == ComputeTimeWorking:
        compute_gpu_id = instance.compute_id

    # Get the ComputeGPU instance
    try:
        compute_gpu = ComputeGPU.objects.get(id=compute_gpu_id)
    except ComputeGPU.DoesNotExist:
        return

    # Check if related records exist
    has_price = ComputeGpuPrice.objects.filter(compute_gpu_id=compute_gpu_id).exists()
    has_time_working = ComputeTimeWorking.objects.filter(
        compute_id=compute_gpu.compute_marketplace_id,
        deleted_at__isnull = True
    ).exists()

    # Update status in marketplace if set price and time working
    if (
        compute_gpu.status != ComputeGPU.Status.BEEN_REMOVED
        and has_price
        and has_time_working
    ):
        compute_gpu.status = ComputeGPU.Status.IN_MARKETPLACE
        compute_gpu.save()
