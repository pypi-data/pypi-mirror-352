import importlib
import json
from functools import reduce

from .serialization import FluxJSONEncoder, FluxJSONDecoder


def invoke(event):
    hook = event['hook']
    hook_params = event['hook_params']
    app_implementation_type = event['app_implementation_type']
    app_name = event['app_name']
    kit_name = event['kit_name']
    capability_snake_case = convert_to_snakecase(app_implementation_type)
    kit_snake_case = convert_to_snakecase(kit_name)

    module_path = ".".join(
        [
            "app",
            kit_snake_case,
            "capabilities",
            capability_snake_case,
            "implementation",
        ]
    )

    module = importlib.import_module(module_path)

    module_cls = app_implementation_type + "Impl"

    if module and hasattr(module, module_cls):
        app_class = getattr(module, module_cls)
        hook_method = getattr(app_class, hook)

        import inspect
        method_signature = inspect.signature(hook_method)

        parameters = ()
        for parameter_name, parameter in method_signature.parameters.items():
            parameters += (json.loads(hook_params[parameter_name], cls=FluxJSONDecoder, target_type=parameter.annotation),)

    return json.dumps(hook_method(*parameters), cls=FluxJSONEncoder)


def convert_to_snakecase(s: str) -> str:
    """
    Convert a string to snake case. For example, "MyApp" becomes "my_app".
    This is to follow the python convention for module names.
    """
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, s).lower()