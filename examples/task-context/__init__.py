from engine import register, retries, PipelineExecutor, Task
import requests


@register()
class NewTenant(Task):
    @retries(3)
    def perform_task(self):
        response = requests.post(self.context['tenant_info']['tenant_url'])
        if response.status_code == 400:
            raise Exception("Tenant already exists 400")
        print("Creating new tenant")

    def retry_handler(self, error):
        if "400" in str(error):
            return False
        return True


@register(depends_on=NewTenant)
class NewEntity(Task):
    def perform_task(self):
        requests.post(self.context['tenant_info']['entity_name'])
        print("Creating new entity")

    def retry_handler(self, error):
        return False


if __name__ == "__main__":
    executor = PipelineExecutor()
    executor.run()