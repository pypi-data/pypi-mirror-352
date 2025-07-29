"""Tests for config"""

import json
import os
import ssl
from unittest.mock import patch

import pytest
import yaml
from httpx import Response

from cloudcoil.client._config import (
    Config,
)


@pytest.mark.parametrize(
    "kubeconfig_content,expected",
    [
        # Test case 1: Basic kubeconfig
        (
            {
                "current-context": "test-context",
                "contexts": [
                    {
                        "name": "test-context",
                        "context": {
                            "cluster": "test-cluster",
                            "user": "test-user",
                            "namespace": "test-ns",
                        },
                    }
                ],
                "clusters": [
                    {
                        "name": "test-cluster",
                        "cluster": {"server": "https://test-server"},
                    }
                ],
                "users": [{"name": "test-user", "user": {"token": "test-token"}}],
            },
            {
                "server": "https://test-server",
                "namespace": "test-ns",
                "token": "test-token",
                "ssl_verify_mode": ssl.CERT_REQUIRED,
            },
        ),
        # Test case 2: Kubeconfig with certificate data
        (
            {
                "current-context": "test-context",
                "contexts": [
                    {
                        "name": "test-context",
                        "context": {"cluster": "test-cluster", "user": "test-user"},
                    }
                ],
                "clusters": [
                    {
                        "name": "test-cluster",
                        "cluster": {
                            "server": "https://test-server",
                            "certificate-authority-data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkakNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUzTXpVME1EY3lOek13SGhjTk1qUXhNakk0TVRjek5ETXpXaGNOTXpReE1qSTJNVGN6TkRNegpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUzTXpVME1EY3lOek13V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFTeGVETlErSE9FVHZDUUtSWTVqR2JCblUwcXBBUHM2akNyeFE5QXBpd0YKWXJqMlZSOFBEUnVYWWE1L1o5STRlT0NxSkljZWFjckNVUUNRUUhOZU94Y1hvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVUJXWDhYelZQcDF5d3YwZXRXQlpOCnNEbmpTckl3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdSQUlnYWx0RmNxTGlXNTdiemxlYXFVV1pXOXhTTTM2OUFmK2EKamNUakZJZ0ZzZHNDSUNYR3lid2pUUTVMZk1taFRoTytMaGhxT1ZpdDBQV1JMN1dTV255NDlSTGQKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=",  # base64 encoded "certdata"
                        },
                    }
                ],
                "users": [
                    {
                        "name": "test-user",
                        "user": {
                            "client-certificate-data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJrakNDQVRlZ0F3SUJBZ0lJV2hxakpvUFR6Qkl3Q2dZSUtvWkl6ajBFQXdJd0l6RWhNQjhHQTFVRUF3d1kKYXpOekxXTnNhV1Z1ZEMxallVQXhOek0xTkRBM01qY3pNQjRYRFRJME1USXlPREUzTXpRek0xb1hEVEkxTVRJeQpPREUzTXpRek0xb3dNREVYTUJVR0ExVUVDaE1PYzNsemRHVnRPbTFoYzNSbGNuTXhGVEFUQmdOVkJBTVRESE41CmMzUmxiVHBoWkcxcGJqQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJBaXVzZ3ExcG9QYkM3S3AKbVU4UmRKZDU1K3BkY1dVZkF1Z3h1S29ucEMxVmpERHRXaEpEWkxycktsQWk4ZkxlMkJRV29aOEVXSDNkTmxtVwpmb093K2RXalNEQkdNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUtCZ2dyQmdFRkJRY0RBakFmCkJnTlZIU01FR0RBV2dCVHZTQlQrVk83b2s5MkJ5T2pkRnRacmo5a21oVEFLQmdncWhrak9QUVFEQWdOSkFEQkcKQWlFQXZVcGdYU3d2akpkaUdaUEJJVHhnTmNZdHA2VDVJbjN2eDUzRmZXeGVlcjRDSVFDWDhveWZwVGl5aTljSQplNGRlUTdSR1ZuaTErNDhabXBOL1M5QXRNd2pIV0E9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCi0tLS0tQkVHSU4gQ0VSVElGSUNBVEUtLS0tLQpNSUlCZHpDQ0FSMmdBd0lCQWdJQkFEQUtCZ2dxaGtqT1BRUURBakFqTVNFd0h3WURWUVFEREJock0zTXRZMnhwClpXNTBMV05oUURFM016VTBNRGN5TnpNd0hoY05NalF4TWpJNE1UY3pORE16V2hjTk16UXhNakkyTVRjek5ETXoKV2pBak1TRXdId1lEVlFRRERCaHJNM010WTJ4cFpXNTBMV05oUURFM016VTBNRGN5TnpNd1dUQVRCZ2NxaGtqTwpQUUlCQmdncWhrak9QUU1CQndOQ0FBU2hrNHpxa2dXNU96NnMzNWpoa0JzenBtazRwS0ROa2FKWGpaWTlIakcvCkR3N0VwcXFLT0prTEQvbEZjUk9nY1czdDBZajgxM3pOTmpXcmdUbTN4YjY3bzBJd1FEQU9CZ05WSFE4QkFmOEUKQkFNQ0FxUXdEd1lEVlIwVEFRSC9CQVV3QXdFQi96QWRCZ05WSFE0RUZnUVU3MGdVL2xUdTZKUGRnY2pvM1JiVwphNC9aSm9Vd0NnWUlLb1pJemowRUF3SURTQUF3UlFJZ2VvTWViOFcrRzFpTjZDcW5tQm5QOGg4TDYzNWsrTXhFCnJzNnBYYUN1SEFJQ0lRRERJVWRlR1BjTUQ2eW1JVE1xbnBuUVkxMFp3cGkzQWxZUVFJcDNjb05iM2c9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==",  # base64 encoded "clientcert"
                            "client-key-data": "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU8wN1hGT0lmTVFyS3Z6Skp4OEkrbnpCQXdnZmpuVGdWZ3o4L2JiRi9Sc1hvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFQ0s2eUNyV21nOXNMc3FtWlR4RjBsM25uNmwxeFpSOEM2REc0cWlla0xWV01NTzFhRWtOawp1dXNxVUNMeDh0N1lGQmFobndSWWZkMDJXWlorZzdENTFRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=",  # base64 encoded "clientkey"
                        },
                    }
                ],
            },
            {
                "server": "https://test-server",
                "namespace": "default",
                "ssl_verify_mode": ssl.CERT_REQUIRED,
            },
        ),
        # Test case 3: Kubeconfig with insecure-skip-tls
        (
            {
                "current-context": "test-context",
                "contexts": [
                    {
                        "name": "test-context",
                        "context": {"cluster": "test-cluster", "user": "test-user"},
                    }
                ],
                "clusters": [
                    {
                        "name": "test-cluster",
                        "cluster": {
                            "server": "https://test-server",
                            "insecure-skip-tls-verify": True,
                        },
                    }
                ],
                "users": [
                    {
                        "name": "test-user",
                        "user": {
                            "client-certificate-data": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJrakNDQVRlZ0F3SUJBZ0lJV2hxakpvUFR6Qkl3Q2dZSUtvWkl6ajBFQXdJd0l6RWhNQjhHQTFVRUF3d1kKYXpOekxXTnNhV1Z1ZEMxallVQXhOek0xTkRBM01qY3pNQjRYRFRJME1USXlPREUzTXpRek0xb1hEVEkxTVRJeQpPREUzTXpRek0xb3dNREVYTUJVR0ExVUVDaE1PYzNsemRHVnRPbTFoYzNSbGNuTXhGVEFUQmdOVkJBTVRESE41CmMzUmxiVHBoWkcxcGJqQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJBaXVzZ3ExcG9QYkM3S3AKbVU4UmRKZDU1K3BkY1dVZkF1Z3h1S29ucEMxVmpERHRXaEpEWkxycktsQWk4ZkxlMkJRV29aOEVXSDNkTmxtVwpmb093K2RXalNEQkdNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUtCZ2dyQmdFRkJRY0RBakFmCkJnTlZIU01FR0RBV2dCVHZTQlQrVk83b2s5MkJ5T2pkRnRacmo5a21oVEFLQmdncWhrak9QUVFEQWdOSkFEQkcKQWlFQXZVcGdYU3d2akpkaUdaUEJJVHhnTmNZdHA2VDVJbjN2eDUzRmZXeGVlcjRDSVFDWDhveWZwVGl5aTljSQplNGRlUTdSR1ZuaTErNDhabXBOL1M5QXRNd2pIV0E9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCi0tLS0tQkVHSU4gQ0VSVElGSUNBVEUtLS0tLQpNSUlCZHpDQ0FSMmdBd0lCQWdJQkFEQUtCZ2dxaGtqT1BRUURBakFqTVNFd0h3WURWUVFEREJock0zTXRZMnhwClpXNTBMV05oUURFM016VTBNRGN5TnpNd0hoY05NalF4TWpJNE1UY3pORE16V2hjTk16UXhNakkyTVRjek5ETXoKV2pBak1TRXdId1lEVlFRRERCaHJNM010WTJ4cFpXNTBMV05oUURFM016VTBNRGN5TnpNd1dUQVRCZ2NxaGtqTwpQUUlCQmdncWhrak9QUU1CQndOQ0FBU2hrNHpxa2dXNU96NnMzNWpoa0JzenBtazRwS0ROa2FKWGpaWTlIakcvCkR3N0VwcXFLT0prTEQvbEZjUk9nY1czdDBZajgxM3pOTmpXcmdUbTN4YjY3bzBJd1FEQU9CZ05WSFE4QkFmOEUKQkFNQ0FxUXdEd1lEVlIwVEFRSC9CQVV3QXdFQi96QWRCZ05WSFE0RUZnUVU3MGdVL2xUdTZKUGRnY2pvM1JiVwphNC9aSm9Vd0NnWUlLb1pJemowRUF3SURTQUF3UlFJZ2VvTWViOFcrRzFpTjZDcW5tQm5QOGg4TDYzNWsrTXhFCnJzNnBYYUN1SEFJQ0lRRERJVWRlR1BjTUQ2eW1JVE1xbnBuUVkxMFp3cGkzQWxZUVFJcDNjb05iM2c9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==",  # base64 encoded "clientcert"
                            "client-key-data": "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU8wN1hGT0lmTVFyS3Z6Skp4OEkrbnpCQXdnZmpuVGdWZ3o4L2JiRi9Sc1hvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFQ0s2eUNyV21nOXNMc3FtWlR4RjBsM25uNmwxeFpSOEM2REc0cWlla0xWV01NTzFhRWtOawp1dXNxVUNMeDh0N1lGQmFobndSWWZkMDJXWlorZzdENTFRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=",  # base64 encoded "clientkey"
                        },
                    }
                ],
            },
            {
                "server": "https://test-server",
                "namespace": "default",
                "ssl_verify_mode": ssl.CERT_NONE,
            },
        ),
    ],
)
def test_kubeconfig_initialization(kubeconfig_content, expected, tmp_path):
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    with patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}):
        client = Config()
        assert client.server == expected["server"]
        assert client.namespace == expected["namespace"]
        if "token" in expected:
            assert client.token == expected["token"]

        # Context information like `verify=<ctx or bool>` passed to the httpx.Client is only reflected on the transport pool
        assert (
            client.client._transport._pool._ssl_context.verify_mode == expected["ssl_verify_mode"]
        )


