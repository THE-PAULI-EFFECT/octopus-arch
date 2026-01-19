"""
Custom exceptions for Octopus Architecture API
"""

from fastapi import status


class OctopusException(Exception):
    """Base exception for Octopus Architecture"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class ProviderNotFoundException(OctopusException):
    """Provider not found"""

    def __init__(self, provider_id: str):
        super().__init__(
            message=f"Provider {provider_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TrustScoreTooLowException(OctopusException):
    """Trust score below minimum threshold"""

    def __init__(self, score: int, minimum: int):
        super().__init__(
            message=f"Trust score {score} is below minimum {minimum}",
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider requires manual review or verification",
        )


class LeadAttributionException(OctopusException):
    """Lead attribution error"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class RateLimitExceededException(OctopusException):
    """Rate limit exceeded"""

    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class UnauthorizedException(OctopusException):
    """Unauthorized access"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidSignatureException(OctopusException):
    """Invalid signature for signed URL"""

    def __init__(self):
        super().__init__(
            message="Invalid or expired signature",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ContributionRequiredException(OctopusException):
    """Social contribution not met"""

    def __init__(self, hours_remaining: int):
        super().__init__(
            message=f"Social contribution requirement not met. {hours_remaining} hours remaining.",
            status_code=status.HTTP_403_FORBIDDEN,
            detail="All members must contribute to local projects",
        )
