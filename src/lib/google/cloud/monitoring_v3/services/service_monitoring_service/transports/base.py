# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import abc
from typing import Awaitable, Callable, Dict, Optional, Sequence, Union

from google.cloud.monitoring_v3 import gapic_version as package_version

import google.auth  # type: ignore
import google.api_core
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import retry as retries
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.cloud.monitoring_v3.types import service
from google.cloud.monitoring_v3.types import service as gm_service
from google.cloud.monitoring_v3.types import service_service
from google.protobuf import empty_pb2  # type: ignore

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=package_version.__version__
)


class ServiceMonitoringServiceTransport(abc.ABC):
    """Abstract transport class for ServiceMonitoringService."""

    AUTH_SCOPES = (
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/monitoring",
        "https://www.googleapis.com/auth/monitoring.read",
    )

    DEFAULT_HOST: str = "monitoring.googleapis.com"

    def __init__(
        self,
        *,
        host: str = DEFAULT_HOST,
        credentials: Optional[ga_credentials.Credentials] = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        api_audience: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
        """

        scopes_kwargs = {"scopes": scopes, "default_scopes": self.AUTH_SCOPES}

        # Save the scopes.
        self._scopes = scopes

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise core_exceptions.DuplicateCredentialArgs(
                "'credentials_file' and 'credentials' are mutually exclusive"
            )

        if credentials_file is not None:
            credentials, _ = google.auth.load_credentials_from_file(
                credentials_file, **scopes_kwargs, quota_project_id=quota_project_id
            )
        elif credentials is None:
            credentials, _ = google.auth.default(
                **scopes_kwargs, quota_project_id=quota_project_id
            )
            # Don't apply audience if the credentials file passed from user.
            if hasattr(credentials, "with_gdch_audience"):
                credentials = credentials.with_gdch_audience(
                    api_audience if api_audience else host
                )

        # If the credentials are service account credentials, then always try to use self signed JWT.
        if (
            always_use_jwt_access
            and isinstance(credentials, service_account.Credentials)
            and hasattr(service_account.Credentials, "with_always_use_jwt_access")
        ):
            credentials = credentials.with_always_use_jwt_access(True)

        # Save the credentials.
        self._credentials = credentials

        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_service: gapic_v1.method.wrap_method(
                self.create_service,
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.get_service: gapic_v1.method.wrap_method(
                self.get_service,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.list_services: gapic_v1.method.wrap_method(
                self.list_services,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.update_service: gapic_v1.method.wrap_method(
                self.update_service,
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.delete_service: gapic_v1.method.wrap_method(
                self.delete_service,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.create_service_level_objective: gapic_v1.method.wrap_method(
                self.create_service_level_objective,
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.get_service_level_objective: gapic_v1.method.wrap_method(
                self.get_service_level_objective,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.list_service_level_objectives: gapic_v1.method.wrap_method(
                self.list_service_level_objectives,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.update_service_level_objective: gapic_v1.method.wrap_method(
                self.update_service_level_objective,
                default_timeout=30.0,
                client_info=client_info,
            ),
            self.delete_service_level_objective: gapic_v1.method.wrap_method(
                self.delete_service_level_objective,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=30.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=30.0,
                ),
                default_timeout=30.0,
                client_info=client_info,
            ),
        }

    def close(self):
        """Closes resources associated with the transport.

        .. warning::
             Only call this method if the transport is NOT shared
             with other clients - this may cause errors in other clients!
        """
        raise NotImplementedError()

    @property
    def create_service(
        self,
    ) -> Callable[
        [service_service.CreateServiceRequest],
        Union[gm_service.Service, Awaitable[gm_service.Service]],
    ]:
        raise NotImplementedError()

    @property
    def get_service(
        self,
    ) -> Callable[
        [service_service.GetServiceRequest],
        Union[service.Service, Awaitable[service.Service]],
    ]:
        raise NotImplementedError()

    @property
    def list_services(
        self,
    ) -> Callable[
        [service_service.ListServicesRequest],
        Union[
            service_service.ListServicesResponse,
            Awaitable[service_service.ListServicesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_service(
        self,
    ) -> Callable[
        [service_service.UpdateServiceRequest],
        Union[gm_service.Service, Awaitable[gm_service.Service]],
    ]:
        raise NotImplementedError()

    @property
    def delete_service(
        self,
    ) -> Callable[
        [service_service.DeleteServiceRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def create_service_level_objective(
        self,
    ) -> Callable[
        [service_service.CreateServiceLevelObjectiveRequest],
        Union[service.ServiceLevelObjective, Awaitable[service.ServiceLevelObjective]],
    ]:
        raise NotImplementedError()

    @property
    def get_service_level_objective(
        self,
    ) -> Callable[
        [service_service.GetServiceLevelObjectiveRequest],
        Union[service.ServiceLevelObjective, Awaitable[service.ServiceLevelObjective]],
    ]:
        raise NotImplementedError()

    @property
    def list_service_level_objectives(
        self,
    ) -> Callable[
        [service_service.ListServiceLevelObjectivesRequest],
        Union[
            service_service.ListServiceLevelObjectivesResponse,
            Awaitable[service_service.ListServiceLevelObjectivesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_service_level_objective(
        self,
    ) -> Callable[
        [service_service.UpdateServiceLevelObjectiveRequest],
        Union[service.ServiceLevelObjective, Awaitable[service.ServiceLevelObjective]],
    ]:
        raise NotImplementedError()

    @property
    def delete_service_level_objective(
        self,
    ) -> Callable[
        [service_service.DeleteServiceLevelObjectiveRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def kind(self) -> str:
        raise NotImplementedError()


__all__ = ("ServiceMonitoringServiceTransport",)