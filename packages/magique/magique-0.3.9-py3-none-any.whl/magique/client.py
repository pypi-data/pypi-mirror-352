import typing as T
import asyncio
import uuid
import inspect
import time

from .protocol import (
    ServiceInfo, InvokeServiceRequest, InvokeServiceResponse,
    InvokeFuture, GetFutureResultRequest,
)
from .utils.log import logger
from .ser import DefaultSerializer
from .utils.network import ws_connect
from .base import NetworkObject


class MagiqueError(Exception):
    pass


class MagiqueFutureError(MagiqueError):
    pass


class LoginError(MagiqueError):
    pass


class PyFunction:
    def __init__(self, func: T.Callable):
        self.func = func


class ServiceProxy(NetworkObject):
    def __init__(
        self,
        url: str,
        client_id: T.Optional[str] = None,
        service_info: T.Optional[ServiceInfo] = None,
        serializer: T.Optional[DefaultSerializer] = None,
        jwt: T.Optional[str] = None,
    ):
        super().__init__(serializer or DefaultSerializer())
        self.url = url
        self.service_info = service_info
        self._connection = None
        self.client_id = client_id
        if self.client_id is None:
            self.client_id = str(uuid.uuid4())
        self.jwt = jwt
        self.direct_connection = False

    @property
    def protocol(self):
        return self.url.split("://")[0]

    async def ensure_connection(
        self,
        force: bool = True,
        ping_timeout: float = 0.1,
    ):
        if force:
            _connection = await ws_connect(self.url)
            self._connection = _connection
            return _connection
        if self._connection is None:
            self._connection = await ws_connect(self.url)
        else:
            try:
                await asyncio.wait_for(self.ping(), timeout=ping_timeout)
            except Exception:
                self._connection = await ws_connect(self.url)
        return self._connection

    async def ping(self):
        await self.send_message(self._connection, {"action": "ping"})
        msg = await self.receive_message(self._connection)
        assert msg["message"] == "pong"

    async def invoke(
        self,
        function_name: str,
        parameters: dict | None = None,
        return_future: bool = False,
    ) -> T.Any:
        invoke_id = str(uuid.uuid4())
        if parameters is None:
            parameters = {}
        reverse_callables = {}
        for k, v in parameters.items():
            if isinstance(v, T.Callable):
                reverse_callables[k] = v
                _parameters = inspect.signature(v).parameters
                parameters[k] = {
                    "reverse_callable": True,
                    "name": k,
                    "invoke_id": invoke_id,
                    "parameters": list(_parameters.keys()),
                    "is_async": inspect.iscoroutinefunction(v),
                }
            elif isinstance(v, PyFunction):
                parameters[k] = v.func  # pass the function object

        request = InvokeServiceRequest(
            client_id=self.client_id,
            service_id=self.service_info.service_id,
            function_name=function_name,
            parameters=parameters,
            return_future=return_future,
            invoke_id=invoke_id,
        )
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request.encode())
        response = None
        while True:
            resp = await self.receive_message(websocket)
            action = resp.get("action")
            logger.debug(f"Received action while waiting for result: {action}")
            if action == "reverse_invoke":
                await self.handle_reverse_invoke(websocket, resp, reverse_callables)
            else:
                if return_future:
                    response = InvokeFuture.decode(resp)
                else:
                    response = InvokeServiceResponse.decode(resp)
                    if resp.get("status") == "error":
                        raise MagiqueError(resp.get("message") or resp.get("result"))
                    response = response.result
                break
        await websocket.close()
        return response

    async def handle_reverse_invoke(self, websocket, request: dict, reverse_callables: dict):
        name = request["name"]
        parameters = request["parameters"]
        func = reverse_callables[name]
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**parameters)
            else:
                result = func(**parameters)
            status = "success"
        except Exception as e:
            result = str(e)
            status = "error"
        await self.send_message(websocket, {
            "action": "reverse_invoke_result",
            "result": result,
            "status": status,
            "reverse_invoke_id": request["reverse_invoke_id"],
        })

    async def fetch_service_info(self) -> ServiceInfo:
        request = {"action": "get_service_info"}
        if self.service_info is not None:
            request["name_or_id"] = self.service_info.service_id
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request)
        resp = await self.receive_message(websocket)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))
        response = ServiceInfo.decode(resp["service"])
        self.service_info = response
        return response

    async def fetch_future_result(self, future: InvokeFuture) -> T.Any:
        request = GetFutureResultRequest(future)
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request.encode())
        resp = await self.receive_message(websocket)
        if resp.get("status") == "error":
            raise MagiqueFutureError(resp.get("message"))
        response = InvokeServiceResponse.decode(resp)
        return response.result

    async def try_direct_connection(self, timeout: float = 1.0):
        logger.info(
            f"Trying direct connection to {self.service_info.service_name}")
        port = self.service_info.worker_server_port

        async def try_connect_to_ip(ip: str):
            url = f"ws://{ip}:{port}"
            try:
                t1 = time.time()
                async with ws_connect(
                    url,
                    ping_timeout=timeout,
                    open_timeout=timeout,
                ):
                    self.url = url
                    self.direct_connection = True
                    t2 = time.time()
                    d = t2 - t1
                    logger.info(f"Direct connection to {url} in {d} seconds")
                    return d, url
            except Exception as e:
                logger.debug(f"Error connecting to {url}: {e}")
                return None, None

        coroutines = []
        for ip in self.service_info.potential_ip_addresses:
            coroutines.append(try_connect_to_ip(ip))
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        results = [r for r in results if r is not None]
        results = [r for r in results if r[0] is not None]
        results.sort(key=lambda x: x[0])

        if len(results) > 0:
            self.url = results[0][1]
            self.direct_connection = True
            logger.info(f"Connected to {self.url} in {results[0][0]} seconds")
        else:
            logger.warning(
                "Failed to connect to any potential ip address, "
                "using the server as a fallback"
            )

    async def close_connection(self):
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


