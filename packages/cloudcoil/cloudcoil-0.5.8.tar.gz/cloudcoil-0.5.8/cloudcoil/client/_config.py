import base64
import json
import logging
import os
import platform
import ssl
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Literal, Optional, Type, TypeVar, Union, overload

import httpx
import yaml

from cloudcoil._context import context
from cloudcoil.client._api_client import APIClient, AsyncAPIClient
from cloudcoil.resources import GVK, Resource
from cloudcoil.version import __version__

logger = logging.getLogger(__name__)

DEFAULT_SSL_CONTEXT: Union[ssl.SSLContext, "truststore.SSLContext"]
try:
    import truststore

    DEFAULT_SSL_CONTEXT = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    logger.debug("Using truststore for SSL context")
except ImportError:
    DEFAULT_SSL_CONTEXT = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    logger.debug("Using default SSL context")


class ExecAuthenticator(httpx.Auth):
    def __init__(self, exec_config: Dict[str, Any]):
        self.exec_config = exec_config
        self._token_cache: Optional[Dict[str, Any]] = None
        self._token_expiry: Optional[float] = None
        logger.debug("Initialized ExecAuthenticator with command: %s", exec_config["command"])

    def _execute_command(self) -> Dict[str, Any]:
        cmd = [self.exec_config["command"]]
        if "args" in self.exec_config:
            cmd.extend(self.exec_config["args"])

        env = os.environ.copy()
        if self.exec_config.get("env"):
            for env_var in self.exec_config["env"]:
                env[env_var["name"]] = env_var["value"]

        logger.debug("Executing auth command: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def _get_token(self) -> Dict[str, Any]:
        now = time.time()

        if self._token_cache is not None and self._token_expiry is not None:
            # Add 30-second buffer to prevent edge cases
            if now < self._token_expiry - 30:
                logger.debug(
                    "Using cached token (expires in %0.1f seconds)", self._token_expiry - now
                )
                return self._token_cache

        status = self._execute_command()["status"]
        self._token_cache = status

        if "expirationTimestamp" in status:
            expiry = datetime.strptime(status["expirationTimestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            self._token_expiry = expiry.timestamp()
            logger.debug("Refreshed token (expires in %0.1f seconds)", self._token_expiry - now)
        else:
            self._token_expiry = None
            logger.debug("Refreshed token (no expiration)")

        return status

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        status = self._get_token()

        if "token" in status:
            token = status["token"]
            request.headers["Authorization"] = f"Bearer {token}"
        yield request


T = TypeVar("T", bound=Resource)
Auth = Callable[[httpx.Request], httpx.Request] | httpx.Auth | None

DEFAULT_KUBECONFIG = Path.home() / ".kube" / "config"
INCLUSTER_TOKEN_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
INCLUSTER_CERT_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
INCLUSTER_NAMESPACE_PATH = Path("/var/run/secrets/kubernetes.io/serviceaccount/namespace")


class Config:
    def __init__(
        self,
        kubeconfig: Path | str | None = None,
        server: str | None = None,
        namespace: str | None = None,
        token: str | None = None,
        auth: Auth = None,
        cafile: Path | None = None,
        certfile: Path | None = None,
        keyfile: Path | None = None,
        context: str | None = None,
        skip_verify: bool = False,
    ) -> None:
        self.server = None
        self.namespace = "default"
        self.auth: Auth = None
        self.cafile = None
        self.certfile = None
        self.keyfile = None
        self.token = None
        self.skip_verify = False
        tempdir = tempfile.TemporaryDirectory()
        kubeconfig = kubeconfig or os.environ.get("KUBECONFIG")
        if kubeconfig:
            kubeconfig = Path(kubeconfig)
            if not kubeconfig.is_file():
                logger.error("Kubeconfig not found: %s", kubeconfig)
                raise ValueError(f"Kubeconfig {kubeconfig} is not a file")
        else:
            kubeconfig = DEFAULT_KUBECONFIG
            logger.debug("Using default kubeconfig: %s", kubeconfig)

        if kubeconfig.is_file():
            logger.debug("Loading kubeconfig from: %s", kubeconfig)
            kubeconfig_data = yaml.safe_load(kubeconfig.read_text())
            if "clusters" not in kubeconfig_data:
                logger.error("Invalid kubeconfig: missing clusters section")
                raise ValueError(f"Kubeconfig {kubeconfig} does not have clusters")
            if "contexts" not in kubeconfig_data:
                logger.error("Invalid kubeconfig: missing contexts section")
                raise ValueError(f"Kubeconfig {kubeconfig} does not have contexts")
            if "users" not in kubeconfig_data:
                logger.error("Invalid kubeconfig: missing users section")
                raise ValueError(f"Kubeconfig {kubeconfig} does not have users")
            if not context and "current-context" not in kubeconfig_data:
                logger.error("Invalid kubeconfig: no current-context specified")
                raise ValueError(f"Kubeconfig {kubeconfig} does not have current-context")
            current_context = context or kubeconfig_data["current-context"]
            logger.debug("Using context: %s", current_context)

            for data in kubeconfig_data["contexts"]:
                if data["name"] == current_context:
                    break
            else:
                logger.error("Context not found in kubeconfig: %s", current_context)
                raise ValueError(f"Kubeconfig {kubeconfig} does not have context {current_context}")
            context_data = data["context"]

            for data in kubeconfig_data["clusters"]:
                if data["name"] == context_data["cluster"]:
                    break
            else:
                logger.error("Cluster not found in kubeconfig: %s", context_data["cluster"])
                raise ValueError(
                    f"Kubeconfig {kubeconfig} does not have cluster {context_data['cluster']}"
                )
            cluster_data = data["cluster"]

            for data in kubeconfig_data["users"]:
                if data["name"] == context_data["user"]:
                    break
            else:
                logger.error("User not found in kubeconfig: %s", context_data["user"])
                raise ValueError(
                    f"Kubeconfig {kubeconfig} does not have user {context_data['user']}"
                )
            user_data = data["user"]

            self.server = cluster_data["server"]
            logger.debug("Using server: %s", self.server)

            if "certificate-authority" in cluster_data:
                self.cafile = cluster_data["certificate-authority"]
                logger.debug("Using CA file: %s", self.cafile)
            if "certificate-authority-data" in cluster_data:
                # Write certificate to disk at a temporary location and use it
                cafile = Path(tempdir.name) / "ca.crt"
                cafile.write_bytes(base64.b64decode(cluster_data["certificate-authority-data"]))
                self.cafile = cafile
                logger.debug("Using temporary CA file: %s", self.cafile)

            if "insecure-skip-tls-verify" in cluster_data:
                self.skip_verify = cluster_data["insecure-skip-tls-verify"]
                if self.skip_verify:
                    logger.warning("TLS verification disabled")

            if "namespace" in context_data:
                self.namespace = context_data["namespace"]
                logger.debug("Using namespace from context: %s", self.namespace)

            if "exec" in user_data:
                logger.debug("Using exec auth provider")
                self.auth = ExecAuthenticator(user_data["exec"])
            elif "token" in user_data:
                logger.debug("Using static token auth")
                self.token = user_data["token"]
            elif "client-certificate" in user_data and "client-key" in user_data:
                self.certfile = user_data["client-certificate"]
                self.keyfile = user_data["client-key"]
                logger.debug(
                    "Using client certificate auth: cert=%s key=%s", self.certfile, self.keyfile
                )
            elif "client-certificate-data" in user_data and "client-key-data" in user_data:
                # Write client certificate and key to disk at a temporary location
                # and use them
                client_cert = Path(tempdir.name) / "client.crt"
                client_cert.write_bytes(base64.b64decode(user_data["client-certificate-data"]))
                client_key = Path(tempdir.name) / "client.key"
                client_key.write_bytes(base64.b64decode(user_data["client-key-data"]))
                self.certfile = client_cert
                self.keyfile = client_key
                logger.debug(
                    "Using temporary client certificate auth: cert=%s key=%s",
                    self.certfile,
                    self.keyfile,
                )

        elif INCLUSTER_TOKEN_PATH.is_file():
            logger.debug("Detected in-cluster environment")
            self.server = "https://kubernetes.default.svc"
            self.namespace = INCLUSTER_NAMESPACE_PATH.read_text()
            self.token = INCLUSTER_TOKEN_PATH.read_text()
            if INCLUSTER_CERT_PATH.is_file():
                self.cafile = INCLUSTER_CERT_PATH
                logger.debug("Using in-cluster CA file: %s", self.cafile)

        self.server = server or self.server or "https://localhost:6443"
        self.namespace = namespace or self.namespace
        self.token = token or self.token
        self.auth = auth or self.auth
        self.cafile = cafile or self.cafile
        self.certfile = certfile or self.certfile
        self.keyfile = keyfile or self.keyfile
        self.skip_verify = skip_verify or self.skip_verify

        ctx: ssl.SSLContext | None = None
        if self.cafile:
            logger.debug("Creating SSL context with CA file: %s", self.cafile)
            ctx = ssl.create_default_context(cafile=self.cafile)
        else:
            logger.debug("Using default SSL context")
            ctx = DEFAULT_SSL_CONTEXT

        if self.certfile:
            logger.debug("Loading client certificate: cert=%s key=%s", self.certfile, self.keyfile)
            ctx.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        if self.skip_verify:
            logger.warning("Using insecure SSL context (verify=False)")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        headers = {
            "User-Agent": f"cloudcoil/{__version__} ({platform.platform()}) python/{platform.python_version()}",
        }
        if self.token:
            logger.debug("Adding token authentication to headers")
            headers["Authorization"] = f"Bearer {self.token}"

        logger.debug("Creating HTTP clients for server %s", self.server)
        self.client = httpx.Client(
            verify=ctx, auth=self.auth or None, base_url=self.server, headers=headers
        )
        self.async_client = httpx.AsyncClient(
            verify=ctx, auth=self.auth or None, base_url=self.server, headers=headers
        )
        self._rest_mapping: dict[GVK, Any] = {}

    def _create_rest_mapper(self):
        logger.debug("Fetching Kubernetes version")
        version_response = self.client.get("/version")
        if version_response.status_code != 200:
            logger.error("Failed to get Kubernetes version: %s", version_response.text)
            raise ValueError(f"Failed to get version: {version_response.text}")
        version_data = version_response.json()
        major = int("".join(filter(str.isdigit, version_data["major"])))
        minor = int("".join(filter(str.isdigit, version_data["minor"])))
        logger.debug("Connected to Kubernetes %s.%s", major, minor)

        if major > 1 or (major == 1 and minor >= 30):
            try:
                logger.debug("Attempting aggregated API discovery")
                if self._try_aggregated_discovery():
                    return
            except Exception as e:
                logger.debug("Aggregated discovery failed, falling back to traditional: %s", e)

        logger.debug("Using traditional API discovery")
        self._traditional_discovery()

    def _try_aggregated_discovery(self) -> bool:
        logger.debug("Fetching core API groups")
        api_response = self.client.get(
            "/api",
            headers={
                "Accept": "application/json;v=v2;g=apidiscovery.k8s.io;as=APIGroupDiscoveryList"
            },
        )
        if api_response.status_code != 200:
            logger.debug("Core API groups not available in aggregated format")
            return False
        self._process_api_discovery(api_response.json())

        logger.debug("Fetching extension API groups")
        apis_response = self.client.get(
            "/apis",
            headers={
                "Accept": "application/json;v=v2;g=apidiscovery.k8s.io;as=APIGroupDiscoveryList"
            },
        )
        if apis_response.status_code != 200:
            logger.debug("Extension API groups not available in aggregated format")
            return False
        self._process_api_discovery(apis_response.json())
        return True

    def _traditional_discovery(self):
        logger.debug("Fetching core API versions")
        api_response = self.client.get("/api")
        if api_response.status_code == 200:
            for version in api_response.json().get("versions", []):
                logger.debug("Fetching resources for core API version: %s", version)
                version_response = self.client.get(f"/api/{version}")
                if version_response.status_code == 200:
                    self._process_api_resources("", version, version_response.json())

        logger.debug("Fetching API groups")
        apis_response = self.client.get("/apis")
        if apis_response.status_code != 200:
            logger.error("Failed to get API groups: %s", apis_response.text)
            raise ValueError(f"Failed to get APIs: {apis_response.text}")

        for group in apis_response.json().get("groups", []):
            group_name = group["name"]
            for version_data in group["versions"]:
                version = version_data["version"]
                logger.debug("Fetching resources for API group: %s/%s", group_name, version)
                group_response = self.client.get(f"/apis/{group_name}/{version}")
                if group_response.status_code == 200:
                    self._process_api_resources(group_name, version, group_response.json())

    def _process_api_discovery(self, api_discovery):
        if not isinstance(api_discovery, dict) or "items" not in api_discovery:
            logger.debug("Invalid API discovery response format")
            return

        for api in api_discovery["items"]:
            group = api.get("metadata", {}).get("name", "")
            for version_data in api.get("versions", []):
                version = version_data.get("version")
                if not version:
                    continue

                for resource_data in version_data.get("resources", []):
                    kind = resource_data.get("responseKind", {}).get("kind")
                    resource = resource_data.get("resource")
                    scope = resource_data.get("scope")
                    subresources = list(
                        map(lambda sr: sr["subresource"], resource_data.get("subresources", {}))
                    )

                    if not all([kind, resource, scope]):
                        continue

                    namespaced = scope == "Namespaced"
                    api_version = f"{group}/{version}" if group != "" else version
                    logger.debug(
                        "Registered API resource: %s/%s (namespaced=%s)",
                        api_version,
                        kind,
                        namespaced,
                    )
                    self._rest_mapping[GVK(api_version=api_version, kind=kind)] = {
                        "namespaced": namespaced,
                        "resource": resource,
                        "subresources": subresources,
                    }

    def _process_api_resources(self, group: str, version: str, data: dict):
        api_version = f"{group}/{version}" if group else version

        for resource in data.get("resources", []):
            if "/" in resource["name"]:
                continue

            kind = resource["kind"]
            namespaced = resource["namespaced"]
            resource_name = resource["name"]
            subresources: list[str] = []

            logger.debug(
                "Registered API resource: %s/%s (namespaced=%s)",
                api_version,
                kind,
                namespaced,
            )
            self._rest_mapping[GVK(api_version=api_version, kind=kind)] = {
                "namespaced": namespaced,
                "resource": resource_name,
                "subresources": subresources,
            }
            for subresource in data.get("resources", []):
                if subresource["name"].startswith(f"{resource_name}/"):
                    subresources.append(subresource["name"].split("/", 1)[1])

    @overload
    def client_for(self, resource: Type[T], sync: Literal[True] = True) -> APIClient[T]: ...

    @overload
    def client_for(self, resource: Type[T], sync: Literal[False] = False) -> AsyncAPIClient[T]: ...

    def client_for(
        self, resource: Type[T], sync: Literal[False, True] = True
    ) -> APIClient[T] | AsyncAPIClient[T]:
        self.initialize()
        if not issubclass(resource, Resource):
            logger.error("Invalid resource type: %s", resource)
            raise ValueError(f"Resource {resource} is not a cloudcoil.Resource")
        gvk = resource.gvk()
        if gvk not in self._rest_mapping:
            logger.error("Resource not registered with API server: %s", gvk)
            raise ValueError(f"Resource with {gvk=} is not registered with the server")

        logger.debug("Creating %s client for %s", "sync" if sync else "async", gvk)
        if sync:
            return APIClient(
                api_version=gvk.api_version,
                kind=resource,
                resource=self._rest_mapping[gvk]["resource"],
                namespaced=self._rest_mapping[gvk]["namespaced"],
                subresources=self._rest_mapping[gvk]["subresources"],
                default_namespace=self.namespace,
                client=self.client,
            )
        return AsyncAPIClient(
            api_version=gvk.api_version,
            kind=resource,
            resource=self._rest_mapping[gvk]["resource"],
            namespaced=self._rest_mapping[gvk]["namespaced"],
            subresources=self._rest_mapping[gvk]["subresources"],
            default_namespace=self.namespace,
            client=self.async_client,
        )

    def set_default(self) -> None:
        logger.debug("Setting as default config")
        context.set_default(self)

    def initialize(self):
        if not self._rest_mapping:
            logger.debug("Initializing API resource mapping")
            self._create_rest_mapper()

    def activate(self):
        logger.debug("Activating config")
        self.__enter__()

    def deactivate(self):
        logger.debug("Deactivating config")
        self.__exit__()

    def __enter__(self):
        self.initialize()
        context._enter(self)
        return self

    def __exit__(self, *_):
        context._exit()

    def refresh_api_resources(self) -> None:
        logger.debug("Refreshing API resource mapping")
        self._rest_mapping.clear()
        self._create_rest_mapper()
