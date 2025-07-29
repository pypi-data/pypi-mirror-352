class ProviderBase:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def list_compute(self, data_filter):
        pass

    def info_compute(self, id):
        pass

    def delete_compute(self, id):
        pass

    def start_compute(self, id):
        pass

    def reset_compute(self, id):
        pass

    def stop_compute(self, id):
        pass

    
