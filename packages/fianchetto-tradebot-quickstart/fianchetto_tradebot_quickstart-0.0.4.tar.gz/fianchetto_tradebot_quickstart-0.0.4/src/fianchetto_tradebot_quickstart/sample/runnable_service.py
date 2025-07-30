class RunnableService:
    def __init__(self, port, service):
        self.port = port
        self.service = service

    def __call__(self, *args, **kwargs):
        self.service.run(host='0.0.0.0',port=self.port)
