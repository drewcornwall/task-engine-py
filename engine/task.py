class Task:
    def perform_task(self):
        raise NotImplementedError
    
    def retry_handler(self, error):
        return False