@pytest.mark.parametrize(
    "params,expected",
    [
        (
            {
                "server": "https://custom-server",
                "namespace": "custom-ns",
                "token": "custom-token",
            },
            {
                "server": "https://custom-server",
                "namespace": "custom-ns",
                "token": "custom-token",
            },
        ),
        (
            {"server": "https://custom-server"},
            {"server": "https://custom-server", "namespace": "default", "token": None},
        ),
    ],
)
def test_direct_parameter_initialization(
    params,
    expected,
):
    client = Config(**params)
    assert client.server == expected["server"]
    assert client.namespace == expected["namespace"]
    assert client.token == expected["token"]


@pytest.mark.parametrize(
    "kubeconfig_content",
    [
        {"current-context": "test-context"},  # Missing required sections
        {
            "current-context": "test-context",
            "contexts": [],
            "clusters": [],
            "users": [],
        },  # Empty required sections
        {"contexts": [], "clusters": [], "users": []},  # Missing current-context
    ],
)
def test_invalid_kubeconfig(kubeconfig_content, tmp_path):
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    with patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}):
        with pytest.raises(ValueError):
            Config()


def test_incluster_initialization(tmp_path):
    token_path = tmp_path / "token"
    ca_path = tmp_path / "ca.crt"
    namespace_path = tmp_path / "namespace"

    # Create mock in-cluster files
    token_path.write_text("test-token")
    namespace_path.write_text("test-namespace")

    with (
        patch("cloudcoil.client._config.INCLUSTER_TOKEN_PATH", token_path),
        patch("cloudcoil.client._config.INCLUSTER_CERT_PATH", ca_path),
        patch("cloudcoil.client._config.DEFAULT_KUBECONFIG", tmp_path / "dne"),
        patch("cloudcoil.client._config.INCLUSTER_NAMESPACE_PATH", namespace_path),
    ):
        client = Config()
        assert client.server == "https://kubernetes.default.svc"
        assert client.namespace == "test-namespace"
        assert client.token == "test-token"