class ServerProxy(NetworkObject):
    def __init__(
        self,
        url: str,
        serializer: T.Optional[DefaultSerializer] = None,
    ):
        super().__init__(serializer or DefaultSerializer())
        self.url = url
        self.jwt = None
        self.client_id = str(uuid.uuid4())

    async def list_services(self) -> T.List[ServiceInfo]:
        async with ws_connect(self.url) as websocket:
            await self.send_message(
                websocket,
                {"action": "get_services", "jwt": self.jwt}
            )
            response = await self.receive_message(websocket)
            services = [
                ServiceInfo.decode(service)
                for service in response["services"]
            ]
            return services

    async def get_service(
        self,
        name_or_id: str,
        try_direct_connection: bool = True,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceProxy:
        request = {
            "action": "get_service_info",
            "name_or_id": name_or_id,
            "choice_strategy": choice_strategy,
            "jwt": self.jwt,
        }
        async with ws_connect(self.url) as websocket:
            await self.send_message(websocket, request)
            resp = await self.receive_message(websocket)
            if resp.get("status") == "error":
                raise MagiqueError(resp.get("message"))
        service = ServiceInfo.decode(resp["service"])
        proxy = ServiceProxy(self.url, self.client_id, service, self.serializer, self.jwt)
        if service.use_worker_server and try_direct_connection:
            await proxy.try_direct_connection()
        return proxy

    async def ping(self):
        async with ws_connect(self.url) as websocket:
            await self.send_message(websocket, {"action": "ping"})
            msg = await self.receive_message(websocket)
            assert msg["message"] == "pong"

    async def login(self):
        if self.jwt is not None:
            logger.info("Already logged in.")
            return
        async with ws_connect(self.url) as websocket:
            await self.send_message(websocket, {"action": "login"})
            msg = await self.receive_message(websocket)
            auth_url = msg["auth_url"]
            logger.info(f"Open this URL in your browser to log in:\n{auth_url}")
            msg = await self.receive_message(websocket)
            if msg.get("status") == "error":
                raise LoginError(msg.get("message"))
            jwt = msg.get("jwt")
            self.jwt = jwt
            logger.info("Login successful!")


async def connect_to_server(
    url: str,
    **kwargs,
) -> ServerProxy:
    server = ServerProxy(
        url,
        **kwargs,
    )
    await server.ping()
    return server


async def connect_to_service(url: str, **kwargs) -> ServiceProxy:
    service_proxy = ServiceProxy(url, **kwargs)
    await service_proxy.fetch_service_info()
    return service_proxy
