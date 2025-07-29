import django_rq
from rq import Queue
from redis import Redis

def process_task_id(self, task_id):
    pass

class Task_Manage_Queue:
    def __init__(self, queue_name='default', connection_params=None):
        self.queue_name = queue_name
        if connection_params:
            self.connection = Redis(**connection_params)
            self.queue = Queue(name=self.queue_name, connection=self.connection)
        else:
            self.queue = django_rq.get_queue(self.queue_name)

    def is_task_in_queue(self, task_id):
        for job_id in self.queue.job_ids:
            job = self.queue.fetch_job(job_id)
            if job and job.args and job.args[0] == task_id:
                return True 
        return False
    
    def get_task_ids_from_queue(self):
        jobs = map(self.queue.fetch_job, self.queue.job_ids)
        task_ids = [job.meta.get('task_id') for job in jobs if job and job.meta]
        return task_ids

    def push_tasks_to_queue(self, task_ids, user_id=0):
        # queue = django_rq.get_queue(self.queue_name)
        task_id_exits = self.get_task_ids_from_queue()
        for task_id in task_ids:
            # if not self.is_task_in_queue(task_id):
            if task_id not in task_id_exits:
                # print(task_id)
                self.queue.enqueue_call(func=process_task_id, args=(task_id,), result_ttl=0, ttl=3600*24*30, meta={'task_id': task_id, 'status': 'queued', "user_id": user_id})


    def push_task_to_queue(self, task_id, user_id=0):
        # queue = django_rq.get_queue(self.queue_name)
        task_ids = self.get_task_ids_from_queue()
        # if not self.is_task_in_queue(task_id):
        if task_id not in task_ids:
            # print(task_id)
            self.queue.enqueue_call(func=process_task_id, args=(task_id,), result_ttl=0, ttl=3600*24*30, meta={'task_id': task_id, 'status': 'queued', "user_id": user_id})

    def check_tasks_queue(self, ids):
        if len(self.queue.job_ids) == 0:
            self.push_tasks_to_queue(ids)

    def mark_task_status(self, task_id, status, user_id=0):
        for job_id in self.queue.job_ids:
            job = self.queue.fetch_job(job_id)
            if job and job.meta and job.meta.get('task_id') == task_id:
                # Cập nhật trạng thái của công việc
                job.meta['status'] = status
                job.meta['user_id'] = user_id
                job.save()
                return True  
        return False

    def get_and_mark_task_in_processing(self, user_id=0):
        job_ids = self.queue.job_ids

        processing_task_id = None
        queued_task_id = None

        # Duyệt qua tất cả job_ids một lần
        for job_id in job_ids:
            job = self.queue.fetch_job(job_id)
            if job:
                task_id = job.meta.get('task_id')
                status = job.meta.get('status')
                job_user_id = job.meta.get('user_id')

                if job_user_id == user_id and status == 'processing':
                    processing_task_id = task_id
                    break

                if status == 'queued' and not queued_task_id:
                    queued_task_id = task_id  # Ghi nhận task đầu tiên có trạng thái queued

        if processing_task_id:
            return processing_task_id
        
        elif queued_task_id:
            self.mark_task_status(queued_task_id, 'processing', user_id)
            return queued_task_id

        return None

    # Xóa task đã hoàn thành khỏi hàng đợi
    def delete_completed_task(self, task_id):
        for job_id in self.queue.job_ids:
            job = self.queue.fetch_job(job_id)
            if job and job.meta.get('task_id') == task_id:
                job.delete()
                break
    
    def delete_completed_tasks(self, tasks):
        for job_id in self.queue.job_ids:
            job = self.queue.fetch_job(job_id)
            if job and job.meta.get('task_id') in tasks:
                job.delete()
    
    def clear_all_queue(self):
        self.queue.empty()

# task_annotation = Task_Manage_Queue("task_annotation")
# task_qa = Task_Manage_Queue("task_qa")
# task_qc = Task_Manage_Queue("task_qc")

# task_annotation.clear_all_queue()
# task_qa.clear_all_queue()
# task_qc.clear_all_queue()