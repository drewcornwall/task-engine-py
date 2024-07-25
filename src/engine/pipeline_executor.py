from collections import defaultdict, deque
from typing import Dict

from engine.config_provider import get_default_config_provider
from reporters import plan_reporters


tasks_registry = {}
tasks_dependencies = defaultdict(list)
context: Dict = dict()

config_provider = get_default_config_provider()
context.update(config_provider.get_config())


class PipelineExecutor:
    def __init__(self):
        self.config_provider = get_default_config_provider()
        self.tasks = tasks_registry
        self.dependencies = tasks_dependencies
        self.execution_order = self.build_execution_order()
        self.report_plan()

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

    def run(self):
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            print(f"Executing {task_name}")
            task.perform_task()


def register(depends_on=None):
    """Decorator to register a task class in the tasks registry"""
    def decorator(cls):
        key = cls.__name__
        if tasks_registry.get(key):
            raise Exception(f"Duplicate task name: {key}")

        tasks_registry[key] = cls(context)
        if depends_on:
            tasks_dependencies[key].append(depends_on.__name__)
        return cls
    return decorator
