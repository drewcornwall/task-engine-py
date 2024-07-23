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

Examples can be run like so: `python run_examples.py <example_module_name>`


### tasks
tasks example contains four tasks:

- BaseTask: Prints a message.
- Task1: Simulates an HTTP call that randomly returns a 200, 500, or 401 error code. It gracefully handles 500 errors by retrying up to 3 times, but it stops the pipeline if a 401 error is encountered.
- Task2: Prints a message.
- AlwaysFailsTask: Fails 3 times but is designed to skip and not stop the pipeline execution.

The DAG is as follows: BaseTask -> Task1 -> AlwaysFailsTask -> Task2

Example runs:

Run 1 (no terminating errors encountered, single retry occurs on 500)
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

Run 2 (Pipeline terminating error encountered, 500 followed by a 401 on retry)
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

### jobs

Jobs are simply composed into modules of tasks. Tasks can have cross job-task dependencies, and the pipeline executor will ensure jobs are executed in the correct order.

The DAG is as follows: Job2Task1 -> Job2Task2 -> Job1Task1 -> Job1Task2

Example run:

```
Executing Job2Task1
Hello from Job2, Task1!
Executing Job2Task2
Hello from Job2, Task2!
Executing Job1Task1
Hello from Job1, Task1!
Executing Job1Task2
Hello from Job1, Task2!
```

# July 24-25 2024 HC Data Platform Hackathon

Welcome! This section outlines some potential features that could be added to task-engine, and some use cases. Feel free to come up with features/use cases of your own!
Have fun!

Use cases:

Features:

- TaskContext
  - At the start of a pipeline execution, we should be able to hydrate some read-only store of configuration values. These values form a TaskContext that is available to every task. e.g. reading url for an endpoint we need to hit, or key vault secrets.
  - Bonus points: Store hydrators are registerable. By default, the store is hydrated from a local .yml file. Additional hydrators can be registered by client applications that override the default.

- WaitForResource
  - Sometimes we have to wait for a resource to become available to configure it. Implement a hook that can wait for a resource up to a specified amount of time before firing performTask()

- SensibleDefaults
  - Create a SensibleDefaultsRequests module which has classes that extend Task. It will have sensible defaults on how to handle certain errors codes from the `requests` library. For example, 429(too many requests), we should retry 3 times, exponentially backing off (1 second, 2 seconds, 4 seconds) before failing.
  - The goal is that users can extends this class instead of the base Task class, and get some sensible error handling automatically.

- RateLimiter
  - Use some kind of algorithm (Token Bucket e.g.) to keep track of how many requests per second are happening against certain endpoints. You can use the [Databricks API rate limits](https://docs.databricks.com/en/resources/limits.html#limits-api-rate-limits) as an example.
  - If we are approaching the rate limit, add a delay to the task until more tokens becomes available (if using Token Bucket Algorithm)
  - Ideally this would be a decorator `@rateLimit(key='/'jobs/runs/get')`. The key is used as a lookup in some global hash table to keep track of how many requests per second are being issues against the endpoint.

- Reporter
  - Currently there is one reporter that logs the DAG to console before running. It would be great to have one that shows the current progress/state of execution, or output the DAG for graphiz/dot language, mermaid, html, or other graphing library.

- Parallelism
  - Currently task-engine is single process, and executes all the tasks in the DAG sequentially. It would be great if we could execute the tasks in individual threads while respecting DAG dependencies.

- Logging
  - Hook up OpenTelemetry to collect logs. Register any exporter as an example (log file is fine). All tasks associated with a pipeline execution should be associated with the same trace id.

- PriorityExecution (depends on Parallelism)
  - Some tasks might take longer to execute than others. If these tasks have no dependencies or have their dependency met, move them to the front of the execution pipeline to shorten the length of overall pipeline execution.
  - This feature requires runtime statistics to be collected and persisted (local file is fine) for every task and some re-balancing algorithm to run before pipeline execution or even after every task. If no statistics exist, in the case of a first run, no re-balancing happens.
  - Max heap priority queue seems like a good DS for this.