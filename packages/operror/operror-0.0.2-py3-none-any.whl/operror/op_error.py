from typing import Any, Dict, Type, TypeVar

from operror.op_status import Case, Code, Status


class OpError(Exception):
    """Represents an operation error.
    
    Args:
        status: The status of the operation that raised this error.
        module: The module where this error occured.
    """
    
    def __init__(self, status: Status, module: str = "none"):
        super().__init__(status)
        self._status = status
        self._module = module
    
    @property
    def status(self) -> Status:
        return self._status
    
    @property
    def module(self) -> str:
        return self._module
        
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(module={self.module}, status={self.status})"

    def add_more_ctx_to_msg(self, more_ctx: str) -> None:
        """Augments the message of the status with more contextual information."""
        self.status.add_more_ctx_to_msg(more_ctx)

E = TypeVar('E', bound=OpError) # generic type represents subclass of OpError

class ErrorBuilder:
    def __init__(self, status: Status):
        self._status = status
        self._module = "none"

    def with_module(self, module: str) -> 'ErrorBuilder':
        if not (module and module.strip()):
            return self
        self._module = module
        return self

    def with_message(self, msg: str) -> 'ErrorBuilder':
        self._status = self._status.with_msg(msg)
        return self

    def with_case(self, case: Case) -> 'ErrorBuilder':
        self._status = self._status.with_case(case)
        return self

    def with_details(self, details: Dict[str, Any] = {}) -> 'ErrorBuilder':
        self._status = self._status.with_details(details)
        return self

    def build(self, cls: Type[E]=OpError, *args: Any, **kwargs: Any) -> E:
        return cls(self._status, self._module, *args, **kwargs)


# Factory functions for creating ErrorBuilder instances
def new_from_status(status: Status) -> ErrorBuilder:
    """Creates a new ErrorBuilder with the given status."""
    return ErrorBuilder(status=status)

def new_op_cancelled() -> ErrorBuilder:
    """Creates a new ErrorBuilder for cancelled operation."""
    return ErrorBuilder(status=Status(Code.OP_CANCELLED))

def new_unknown_error() -> ErrorBuilder:
    """Creates a new ErrorBuilder for unknown error."""
    return ErrorBuilder(status=Status(Code.UNKNOWN_ERROR))

def new_illegal_input() -> ErrorBuilder:
    """Creates a new ErrorBuilder for illegal input."""
    return ErrorBuilder(status=Status(Code.ILLEGAL_INPUT))

def new_timeout() -> ErrorBuilder:
    """Creates a new ErrorBuilder for timeout."""
    return ErrorBuilder(status=Status(Code.TIMEOUT))

def new_not_found() -> ErrorBuilder:
    """Creates a new ErrorBuilder for not found."""
    return ErrorBuilder(status=Status(Code.NOT_FOUND))

def new_already_exists() -> ErrorBuilder:
    """Creates a new ErrorBuilder for already exists."""
    return ErrorBuilder(status=Status(Code.ALREADY_EXISTS))

def new_permission_denied() -> ErrorBuilder:
    """Creates a new ErrorBuilder for permission denied."""
    return ErrorBuilder(status=Status(Code.PERMISSION_DENIED))

def new_unauthenticated() -> ErrorBuilder:
    """Creates a new ErrorBuilder for unauthenticated."""
    return ErrorBuilder(status=Status(Code.UNAUTHENTICATED))

def new_resource_exhausted() -> ErrorBuilder:
    """Creates a new ErrorBuilder for resource exhausted."""
    return ErrorBuilder(status=Status(Code.RESOURCE_EXHAUSTED))

def new_failed_precondition() -> ErrorBuilder:
    """Creates a new ErrorBuilder for failed precondition."""
    return ErrorBuilder(status=Status(Code.FAILED_PRECONDITION))

def new_op_aborted() -> ErrorBuilder:
    """Creates a new ErrorBuilder for aborted."""
    return ErrorBuilder(status=Status(Code.OP_ABORTED))

def new_out_of_range() -> ErrorBuilder:
    """Creates a new ErrorBuilder for out of range."""
    return ErrorBuilder(status=Status(Code.OUT_OF_RANGE))

def new_unimplemented() -> ErrorBuilder:
    """Creates a new ErrorBuilder for unimplemented."""
    return ErrorBuilder(status=Status(Code.UNIMPLEMENTED))

def new_internal_error() -> ErrorBuilder:
    """Creates a new ErrorBuilder for internal error."""
    return ErrorBuilder(status=Status(Code.INTERNAL_ERROR))

def new_unavailable() -> ErrorBuilder:
    """Creates a new ErrorBuilder for unavailable."""
    return ErrorBuilder(status=Status(Code.UNAVAILABLE))

def new_data_corrupted() -> ErrorBuilder:
    """Creates a new ErrorBuilder for data corrupted."""
    return ErrorBuilder(status=Status(Code.DATA_CORRUPTED))

def new_authorization_expired() -> ErrorBuilder:
    """Creates a new ErrorBuilder for authorization expired."""
    return ErrorBuilder(status=Status(Code.AUTHORIZATION_EXPIRED)) 

def new_from_http_resp(status_code: int, headers: Any = None, body: str = "") -> ErrorBuilder:
    """Creates a new ErrorBuilder from an HTTP response."""
    return ErrorBuilder(status=Status.new_from_http_resp(status_code, headers, body))