class MockTransport:
    def handle_request(self, request):
        return Response(200)


@pytest.mark.parametrize(
    "kubeconfig_content,exec_output,expected_headers",
    [
        # Test exec auth with token output
        (
            {
                "current-context": "test-context",
                "contexts": [
                    {
                        "name": "test-context",
                        "context": {"cluster": "test-cluster", "user": "test-user"},
                    }
                ],
                "clusters": [
                    {
                        "name": "test-cluster",
                        "cluster": {"server": "https://test-server"},
                    }
                ],
                "users": [
                    {
                        "name": "test-user",
                        "user": {
                            "exec": {
                                "command": "aws",
                                "args": ["eks", "get-token", "--cluster-name", "test-cluster"],
                                "env": [{"name": "AWS_PROFILE", "value": "test"}],
                            }
                        },
                    }
                ],
            },
            {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "status": {
                    "token": "test-exec-token",
                    "expirationTimestamp": "2024-12-31T23:59:59Z",
                },
            },
            {"Authorization": "Bearer test-exec-token"},
        ),
    ],
)
def test_exec_auth(kubeconfig_content, exec_output, expected_headers, tmp_path):
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    mock_transport = MockTransport()

    with (
        patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}),
        patch("cloudcoil.client._config.subprocess.run") as mock_run,
    ):
        # Setup mock subprocess.run
        mock_run.return_value.stdout = json.dumps(exec_output)
        mock_run.return_value.check = True

        config = Config()
        config.client._transport = mock_transport
        config.client.get("/")

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0][0] == "aws"  # Command
        assert "eks" in args[0]  # Args
        assert kwargs["env"].get("AWS_PROFILE") == "test"  # Environment


