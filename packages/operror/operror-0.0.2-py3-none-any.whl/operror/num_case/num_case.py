from operror.op_status import Case, Code


class NumCase(Case):
    """A case represented by a numeric code.
    
    The identifier format is: {app_code}_{module_code}_{case_code}
    For example: 1_1_1000
    
    Attributes:
        app_code (int): Application code
        module_code (int): Module code
        case_code (int): Case code
        identifier (str): The full identifier string
        op_status_code (Code): The operation status code in which this specific error case belongs.
    """
    
    def __init__(self, app_code: int, module_code: int, case_code: int, 
                 identifier: str, op_status_code: Code) -> None:
        """Initialize a new NumCase.
        
        Args:
            app_code: Application code
            module_code: Module code
            case_code: Case code
            identifier: The full identifier string
            op_status_code: The operation status code in which this specific error case belongs.
        """
        self._app_code = app_code
        self._module_code = module_code
        self._case_code = case_code
        self._identifier = identifier
        self._op_status_code = op_status_code
    
    @property
    def identifier(self) -> str:
        """Get the case identifier.
        
        Returns:
            The full identifier string
        """
        return self._identifier
    
    def op_status_code(self) -> Code:
        """Get the operation status code.
        
        Returns:
            The operation status code
        """
        return self._op_status_code
    
    def __str__(self) -> str:
        return f"{self._identifier}"
    
    def __eq__(self, other: object) -> bool:
        """Check if this case is equal to another case.
        
        Args:
            other: The other case to compare with
            
        Returns:
            True if the cases are equal, False otherwise
        """
        if not isinstance(other, NumCase):
            return False
        return (self._identifier == other._identifier and 
                self._op_status_code == other._op_status_code)