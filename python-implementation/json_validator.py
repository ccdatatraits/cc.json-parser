"""
JSON Schema Validator - Advanced validation beyond basic JSON syntax.

This module provides validation against JSON schemas and common validation
patterns for real-world JSON data.
"""

from typing import Any, Dict, List, Union, Optional, Callable
import re
import logging
from datetime import datetime
from parser import parse_json

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for JSON validation errors."""
    
    def __init__(self, message: str, path: str = "", value: Any = None):
        self.message = message
        self.path = path
        self.value = value
        super().__init__(f"Validation error at '{path}': {message}")


class JSONValidator:
    """
    Advanced JSON validator with schema support and custom validation rules.
    
    Features:
    - JSON Schema-like validation
    - Custom validation functions
    - Type checking with coercion
    - Pattern matching for strings
    - Range validation for numbers
    - Array and object validation
    """
    
    def __init__(self):
        self.custom_validators: Dict[str, Callable] = {}
        self.register_built_in_validators()
        
    def register_built_in_validators(self):
        """Register built-in validation functions."""
        self.custom_validators.update({
            'email': self._validate_email,
            'url': self._validate_url,
            'date': self._validate_date,
            'uuid': self._validate_uuid,
            'ipv4': self._validate_ipv4,
            'ipv6': self._validate_ipv6,
        })
        
    def register_validator(self, name: str, validator_func: Callable[[Any], bool]):
        """
        Register a custom validator function.
        
        Args:
            name: Name of the validator
            validator_func: Function that takes a value and returns bool
        """
        self.custom_validators[name] = validator_func
        
    def validate(self, data: Any, schema: Dict[str, Any], path: str = "$") -> List[ValidationError]:
        """
        Validate data against a schema.
        
        Args:
            data: Data to validate
            schema: Validation schema
            path: Current path in the data structure
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            # Type validation
            if 'type' in schema:
                type_errors = self._validate_type(data, schema['type'], path)
                errors.extend(type_errors)
                
            # Required fields (for objects)
            if isinstance(data, dict) and 'required' in schema:
                required_errors = self._validate_required(data, schema['required'], path)
                errors.extend(required_errors)
                
            # Properties validation (for objects)
            if isinstance(data, dict) and 'properties' in schema:
                prop_errors = self._validate_properties(data, schema['properties'], path)
                errors.extend(prop_errors)
                
            # Array items validation
            if isinstance(data, list) and 'items' in schema:
                item_errors = self._validate_array_items(data, schema['items'], path)
                errors.extend(item_errors)
                
            # String pattern validation
            if isinstance(data, str) and 'pattern' in schema:
                pattern_errors = self._validate_pattern(data, schema['pattern'], path)
                errors.extend(pattern_errors)
                
            # Numeric range validation
            if isinstance(data, (int, float)):
                range_errors = self._validate_numeric_range(data, schema, path)
                errors.extend(range_errors)
                
            # Custom format validation
            if 'format' in schema:
                format_errors = self._validate_format(data, schema['format'], path)
                errors.extend(format_errors)
                
            # Enum validation
            if 'enum' in schema:
                enum_errors = self._validate_enum(data, schema['enum'], path)
                errors.extend(enum_errors)
                
        except Exception as e:
            errors.append(ValidationError(f"Validation error: {str(e)}", path, data))\n            \n        return errors\n        \n    def _validate_type(self, data: Any, expected_type: Union[str, List[str]], path: str) -> List[ValidationError]:\n        \"\"\"Validate data type.\"\"\"\n        errors = []\n        \n        if isinstance(expected_type, list):\n            # Multiple types allowed\n            valid = any(self._check_type(data, t) for t in expected_type)\n            if not valid:\n                errors.append(ValidationError(\n                    f\"Expected one of {expected_type}, got {type(data).__name__}\",\n                    path, data\n                ))\n        else:\n            # Single type\n            if not self._check_type(data, expected_type):\n                errors.append(ValidationError(\n                    f\"Expected {expected_type}, got {type(data).__name__}\",\n                    path, data\n                ))\n                \n        return errors\n        \n    def _check_type(self, data: Any, expected_type: str) -> bool:\n        \"\"\"Check if data matches expected type.\"\"\"\n        type_mapping = {\n            'string': str,\n            'number': (int, float),\n            'integer': int,\n            'boolean': bool,\n            'array': list,\n            'object': dict,\n            'null': type(None)\n        }\n        \n        expected_python_type = type_mapping.get(expected_type)\n        if expected_python_type is None:\n            return False\n            \n        return isinstance(data, expected_python_type)\n        \n    def _validate_required(self, data: Dict[str, Any], required: List[str], path: str) -> List[ValidationError]:\n        \"\"\"Validate required fields in object.\"\"\"\n        errors = []\n        \n        for field in required:\n            if field not in data:\n                errors.append(ValidationError(\n                    f\"Required field '{field}' is missing\",\n                    f\"{path}.{field}\"\n                ))\n                \n        return errors\n        \n    def _validate_properties(self, data: Dict[str, Any], properties: Dict[str, Any], path: str) -> List[ValidationError]:\n        \"\"\"Validate object properties.\"\"\"\n        errors = []\n        \n        for prop_name, prop_schema in properties.items():\n            if prop_name in data:\n                prop_path = f\"{path}.{prop_name}\"\n                prop_errors = self.validate(data[prop_name], prop_schema, prop_path)\n                errors.extend(prop_errors)\n                \n        return errors\n        \n    def _validate_array_items(self, data: List[Any], items_schema: Dict[str, Any], path: str) -> List[ValidationError]:\n        \"\"\"Validate array items.\"\"\"\n        errors = []\n        \n        for i, item in enumerate(data):\n            item_path = f\"{path}[{i}]\"\n            item_errors = self.validate(item, items_schema, item_path)\n            errors.extend(item_errors)\n            \n        return errors\n        \n    def _validate_pattern(self, data: str, pattern: str, path: str) -> List[ValidationError]:\n        \"\"\"Validate string pattern.\"\"\"\n        errors = []\n        \n        try:\n            if not re.match(pattern, data):\n                errors.append(ValidationError(\n                    f\"String does not match pattern '{pattern}'\",\n                    path, data\n                ))\n        except re.error as e:\n            errors.append(ValidationError(\n                f\"Invalid regex pattern '{pattern}': {e}\",\n                path\n            ))\n            \n        return errors\n        \n    def _validate_numeric_range(self, data: Union[int, float], schema: Dict[str, Any], path: str) -> List[ValidationError]:\n        \"\"\"Validate numeric ranges.\"\"\"\n        errors = []\n        \n        if 'minimum' in schema and data < schema['minimum']:\n            errors.append(ValidationError(\n                f\"Value {data} is less than minimum {schema['minimum']}\",\n                path, data\n            ))\n            \n        if 'maximum' in schema and data > schema['maximum']:\n            errors.append(ValidationError(\n                f\"Value {data} is greater than maximum {schema['maximum']}\",\n                path, data\n            ))\n            \n        if 'exclusiveMinimum' in schema and data <= schema['exclusiveMinimum']:\n            errors.append(ValidationError(\n                f\"Value {data} is not greater than exclusive minimum {schema['exclusiveMinimum']}\",\n                path, data\n            ))\n            \n        if 'exclusiveMaximum' in schema and data >= schema['exclusiveMaximum']:\n            errors.append(ValidationError(\n                f\"Value {data} is not less than exclusive maximum {schema['exclusiveMaximum']}\",\n                path, data\n            ))\n            \n        return errors\n        \n    def _validate_format(self, data: Any, format_name: str, path: str) -> List[ValidationError]:\n        \"\"\"Validate custom formats.\"\"\"\n        errors = []\n        \n        if format_name in self.custom_validators:\n            validator = self.custom_validators[format_name]\n            try:\n                if not validator(data):\n                    errors.append(ValidationError(\n                        f\"Value does not match format '{format_name}'\",\n                        path, data\n                    ))\n            except Exception as e:\n                errors.append(ValidationError(\n                    f\"Format validation error for '{format_name}': {e}\",\n                    path, data\n                ))\n        else:\n            logger.warning(f\"Unknown format '{format_name}' - skipping validation\")\n            \n        return errors\n        \n    def _validate_enum(self, data: Any, enum_values: List[Any], path: str) -> List[ValidationError]:\n        \"\"\"Validate enum values.\"\"\"\n        errors = []\n        \n        if data not in enum_values:\n            errors.append(ValidationError(\n                f\"Value must be one of {enum_values}\",\n                path, data\n            ))\n            \n        return errors\n        \n    # Built-in format validators\n    def _validate_email(self, value: Any) -> bool:\n        \"\"\"Validate email format.\"\"\"\n        if not isinstance(value, str):\n            return False\n        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n        return bool(re.match(email_pattern, value))\n        \n    def _validate_url(self, value: Any) -> bool:\n        \"\"\"Validate URL format.\"\"\"\n        if not isinstance(value, str):\n            return False\n        url_pattern = r'^https?://[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(?:/.*)?$'\n        return bool(re.match(url_pattern, value))\n        \n    def _validate_date(self, value: Any) -> bool:\n        \"\"\"Validate ISO date format.\"\"\"\n        if not isinstance(value, str):\n            return False\n        try:\n            datetime.fromisoformat(value.replace('Z', '+00:00'))\n            return True\n        except ValueError:\n            return False\n            \n    def _validate_uuid(self, value: Any) -> bool:\n        \"\"\"Validate UUID format.\"\"\"\n        if not isinstance(value, str):\n            return False\n        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'\n        return bool(re.match(uuid_pattern, value.lower()))\n        \n    def _validate_ipv4(self, value: Any) -> bool:\n        \"\"\"Validate IPv4 address.\"\"\"\n        if not isinstance(value, str):\n            return False\n        parts = value.split('.')\n        if len(parts) != 4:\n            return False\n        try:\n            return all(0 <= int(part) <= 255 for part in parts)\n        except ValueError:\n            return False\n            \n    def _validate_ipv6(self, value: Any) -> bool:\n        \"\"\"Validate IPv6 address (simplified).\"\"\"\n        if not isinstance(value, str):\n            return False\n        ipv6_pattern = r'^[0-9a-f]{0,4}(?::[0-9a-f]{0,4}){0,7}$'\n        return bool(re.match(ipv6_pattern, value.lower()))\n\n\ndef validate_json_with_schema(json_text: str, schema: Dict[str, Any]) -> tuple[bool, List[str]]:\n    \"\"\"\n    Convenience function to validate JSON against a schema.\n    \n    Args:\n        json_text: JSON string to validate\n        schema: Validation schema\n        \n    Returns:\n        Tuple of (is_valid, list_of_error_messages)\n    \"\"\"\n    try:\n        # First parse the JSON\n        data = parse_json(json_text)\n        \n        # Then validate against schema\n        validator = JSONValidator()\n        errors = validator.validate(data, schema)\n        \n        error_messages = [str(error) for error in errors]\n        return len(errors) == 0, error_messages\n        \n    except Exception as e:\n        return False, [f\"JSON parsing failed: {str(e)}\"]\n\n\n# Common schema templates\nCOMMON_SCHEMAS = {\n    'user': {\n        'type': 'object',\n        'required': ['id', 'name', 'email'],\n        'properties': {\n            'id': {'type': 'integer', 'minimum': 1},\n            'name': {'type': 'string', 'pattern': r'^[A-Za-z\\s]+$'},\n            'email': {'type': 'string', 'format': 'email'},\n            'age': {'type': 'integer', 'minimum': 0, 'maximum': 150},\n            'active': {'type': 'boolean'}\n        }\n    },\n    \n    'product': {\n        'type': 'object',\n        'required': ['id', 'name', 'price'],\n        'properties': {\n            'id': {'type': 'string', 'format': 'uuid'},\n            'name': {'type': 'string'},\n            'price': {'type': 'number', 'minimum': 0},\n            'category': {'type': 'string', 'enum': ['electronics', 'clothing', 'books', 'other']},\n            'inStock': {'type': 'boolean'}\n        }\n    }\n}"