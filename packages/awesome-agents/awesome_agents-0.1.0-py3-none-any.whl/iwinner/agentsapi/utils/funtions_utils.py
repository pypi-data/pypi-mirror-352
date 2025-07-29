from typing import Callable, Dict


def add(x: int, y: int) -> int:
    "Add function"
    return x + y


def mult(x: int, y: int) -> int:
    "Mult function"
    return x * y


def get_fun_signature(fn: Callable):
    fn_dict: Dict = {
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": {
            "properties": {}
        }
    }
    print(fn_dict)
    # for k, v in fn.__annotations__.items():
    #     print(f" k={k} and v={v}")
    schema = {
        k: {"type": v.__name__} for k, v in fn.__annotations__.items() if k != "return"
    }
    fn_dict["parameters"]["properties"]=schema
    return fn_dict


print(get_fun_signature(add))
