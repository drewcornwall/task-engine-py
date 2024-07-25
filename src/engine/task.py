class Task:
    def __init__(self, context: any):
        self.context = context
    
    def perform_task(self):
        raise NotImplementedError
    
    def retry_handler(self, error):
        return False