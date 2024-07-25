from engine import Task, register
from job_2 import Job2Task2


@register()
class Job1Task1(Task):
    def perform_task(self):
        print("Hello from Job1, Task1!")


@register(depends_on=Job2Task2)
class Job1Task2(Task):
    def perform_task(self):
        print("Hello from Job1, Task2!")