def test_exec_auth_environment_inheritance(tmp_path):
    kubeconfig_content = {
        "current-context": "test-context",
        "contexts": [
            {
                "name": "test-context",
                "context": {"cluster": "test-cluster", "user": "test-user"},
            }
        ],
        "clusters": [
            {
                "name": "test-cluster",
                "cluster": {"server": "https://test-server"},
            }
        ],
        "users": [
            {
                "name": "test-user",
                "user": {
                    "exec": {
                        "command": "echo",
                        "args": ["{}"],
                    }
                },
            }
        ],
    }
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    mock_transport = MockTransport()
    test_env = {"TEST_VAR": "test_value", "PATH": "/test/path"}

    with (
        patch.dict(os.environ, test_env, clear=True),
        patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}),
        patch("cloudcoil.client._config.subprocess.run") as mock_run,
    ):
        # Setup mock subprocess.run
        mock_run.return_value.stdout = json.dumps(
            {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "status": {
                    "token": "test-exec-token",
                },
            }
        )
        mock_run.return_value.check = True

        config = Config()
        config.client._transport = mock_transport
        config.client.get("/")

        # Verify subprocess was called with inherited environment
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["TEST_VAR"] == "test_value"
        assert kwargs["env"]["PATH"] == "/test/path"


def test_exec_auth_environment_override(tmp_path):
    kubeconfig_content = {
        "current-context": "test-context",
        "contexts": [
            {
                "name": "test-context",
                "context": {"cluster": "test-cluster", "user": "test-user"},
            }
        ],
        "clusters": [
            {
                "name": "test-cluster",
                "cluster": {"server": "https://test-server"},
            }
        ],
        "users": [
            {
                "name": "test-user",
                "user": {
                    "exec": {
                        "command": "echo",
                        "args": ["{}"],
                        "env": [
                            {"name": "TEST_VAR", "value": "override_value"},
                            {"name": "NEW_VAR", "value": "new_value"},
                        ],
                    }
                },
            }
        ],
    }
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    mock_transport = MockTransport()
    test_env = {"TEST_VAR": "test_value", "PATH": "/test/path"}

    with (
        patch.dict(os.environ, test_env, clear=True),
        patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}),
        patch("cloudcoil.client._config.subprocess.run") as mock_run,
    ):
        # Setup mock subprocess.run
        mock_run.return_value.stdout = json.dumps(
            {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "status": {
                    "token": "test-exec-token",
                },
            }
        )
        mock_run.return_value.check = True

        config = Config()
        config.client._transport = mock_transport
        config.client.get("/")

        # Verify subprocess was called with correct environment
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["TEST_VAR"] == "override_value"  # Overridden value
        assert kwargs["env"]["NEW_VAR"] == "new_value"  # New variable
        assert kwargs["env"]["PATH"] == "/test/path"  # Inherited value


