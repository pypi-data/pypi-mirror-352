import base64
import io
import json
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Union, get_args, get_origin


class FluxJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder designed for the Flux project.

    This encoder extends the functionality of the default JSONEncoder to handle various data types commonly used
    within the Flux project, ensuring consistent and reliable JSON serialization.

    Supported data types:
    - Simple types: str, datetime, date, Decimal, Enum, bytes, io.IOBase
    - Custom classes with fields of the above simple types
    - Lists of objects, including nested lists
    - Dictionaries with values of the above supported types
    - Optional types, ensuring that optional values are correctly encoded

    Note: This encoder is designed to maintain encoding consistency across the Rippling main application and the Lambda
    function hosting third-party code.

    Usage Example:
    ```
    import json
    from apps.flux_runtime.app_implementation.serialization import FluxJSONEncoder

    encoded_data = json.dumps(data, cls=FluxJSONEncoder)
    ```

    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, bytes):
            return self._encode_bytes(obj)
        if isinstance(obj, io.IOBase):
            return self._encode_io_base(obj)
        if isinstance(obj, list):
            return [self.default(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self.default(value) for key, value in obj.items()}
        if hasattr(obj, "__dict__"):
            serialized_dict = {"target_type": repr(type(obj))}
            for key, value in obj.__dict__.items():
                serialized_dict[key] = json.dumps(value, cls=FluxJSONEncoder)
            return serialized_dict
        return super().default(obj)

    def _encode_bytes(self, obj):
        if hasattr(obj, "read") and callable(obj.read):
            # If it's an IOBase object, read it and encode as bytes
            return base64.b85encode(obj.read()).decode("utf-8")
        else:
            # Encode bytes directly
            return base64.b85encode(obj).decode("utf-8")

    def _encode_io_base(self, obj):
        if isinstance(obj, io.BytesIO):
            content = obj.getvalue()
            encoding = "bytes"
        elif isinstance(obj, io.StringIO):
            content = obj.getvalue().encode("utf-8")
            encoding = "utf-8"
        else:
            raise TypeError("Unsupported IOBase type")

        encoded_content = base64.b85encode(content)
        return {
            "encoding": encoding,
            "content": encoded_content.decode("utf-8"),
        }


class FluxJSONDecoder(json.JSONDecoder):
    """
    Custom JSON decoder designed for the Flux project.

    This decoder extends the functionality of the default JSONDecoder to handle decoding of JSON strings generated
    using the FluxJSONEncoder, ensuring consistent and reliable JSON deserialization.

    Supported data types:
    - Simple types: str, datetime, date, Decimal, Enum, bytes, io.IOBase
    - Custom classes with fields of the above simple types
    - Lists of objects, including nested lists
    - Dictionaries with values of the above supported types
    - Optional types, ensuring that optional values are correctly decoded

    Note: This decoder is designed to maintain decoding consistency across the Rippling main application and the Lambda
    function hosting third-party code.

    Usage Example:
    ```
    import json
    from apps.flux_runtime.app_implementation.serialization import FluxJSONDecoder

    encoded_data = "..."  # Your encoded JSON data
    decoded_data = json.loads(encoded_data, cls=FluxJSONDecoder, target_type=YourClass)
    ```

    """

    def __init__(self, target_type=None, **kwargs):
        self.target_type = target_type
        super().__init__(**kwargs)

    def decode(self, s, *args, **kwargs):
        obj = super().decode(s, *args, **kwargs)
        return self._convert_object(obj, self.target_type)

    def _convert_object(self, obj, target_type):
        passed_in_target_type = obj.pop("target_type", None) if isinstance(obj, dict) else None
        if get_origin(target_type) is Union:
            for union_type in get_args(target_type):
                if repr(union_type) == passed_in_target_type:
                    target_type = union_type
                    break
        if get_origin(target_type) is Union:
            target_type = type(obj)
        if get_origin(target_type) is list:
            target_type = get_args(target_type)[0]
        if get_origin(target_type) is tuple and obj is not None:
            return tuple(self._convert_object(item, get_args(target_type)[i]) for i, item in enumerate(obj))
        if isinstance(obj, list):
            return [self._convert_object(item, target_type) for item in obj]

        if target_type is not None:
            if obj is None or type(obj) is target_type:
                return obj
            elif target_type is Decimal:
                return Decimal(obj)
            elif target_type is datetime:
                return datetime.fromisoformat(obj)
            elif target_type is date:
                return date.fromisoformat(obj)
            elif target_type is bytes:
                return base64.b85decode(obj)
            elif target_type is io.IOBase:
                return self._decode_io_base(obj)
            elif issubclass(target_type, Enum):
                return target_type(obj)
            elif target_type is float:
                return float(obj)
            elif target_type is int:
                return int(obj)
            elif target_type is str:
                return str(obj)
            elif target_type is dict or get_origin(target_type) is dict:
                deserialized_dict = {}
                for key, value in obj.items():
                    value_target_type = None
                    if (
                        hasattr(target_type, "__args__")
                        and len(target_type.__args__) == 2
                        and target_type.__args__[1] is not Any
                    ):
                        value_target_type = target_type.__args__[1]
                    deserialized_dict[key] = self._convert_object(value, target_type=value_target_type)
                return deserialized_dict
            else:
                if not obj:
                    return target_type()
                deserialized_dict = {}
                for key, value in obj.items():
                    if key in target_type.__annotations__:
                        expected_type = target_type.__annotations__[key]
                        if self.is_optional_type(expected_type):
                            expected_type = expected_type.__args__[0]
                        deserialized_dict[key] = json.loads(value, cls=FluxJSONDecoder, target_type=expected_type)
                if is_dataclass(target_type):
                    return target_type(**deserialized_dict)
                instance = target_type()
                for key, value in target_type.__annotations__.items():
                    setattr(instance, key, deserialized_dict.get(key, None))
                return instance

        if isinstance(obj, str):
            try:
                return datetime.fromisoformat(obj)
            except ValueError:
                pass

        if isinstance(obj, dict):
            return {key: self._convert_object(value, target_type) for key, value in obj.items()}

        return obj

    def is_optional_type(self, typ):
        return get_origin(typ) is Union and type(None) in get_args(typ)

    def _decode_io_base(self, obj):
        encoding = obj["encoding"]
        content = base64.b85decode(obj["content"])

        try:
            if encoding == "bytes":
                return io.BytesIO(content)
            elif encoding == "utf-8":
                return io.StringIO(content.decode("utf-8"))
            else:
                raise TypeError(f"Unsupported encoding type {encoding}")
        except (ImportError, AttributeError):
            raise ValueError("Invalid IOBase type during decoding")