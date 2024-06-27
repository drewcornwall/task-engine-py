from engine import Task, PipelineExecutor, register, retries, skippable


@register()
class BaseTask(Task):
    def perform_task(self):
        print("Hello!")
    
    def retry_handler(self, error):
        return False

@register(depends_on=BaseTask)
class Task1(Task):
    @retries(3)
    def perform_task(self):
        # Simulating an HTTP call that might fail
        import random
        response_code = random.choice([200, 500, 401])
        if response_code == 200:
            print("Task1 completed successfully")
        elif response_code == 500:
            print("Task1 failed with error 500, retrying...")
            raise Exception("Error 500")
        elif response_code == 401:
            print("Task1 failed with error 401, no retries")
            raise Exception("Error 401")
    
    def retry_handler(self, error):
        if "500" in str(error):
            return True
        if "401" in str(error):
            return False
        
@register(depends_on=BaseTask)
class AlwaysFailsTask(Task):
    @skippable
    @retries(3)
    def perform_task(self):
        print("AlwaysFailsTask failed")
        raise Exception("AlwaysFailsTask failed")
    
    def retry_handler(self, error):
        return True
        
@register(depends_on=AlwaysFailsTask)
class Task2(Task):
    def perform_task(self):
        print("Task2 completed successfully")

    def retry_handler(self, error):
        return False


if __name__ == "__main__":
    executor = PipelineExecutor()
    executor.run()