def test_exec_auth_token_in_headers(tmp_path):
    """Test that ExecAuthenticator adds the token correctly to request headers."""
    kubeconfig_content = {
        "current-context": "test-context",
        "contexts": [
            {
                "name": "test-context",
                "context": {"cluster": "test-cluster", "user": "test-user"},
            }
        ],
        "clusters": [
            {
                "name": "test-cluster",
                "cluster": {"server": "https://test-server"},
            }
        ],
        "users": [
            {
                "name": "test-user",
                "user": {
                    "exec": {
                        "command": "echo",
                        "args": ["{}"],
                    }
                },
            }
        ],
    }
    kubeconfig = tmp_path / "config"
    kubeconfig.write_text(yaml.dump(kubeconfig_content))

    class HeaderCapturingTransport(MockTransport):
        def __init__(self):
            self.captured_headers = None

        def handle_request(self, request):
            self.captured_headers = request.headers
            return Response(200)

    mock_transport = HeaderCapturingTransport()
    test_token = "test-exec-token-12345"

    with (
        patch.dict(os.environ, {"KUBECONFIG": str(kubeconfig)}),
        patch("cloudcoil.client._config.subprocess.run") as mock_run,
    ):
        # Setup mock subprocess.run
        mock_run.return_value.stdout = json.dumps(
            {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "status": {
                    "token": test_token,
                    "expirationTimestamp": "9999-12-31T23:59:59Z",
                },
            }
        )
        mock_run.return_value.check = True

        config = Config()
        config.client._transport = mock_transport

        # First request should get a new token
        config.client.get("/")
        assert mock_transport.captured_headers["Authorization"] == f"Bearer {test_token}"

        # Second request should use cached token
        mock_transport.captured_headers = None
        config.client.get("/")
        assert mock_transport.captured_headers["Authorization"] == f"Bearer {test_token}"
        assert mock_run.call_count == 1  # Token should be cached, no new exec call

        # Test token expiry
        mock_run.return_value.stdout = json.dumps(
            {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "status": {
                    "token": "new-token-after-expiry",
                    "expirationTimestamp": "2024-12-31T23:59:59Z",
                },
            }
        )

        # Simulate token expiry
        config.client.auth._token_expiry = 0
        config.client.get("/")
        assert mock_transport.captured_headers["Authorization"] == "Bearer new-token-after-expiry"
        assert mock_run.call_count == 2  # Should have made a new exec call
