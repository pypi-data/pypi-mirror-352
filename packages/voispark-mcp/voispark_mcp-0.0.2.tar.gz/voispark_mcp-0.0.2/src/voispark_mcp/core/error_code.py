from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """
    Defines standard error codes and messages for API responses.
    Each enum member is a tuple of (numeric_code, "descriptive_message").
    """

    SUCCESS = (0, "Success")
    PLACEHOLDER = (-1, "Placeholder")
    COMMON_ERROR = (40000, "Common Error")
    API_TOKEN_ALREADY_EXISTS = (40001, "Api Token Already Exists")
    API_TOKEN_INVALID_NAME = (40002, "Api Token Invalid Name")
    UNAUTHORIZED = (40003, "Unauthorized")
    API_TOKEN_NOT_FOUND = (40004, "Api Token Not Found")

    @property
    def code(self) -> int:
        """The numeric error code."""
        return self.value[0]

    @property
    def message(self) -> str:
        """The descriptive error message."""
        return self.value[1]

    @classmethod
    def get_by_code(cls, code_value: int) -> "Optional[ErrorCode]":
        """
        Retrieves an ErrorCode member by its numeric code.

        Args:
            code_value: The numeric code to search for.

        Returns:
            The matching ErrorCode member, or None if not found.
        """
        for member in cls:
            if member.code == code_value:
                return member
        return None

    def __str__(self) -> str:
        return f"{self.name}(code={self.code}, message='{self.message}')"
