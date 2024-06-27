from collections import defaultdict, deque


tasks_registry = {}
tasks_dependencies = defaultdict(list)

class PipelineExecutor:
    def __init__(self):
        self.tasks = tasks_registry
        self.dependencies = tasks_dependencies
        self.execution_order = self.build_execution_order()
    
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
    
    def run(self):
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            print(f"Executing {task_name}")
            task.perform_task()

def register(depends_on=None):
    """Decorator to register a task class in the tasks registry"""
    def decorator(cls):
        key = cls.__name__
        tasks_registry[key] = cls()
        if depends_on:
            tasks_dependencies[key].append(depends_on.__name__)
        return cls
    return decorator