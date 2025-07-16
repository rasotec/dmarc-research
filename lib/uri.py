from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto

# https://docs.python.org/3/library/contextvars.html

class UriParseErrorType(Enum):
    """Enumeration for specific parsing error types."""
    INVALID_SCHEME = auto()
    INVALID_PAYLOAD_UNIT = auto()
    INVALID_PAYLOAD_SIZE = auto()
    INVALID_PAYLOAD = auto()
    EMPTY_EMAIL = auto()

@dataclass
class ParsedUri:
    """
    Represents the parsed data from a mailto URI, including potential errors.

    Attributes:
        email: The parsed email address. None if parsing fails.
        payload: The parsed payload string. None if not present or if parsing fails.
        error_type: The type of error encountered, if any.
        error_description: A human-readable description of the error.
    """
    email: Optional[str] = None
    payload: Optional[str] = None
    error_type: Optional[UriParseErrorType] = None
    error_description: Optional[str] = None


def parse_uri(uri: str) -> ParsedUri:
    """
    Parses a mailto URI with an optional payload, capturing errors.

    Args:
        uri: The mailto URI string to parse.

    Returns:
        A ParsedUri object containing the parsed data or error details.
    """
    if not uri.startswith('mailto:'):
        return ParsedUri(
            error_type=UriParseErrorType.INVALID_SCHEME,
            error_description="URI scheme is not 'mailto:'."
        )

    uri_body = uri.removeprefix('mailto:')

    if '!' in uri_body:
        email, payload_str = uri_body.split('!', 1)
        email = email.strip()
        if not email:
            return ParsedUri(
                error_type=UriParseErrorType.EMPTY_EMAIL,
                error_description="Email address cannot be empty."
            )
        payload_str = payload_str.strip()

        if '!' in payload_str:
            return ParsedUri(
                error_type=UriParseErrorType.INVALID_PAYLOAD,
                error_description="Invalid payload. Must not contain '!' character."
            )

        # Validate payload
        if not payload_str or not payload_str[:-1].isdigit():
            return ParsedUri(
                error_type=UriParseErrorType.INVALID_PAYLOAD_SIZE,
                error_description=f"Invalid payload size in '{payload_str}'. Must be numeric."
            )

        unit = payload_str[-1].lower()
        if unit not in ['k', 'm', 'g', 't']:
            return ParsedUri(
                error_type=UriParseErrorType.INVALID_PAYLOAD_UNIT,
                error_description=f"Invalid payload unit '{unit}'. Must be one of 'k', 'm', 'g', 't'."
            )

        payload = f"{int(payload_str[:-1])}{unit}"
    else:
        email, payload = uri_body.strip(), None

    if not email:
        return ParsedUri(
            error_type=UriParseErrorType.EMPTY_EMAIL,
            error_description="Email address cannot be empty."
        )

    return ParsedUri(email=email, payload=payload)


def parse_domain(email: str) -> Optional[str]:
    if '@' in email:
        _, domain = email.split('@', 1)
        if '.' in domain:
            return domain
        else:
            return None
    else:
        return None