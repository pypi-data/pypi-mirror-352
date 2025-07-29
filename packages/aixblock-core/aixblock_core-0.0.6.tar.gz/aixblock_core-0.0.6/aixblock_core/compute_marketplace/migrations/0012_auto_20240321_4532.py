from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('compute_marketplace', '0011_auto_20240319_1234'),  
    ]

    operations = [
        migrations.AddField(
            model_name='computegpu',
            name='teraflops',
            field=models.CharField( verbose_name='teraflops',max_length=30, null=True),
        ),
         migrations.AddField(
            model_name='computegpuprice',
            name='type',
            field=models.CharField( verbose_name='type',max_length=15,default='gpu', null=True),
        ),
        # migrations.RunSQL("""
        #                 INSERT INTO "public"."compute_marketplace_compute_marketplace" (name, created_at, updated_at, infrastructure_id, owner_id, author_id, catalog_id, organization_id, "order", config, ip_address, port, docker_port, kubernetes_port, status, file, type, infrastructure_desc, callback_url, client_id, client_secret, ssh_key, card, price, compute_type) VALUES ('69.197.168.145', '2024-03-26 03:58:45.650898+00', '2024-03-26 03:58:45.650898+00', 'o88iq8j91ygk', 1, 1, 0, 1, 0, '{"cpu": "29068934", "ram": "3200", "disk": "12963498612", "diskType": "SSD", "os": "Linux"}', '69.197.168.145', '80', '4243', '6443', 'in_marketplace', '', 'MODEL-CUSTOMER', '', '', 'drsacUT2C5Ubi16kLQM9TQvamWpSXuzNU6wWJLnO', 'pbkdf2_sha256$260000$1ADdUSiEIiVpTKt18UpDKT$qMAfs8Dq+KJgdPo4VzKjeOwMKBDO+tJFgllXf7JcLcU=', NULL, NULL, 0, NULL);
        #                 INSERT INTO "public"."compute_marketplace_compute_marketplace" (name, created_at, updated_at, infrastructure_id, owner_id, author_id, catalog_id, organization_id, "order", config, ip_address, port, docker_port, kubernetes_port, status, file, type, infrastructure_desc, callback_url, client_id, client_secret, ssh_key, card, price, compute_type) VALUES ('108.181.196.144', '2024-03-26 04:04:13.091407+00', '2024-03-26 04:04:13.091407+00', '62zjomq5rg4n', 1, 1, 0, 1, 0, '{"cpu": "32068934", "ram": "4800", "disk": "12963498612", "diskType": "SSD", "os": "Linux"}', '108.181.196.144', '80', '4243', '6443', 'in_marketplace', '', 'MODEL-CUSTOMER', '', '', 'ZC2XeQZCwqW1ZZQ4XUyZeobUuZklKuHltubx4fCH', 'pbkdf2_sha256$260000$kh413OeMOO0uVkIyJlU1XT$Li44yBHc5NI4Qykjwvc+dfWnGvqEe+89JebD0aPn1IA=', NULL, NULL, 0, NULL);
        #                  """),
        # migrations.RunSQL("""
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ('o88iq8j91ygk', 'NVIDIA RTX A6000', NULL, 0, '20gb', 'NVIDIA', 'gpu-bkaj-hbas-dasd-i931', '2024-03-26 03:58:45.756541+00', '2024-03-26 03:58:45.756541+00', 'in_marketplace', 1, 'NVIDIA RTX A6000');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ( 'o88iq8j91ygk', 'NVIDIA RTX A5000', NULL, 1, '20gb', 'NVIDIA', 'gpu-xyz-abc-def-123', '2024-03-26 03:58:45.760541+00', '2024-03-26 03:58:45.760541+00', 'in_marketplace', 1, 'NVIDIA RTX A5000');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ( 'o88iq8j91ygk', 'NVIDIA RTX A4000', NULL, 2, '20gb', 'NVIDIA', 'gpu-123-456-789-xyz', '2024-03-26 03:58:45.764541+00', '2024-03-26 03:58:45.764541+00', 'in_marketplace', 1, 'NVIDIA RTX A4000');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ( 'o88iq8j91ygk', 'NVIDIA RTX A3000', NULL, 3, '20gb', 'NVIDIA', 'gpu-789-abc-xyz-456', '2024-03-26 03:58:45.768542+00', '2024-03-26 03:58:45.768542+00', 'in_marketplace', 1, 'NVIDIA RTX A3000');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ('62zjomq5rg4n', 'NVIDIA RTX 4090', NULL, 0, '24gb', 'NVIDIA', 'gpu-hsb3-hbas-321f-i931', '2024-03-26 04:04:13.163403+00', '2024-03-26 04:04:13.163403+00', 'in_marketplace', 2, 'NVIDIA RTX 4090');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ('62zjomq5rg4n', 'NVIDIA RTX 4070', NULL, 1, '12gb', 'NVIDIA', 'gpu-xyz-abcd-defd-12s3', '2024-03-26 04:04:13.168403+00', '2024-03-26 04:04:13.168403+00', 'in_marketplace', 2, 'NVIDIA RTX 4070');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ('62zjomq5rg4n', 'NVIDIA RTX 3090', NULL, 2, '24gb', 'NVIDIA', 'gpsu-123a-45d6-ssdd-xysz', '2024-03-26 04:04:13.172403+00', '2024-03-26 04:04:13.172403+00', 'in_marketplace', 2, 'NVIDIA RTX 3090');
        #                 INSERT INTO "public"."compute_gpu" (infrastructure_id, gpu_name, power_consumption, gpu_index, gpu_memory, branch_name, gpu_id, created_at, updated_at, status, compute_marketplace_id, teraflops) VALUES ('62zjomq5rg4n', 'NVIDIA RTX 3070', NULL, 3, '20gb', 'NVIDIA', 'gpsu-789a-cbsd-xysz-45s6', '2024-03-26 04:04:13.176402+00', '2024-03-26 04:04:13.176402+00', 'in_marketplace', 2, 'NVIDIA RTX 3070');
        #                  """),
        # migrations.RunSQL("""
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 1, 'eth', 20, 1, 'hour', 1, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 2, 'eth', 15, 2, 'hour', 1, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 3, 'eth', 10, 3, 'hour', 1, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 4, 'eth', 5, 4, 'hour', 1, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 5, 'eth', 50, 5, 'hour', 2, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 6, 'eth', 25, 6, 'hour', 2, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 7, 'eth', 10, 7, 'hour', 2, 'gpu');
        #                 INSERT INTO "public"."compute_gpu_price" (id, token_symbol, price, compute_gpu_id, unit, compute_marketplace_id, type) VALUES ( 8, 'eth', 50, 8, 'hour', 2, 'gpu');
        #                  """),
        # migrations.RunSQL("""
        #                 INSERT INTO "public"."compute_timeworking" (infrastructure_id, time_start, time_end, created_at, updated_at, status, compute_gpu_id) VALUES ( 'o88iq8j91ygk', '00:00:00', '23:59:59', '2024-03-26 03:59:30.710654+00', '2024-03-26 03:59:30.710654+00', 'in_marketplace', 1);
        #                 INSERT INTO "public"."compute_timeworking" (infrastructure_id, time_start, time_end, created_at, updated_at, status, compute_gpu_id) VALUES ('62zjomq5rg4n', '00:00:00', '23:59:59', '2024-03-26 04:05:04.203907+00', '2024-03-26 04:05:04.203907+00', 'in_marketplace', 2);
        #                  """) 
    ]
