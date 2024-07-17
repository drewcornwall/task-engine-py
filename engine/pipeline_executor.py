from collections import defaultdict, deque
import multiprocessing
import time

from reporters import plan_reporters


tasks_registry = {}
tasks_dependencies = defaultdict(list)


class PipelineExecutor:
    def __init__(self):
        self.tasks = tasks_registry
        self.dependencies = tasks_dependencies
        self.execution_order = self.build_execution_order()
        self.report_plan()
        self.executed_tasks = set()
        self.lock = multiprocessing.Lock()

    def build_execution_order(self):
        in_degree = {key: 0 for key in self.tasks}
        for task, deps in self.dependencies.items():
            for dep in deps:
                in_degree[task] += 1

        # tasks with no dependencies
        queue = deque([task for task in self.tasks if in_degree[task] == 0])
        execution_order = []

        # Process tasks with in-degree of 0
        while queue:
            task = queue.popleft()
            execution_order.append(task)

            # Reduce the in-degree of dependent tasks
            for dep in self.tasks:
                if task in self.dependencies[dep]:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        if len(execution_order) != len(self.tasks):
            raise Exception("Circular dependency detected")

        return execution_order

    def report_plan(self):
        for reporter in plan_reporters:
            reporter.report(self.execution_order)

    def run_task(self, task_name):
        task = self.tasks[task_name]
        print(f"Executing {task_name}")
        task.perform_task()
        with self.lock:
            self.executed_tasks.add(task_name)

    def can_run_task(self, task_name):
        with self.lock:
            return all(dep in self.executed_tasks for dep in self.dependencies[task_name]) # noqa E501

    def run(self):
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pending_tasks = deque(self.execution_order)
        results = []

        while pending_tasks or any(not r.ready() for r in results):
            while pending_tasks and self.can_run_task(pending_tasks[0]):
                task_name = pending_tasks.popleft()
                result = pool.apply_async(self.run_task, (task_name,))
                results.append(result)
            time.sleep(0.1)  # Brief sleep to avoid busy waiting

        pool.close()
        pool.join()


def register(depends_on=None):
    """Decorator to register a task class in the tasks registry"""
    def decorator(cls):
        key = cls.__name__
        if tasks_registry.get(key):
            raise Exception(f"Duplicate task name: {key}")

        tasks_registry[key] = cls()
        if depends_on:
            tasks_dependencies[key].append(depends_on.__name__)
        return cls
    return decorator
