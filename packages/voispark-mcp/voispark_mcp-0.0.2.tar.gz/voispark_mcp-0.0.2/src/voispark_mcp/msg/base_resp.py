from typing import Optional, Any, Dict, TypeVar, Generic
from pydantic import BaseModel, Field, model_validator

from voispark_mcp.core.error_code import ErrorCode

# Define a TypeVar for the data field. It must be a Pydantic BaseModel.
DataType = TypeVar("DataType", bound=BaseModel)


class BaseResponse(BaseModel, Generic[DataType]):
    """
    Base model for all API responses, generic over DataType.
    The `data` field can hold an instance of DataType or be None.

    Example usage for type hinting a response that includes a specific data model:
    `response_model=BaseResponse[YourDataModel]`
    """

    code: int
    message: str
    data: Optional[DataType] = None


class SuccessResponse(BaseResponse[DataType], Generic[DataType]):
    """
    Represents a successful API response, generic over DataType.
    The code and message are fixed to indicate success using defaults from ErrorCode.SUCCESS.
    The `data` field can be an instance of DataType or None.

    Usage:
        `SuccessResponse[MyDataModel](data=MyDataModel(...))`
        `SuccessResponse[MyDataModel]()` (data will be None)
        `SuccessResponse(data=MyDataModel(...))` (Pydantic may infer DataType if MyDataModel is provided)
    """

    code: int = Field(
        default=ErrorCode.SUCCESS.code,
        frozen=True,
        description="Status code for success.",
    )
    message: str = Field(
        default=ErrorCode.SUCCESS.message,
        frozen=True,
        description="Message for success.",
    )
    # data: Optional[DataType] = None is inherited and correctly typed.


class ErrorResponse(BaseResponse[DataType], Generic[DataType]):
    """
    Represents an error API response, generic over DataType.
    The `code` and `message` are automatically derived from the provided `error_type`.
    The `error_type` parameter during initialization MUST be an ErrorCode enum member.
    The `data` field can be an instance of DataType (e.g., for detailed error information) or None.

    Usage:
        `ErrorResponse[MyErrorDetailModel](error_type=ErrorCode.VALIDATION_ERROR, data=MyErrorDetailModel(...))`
        `ErrorResponse(error_type=ErrorCode.VALIDATION_ERROR)` (data will be None)
    """

    # Provide default values for code and message to satisfy linters regarding __init__ signature.
    # These are overridden by the model_validator based on error_type.
    code: int = ErrorCode.PLACEHOLDER.code
    message: str = ErrorCode.PLACEHOLDER.message

    # This field is used for initialization to define the error, but not included in the response model dump.
    error_type: ErrorCode = Field(
        exclude=True,
        description="The ErrorCode enum member defining this error. Used for initialization only.",
    )
    # data: Optional[DataType] = None is inherited and correctly typed.

    @model_validator(mode="before")
    @classmethod
    def _populate_code_message_from_error_type(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pydantic model validator (runs before field validation).
        Populates `code` and `message` fields based on the `error_type` provided in the input values.
        It also ensures that `error_type` is an instance of the ErrorCode enum.
        """
        error_type_instance = values.get("error_type")

        if not isinstance(error_type_instance, ErrorCode):
            raise ValueError(
                f"'error_type' must be an instance of ErrorCode. "
                f"Received type: {type(error_type_instance).__name__} for value: {error_type_instance!r}"
            )

        if not values.get("code"):
            values["code"] = error_type_instance.code

        if not values.get("message"):
            values["message"] = error_type_instance.message

        return values
