import signal
import time
from threading import Thread, Lock
from django.conf import settings

_managers = dict()
_lock = Lock()

class ThreadsManager:
    name = "[Threads Manager]"
    manager_thread = None
    state = "STOP"
    threads = []
    queue = []
    workers_count = 1
    lock = Lock()

    def __init__(self, name: str, workers_count: int):
        self.name = name
        self.workers_count = workers_count

    def __manager(self):
        while self.state == "RUNNING":
            self.lock.acquire()
            loop_list = self.threads[:]

            for thread in loop_list:
                if self.state != "RUNNING":
                    break

                if thread.is_alive():
                    continue

                try:
                    self.threads.remove(thread)
                    print(f"{self.name} Finish 1 thread. Working: {len(self.threads)}/{self.workers_count}. Queue: {len(self.queue)}")
                except Exception as e:
                    print(f"{self.name} Exception while removing thread: {e}")

            loop_list = self.queue[:]

            for thread in loop_list:
                if len(self.threads) >= self.workers_count or self.state != "RUNNING":
                    break

                try:
                    self.threads.append(thread)
                    thread.start()
                    self.queue.remove(thread)
                    print(f"{self.name} Start 1 thread. Working: {len(self.threads)}/{self.workers_count}. Queue: {len(self.queue)}")
                except Exception as e:
                    print(f"{self.name} Exception while starting thread: {e}")

            self.lock.release()
            time.sleep(1)

    def start(self):
        while self.state != "STOP":
            time.sleep(0.1)

        self.state = "RUNNING"
        self.manager_thread = Thread(target=self.__manager, )
        self.manager_thread.start()

    def stop(self):
        if self.state != "RUNNING":
            return

        self.state = "STOPPING"
        self.join()
        self.state = "STOP"

    def join(self):
        loop_list = self.queue[:]

        for thread in loop_list:
            if thread.is_alive():
                thread.join()

            self.lock.acquire()
            self.threads.remove(thread)
            self.lock.release()

    def add(self, thread):
        if self.state != "RUNNING":
            print(f"{self.name} The manager is not running")
            return

        self.lock.acquire()
        self.queue.append(thread)
        self.lock.release()

    def is_running(self):
        return self.state == "RUNNING"


def _manage_thread(key: str, name: str, thread: Thread):
    _lock.acquire()

    if key not in _managers:
        _managers[key] = ThreadsManager(name, settings.THREADS_MANAGER_WORKER)
        _managers[key].start()

        def _signal_handler(_, __):
            _managers[key].stop()

        try:
            signal.signal(signal.SIGINT, _signal_handler)
            signal.signal(signal.SIGTERM, _signal_handler)
        except Exception:
            pass

    _lock.release()
    _managers[key].add(thread)


def manage_task_optimize(thread):
    _manage_thread("task", "[Threads Manager][Task Optimize]", thread)


def manage_centrifuge_thread(thread):
    _manage_thread("centrifuge", "[Threads Manager][Centrifuge]", thread)


def manage_annotation_redact_thread(thread):
    _manage_thread("annotation_redact", "[Threads Manager][Annotation Redact]", thread)

