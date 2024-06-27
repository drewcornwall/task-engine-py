# Task Engine

Task Engine is a simple Python task orchestration tool designed to register tasks as part of an execution pipeline, provide error handling, and manage the order of execution.

Tasks are single units of work that can perform a wide variety of operations. The specific implementation is up to the user, but each task must extend two methods: perform_task() and retry_handler().

- `perform_task()`: This method contains the code for the task's main operation. It should always return None or raise an exception if the task fails.
- `retry_handler()`: This method handles exceptions and determines whether a task should be retried. It should return True to retry the task or False to not retry.

By default, `retry_handler()` returns False, which will propagate any exceptions and stop the pipeline. If a task might fail intermittently (e.g., due to temporarily unavailable resources), the `retry_handler()` can be customized with logic to handle such scenarios (return True). When used with the retries(n) decorator, the task will be retried up to n times before the pipeline fails.

To register a task, use the `@register` decorator. This allows specifying dependencies on other tasks, ensuring the pipeline executes tasks in the correct order.

```
@register(depends_on=Task1)
def Task2()...
```

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

## Examples

example.py contains four tasks:

- BaseTask: Prints a message.
- Task1: Simulates an HTTP call that randomly returns a 200, 500, or 401 error code. It gracefully handles 500 errors by retrying up to 3 times, but it stops the pipeline if a 401 error is encountered.
- Task2: Prints a message.
- AlwaysFailsTask: Fails 3 times but is designed to skip and not stop the pipeline execution.

The DAG is as follows: BaseTask -> Task1 -> AlwaysFailsTask -> Task2

Example runs:

Run 1 (no Terminating errors encountered, single retry occurs on 500)
```
Executing BaseTask
Hello!
Executing Task1
Task1 failed with error 500, retrying...
Task1 completed successfully
Executing AlwaysFailsTask
AlwaysFailsTask failed
AlwaysFailsTask failed
AlwaysFailsTask failed
Skipping task due to error: AlwaysFailsTask failed
Executing Task2
Task2 completed successfully
```

Run2 (Pipeline terminating error encountered, 500 followed by a 401 on retry)
```
Executing BaseTask
Hello!
Executing Task1
Task1 failed with error 500, retrying...
Task1 failed with error 401, no retries
Traceback (most recent call last):
  File "/Users/yaroslav.berejnoi/Workspace/yarobear/task-engine/example.py", line 56,
  ... raise Exception("Error 401")
Exception: Error 401
```