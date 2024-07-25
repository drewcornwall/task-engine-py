from engine import Task, PipelineExecutor, register, check_resource


def is_resource_available():
    # Replace this with your actual resource availability check logic
    return False


@register()
class CheckResourceAvailable(Task):
    @check_resource(is_resource_available)
    def perform_task(self):
        print("Resource Was Available!")


if __name__ == "__main__":
    executor = PipelineExecutor()
    executor.run()
