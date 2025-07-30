from wbcore.metadata.configs.endpoints import EndpointViewConfig


class TransactionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        model = "{{transaction_url_type}}"
        return f"{self.request.scheme}://{self.request.get_host()}/api/portfolio/{model}/"


class TransactionPortfolioEndpointConfig(TransactionEndpointConfig):
    pass
