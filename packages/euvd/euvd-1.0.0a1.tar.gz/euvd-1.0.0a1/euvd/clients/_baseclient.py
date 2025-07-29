"""
Base HTTP client for the EUVD API.
"""

from typing import Any
import datetime
import math

from euvd.models import EnisaVulnerability
from euvd.exceptions import (
    EUVDException,
    EUVDNotFoundException,
)


class _BaseClient:
    def _parse_vulnerabilities(self, vulnerabilities) -> list[EnisaVulnerability]:
        parsed_vulnerabilities: list[EnisaVulnerability] = list(
            map(
                EnisaVulnerability.from_dict,
                vulnerabilities,
            )
        )

        return parsed_vulnerabilities

    def _prepare_get_latest_vulnerabilities_request(self) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/lastvulnerabilities',
        }

        return request_args

    def _handle_get_latest_vulnerabilities_request_errors(self, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to retrieve latest vulnerabilities: {response.status_code} {response.reason_phrase}",
            )

    def _prepare_get_latest_exploited_vulnerabilities_request(self) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/exploitedvulnerabilities',
        }

        return request_args

    def _handle_get_latest_exploited_vulnerabilities_request_errors(self, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to retrieve latest exploited vulnerabilities: {response.status_code} {response.reason_phrase}",
            )

    def _prepare_get_latest_critical_vulnerabilities_request(self) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/criticalvulnerabilities',
        }

        return request_args

    def _handle_get_latest_critical_vulnerabilities_response_errors(self, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to retrieve latest critical vulnerabilities: {response.status_code} {response.reason_phrase}",
            )

    def _prepare_search_vulnerabilities_request(
        self,
        from_score: float | None = None,
        to_score: float | None = None,
        from_epss: float | None = None,
        to_epss: float | None = None,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
        product: str | None = None,
        vendor: str | None = None,
        assigner: str | None = None,
        exploited: bool | None = None,
        text: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        if from_score is not None and to_score is not None and from_score > to_score:
            raise ValueError("from_score cannot be greater than to_score")
        if from_epss is not None and to_epss is not None and from_epss > to_epss:
            raise ValueError("from_epss cannot be greater than to_epss")
        if from_date is not None and to_date is not None and from_date > to_date:
            raise ValueError("from_date cannot be greater than to_date")
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")
        if page_size < 1:
            raise ValueError("page_size must be greater than or equal to 1")
        if page_size > 100:
            raise ValueError("page_size must be lower than or equal to 100")
        request_params: dict[str, Any] = {}
        if from_score is not None:
            if from_score < 0 or from_score > 10:
                raise ValueError("from_score must be between 0 and 10")
            request_params['fromScore'] = from_score
        if to_score is not None:
            if to_score < 0 or to_score > 10:
                raise ValueError("to_score must be between 0 and 10")
            request_params['toScore'] = to_score
        if from_epss is not None:
            if from_epss < 0.0 or from_epss > 100.0:
                raise ValueError("from_epss must be between 0.0 and 100.0")
            request_params['fromEpss'] = int(math.floor(from_epss))
        if to_epss is not None:
            if to_epss < 0.0 or to_epss > 100.0:
                raise ValueError("to_epss must be between 0.0 and 100.0")
            request_params['toEpss'] = int(math.ceil(to_epss))
        if from_date is not None:
            request_params['fromDate'] = from_date.isoformat()
        if to_date is not None:
            request_params['toDate'] = to_date.isoformat()
        if product is not None:
            request_params['product'] = product
        if vendor is not None:
            request_params['vendor'] = vendor
        if assigner is not None:
            request_params['assigner'] = assigner
        if exploited is not None:
            request_params['exploited'] = str(exploited).lower()
        if text is not None:
            request_params['text'] = text
        request_params['page'] = page - 1  # Convert to zero-based index
        request_params['size'] = page_size
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/search',
            'params': request_params,
        }

        return request_args

    def _handle_search_vulnerabilities_response_errors(self, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to find vulnerabilities: {response.status_code} {response.reason_phrase}",
            )

    def _prepare_get_vulnerability_request(self, vulnerability_id) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/enisaid',
            'params': {
                'id': vulnerability_id,
            },
        }

        return request_args

    def _handle_get_vulnerability_response_errors(self, vulnerability_id, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to retrieve vulnerability: {response.status_code} {response.reason_phrase}",
            )
        else:
            if response.status_code in (404, 204):
                raise EUVDNotFoundException(
                    f"Vulnerability with ID {vulnerability_id} not found.",
                )

    def _prepare_get_advisory_request(self, advisory_id) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            'method': 'GET',
            'url': '/advisory',
            'params': {
                'id': advisory_id,
            },
        }

        return request_args

    def _handle_get_advisory_response_errors(self, advisory_id, response):
        if not response.is_success:
            raise EUVDException(
                f"Failed to retrieve advisory: {response.status_code} {response.reason_phrase}",
            )
        else:
            if response.status_code in (404, 204):
                raise EUVDNotFoundException(
                    f"Advisory with ID {advisory_id} not found.",
                )


__all__ = [
    '_BaseClient',
]
