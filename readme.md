# Task Engine

Task Engine is a simple Python task orchestration tool designed to register tasks as part of an execution pipeline, provide error handling, and manage the order of execution.

Tasks are single units of work that can perform a wide variety of operations. The specific implementation is up to the user, but each task must extend two methods: perform_task() and retry_handler().

- `perform_task()`: This method contains the code for the task's main operation. It should always return None or raise an exception if the task fails.
- `retry_handler()`: This method handles exceptions and determines whether a task should be retried. It should return True to retry the task or False to not retry.

By default, `retry_handler()` returns False, which will propagate any exceptions and stop the pipeline. If a task might fail intermittently (e.g., due to temporarily unavailable resources), the `retry_handler()` can be customized with logic to handle such scenarios (return True). When used with the retries(n) decorator, the task will be retried up to n times before the pipeline fails.

To register a task, use the @register decorator. This allows specifying dependencies on other tasks, ensuring the pipeline executes tasks in the correct order.

If a particular task failure should not stop the entire pipeline, it can be decorated with `@skippable`.

The `retries(n)` and `skippable()` decorator can be stacked. For example:

```
@register()
class AlwaysFailsTask(Task):
    @skippable
    @retries(3)
    def perform_task(self):
        print("AlwaysFailsTask failed")
        raise Exception("AlwaysFailsTask failed")
    
    def retry_handler(self, error):
        return True
```