from typing import TypeVar, Optional
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from crypticorn.hive import HiveClient
from crypticorn.klines import KlinesClient
from crypticorn.pay import PayClient
from crypticorn.trade import TradeClient
from crypticorn.metrics import MetricsClient
from crypticorn.auth import AuthClient
from crypticorn.common import BaseUrl, ApiVersion, Service, apikey_header as aph
from importlib.metadata import version

ConfigT = TypeVar("ConfigT")
SubClient = TypeVar("SubClient")


class ApiClient:
    """
    The official Python client for interacting with the Crypticorn API.
    It is consisting of multiple microservices covering the whole stack of the Crypticorn project.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        jwt: Optional[str] = None,
        base_url: BaseUrl = BaseUrl.PROD,
        *,
        http_client: Optional[ClientSession] = None,
    ):
        self.base_url = base_url
        """The base URL the client will use to connect to the API."""
        self.api_key = api_key
        """The API key to use for authentication (recommended)."""
        self.jwt = jwt
        """The JWT to use for authentication (not recommended)."""
        self.version = version("crypticorn")
        """The version of the client."""

        self._http_client = http_client
        self._owns_http_client = http_client is None  # whether we own the http client
        self._service_classes: dict[Service, type[SubClient]] = {
            Service.HIVE: HiveClient,
            Service.TRADE: TradeClient,
            Service.KLINES: KlinesClient,
            Service.PAY: PayClient,
            Service.METRICS: MetricsClient,
            Service.AUTH: AuthClient,
        }
        self._services: dict[Service, SubClient] = {
            service: client_class(
                self._get_default_config(service), http_client=self._http_client
            )
            for service, client_class in self._service_classes.items()
        }

    @property
    def hive(self) -> HiveClient:
        """
        Entry point for the Hive AI API ([Docs](https://docs.crypticorn.com/api/?api=hive-ai-api)).
        """
        return self._services[Service.HIVE]

    @property
    def trade(self) -> TradeClient:
        """
        Entry point for the Trading API ([Docs](https://docs.crypticorn.com/api/?api=trading-api)).
        """
        return self._services[Service.TRADE]

    @property
    def klines(self) -> KlinesClient:
        """
        Entry point for the Klines API ([Docs](https://docs.crypticorn.com/api/?api=klines-api)).
        """
        return self._services[Service.KLINES]

    @property
    def metrics(self) -> MetricsClient:
        """
        Entry point for the Metrics API ([Docs](https://docs.crypticorn.com/api/?api=metrics-api)).
        """
        return self._services[Service.METRICS]

    @property
    def pay(self) -> PayClient:
        """
        Entry point for the Payment API ([Docs](https://docs.crypticorn.com/api/?api=payment-api)).
        """
        return self._services[Service.PAY]

    @property
    def auth(self) -> AuthClient:
        """
        Entry point for the Auth API ([Docs](https://docs.crypticorn.com/api/?api=auth-api)).
        """
        return self._services[Service.AUTH]

    async def close(self):
        # close each in sync
        for service in self._services.values():
            if hasattr(service.base_client, "close") and self._owns_http_client:
                await service.base_client.close()
        # close shared in async
        if self._http_client and self._owns_http_client:
            await self._http_client.close()
            self._http_client = None

    async def _ensure_session(self) -> None:
        """
        Lazily create the shared HTTP client when first needed and pass it to all subclients.
        """
        if self._http_client is None:
            self._http_client = ClientSession(
                timeout=ClientTimeout(total=30.0),
                connector=TCPConnector(limit=100, limit_per_host=20),
                headers={"User-Agent": f"crypticorn/python/{self.version}"},
            )
            for service in self._services.values():
                if hasattr(service, "base_client") and hasattr(
                    service.base_client, "rest_client"
                ):
                    service.base_client.rest_client.pool_manager = self._http_client

    def _get_default_config(self, service, version=None):
        if version is None:
            version = ApiVersion.V1
        config_class = self._service_classes[service].config_class
        return config_class(
            host=f"{self.base_url}/{version}/{service}",
            access_token=self.jwt,
            api_key={aph.scheme_name: self.api_key} if self.api_key else None,
        )

    def configure(self, config: ConfigT, service: Service) -> None:
        """
        Update a sub-client's configuration by overriding with the values set in the new config.
        Useful for testing a specific service against a local server instead of the default proxy.

        :param config: The new configuration to use for the sub-client.
        :param service: The service to configure.

        Example:
        >>> async with ApiClient() as client:
        ...     client.configure(config=HiveConfig(host="http://localhost:8000"), service=Service.HIVE)
        """
        assert Service.validate(service), f"Invalid service: {service}"
        client = self._services[service]
        new_config = client.config
        for attr in vars(config):
            new_value = getattr(config, attr)
            if new_value:
                setattr(new_config, attr, new_value)
        self._services[service] = type(client)(
            new_config, http_client=self._http_client
        )

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
