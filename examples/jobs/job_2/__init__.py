from engine import Task, register


@register()
class Job2Task1(Task):
    def perform_task(self):
        print("Hello from Job2, Task1!")


@register()
class Job2Task2(Task):
    def perform_task(self):
        print("Hello from Job2, Task2!")
