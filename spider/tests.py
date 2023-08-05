from functools import wraps, partial


def xlogging(func, id = None):
    # @wraps(func)
    def wrapper(*args, **kwargs):
        print(id, func.__name__, "Loggin input", args, kwargs)
        r = func(*args, **kwargs)
        print("Loggin output", r)
        return r
    return wrapper


new = partial(xlogging, id=1)


@xlogging
def ct(_in: str, _out: str) -> str:
    return _in + _out


if __name__ == "__main__":
    a = ct(_in="Ana", _out=" are mere")
    print(a)