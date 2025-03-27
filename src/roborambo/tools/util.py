from typing import Callable

# Helpers for decorator config
def ifelex(l, i):
    if not isinstance(l, Callable) and l is not None and len(l) > 0: return [i]
    else: return None
def storeifindictlist(con, **kwargs):
    result = {}
    for i in con:
        for j in con[i]:
            if j in kwargs: result[i] = kwargs[j]
    return result
def conf_wrapper(w, **kwds):
    def wrapper(c, **kwargs):
        if '__config__' not in c.__dict__: c.__config__ = { 'tool_methods': {} }
        getattr(c, '__config__').update(**(kwargs|kwds))
        return c
    return wrapper(w) if isinstance(w, Callable) else wrapper
def wrap_config(dict, **kwargs): return conf_wrapper(ifelex(dict, 0), **kwargs)

# Decorators
def tool_desc(*args, **kwargs): return wrap_config(args, **storeifindictlist({'tool_desc': {'desc': str}}, desc = args[0]))
def tool_name(*args, **kwargs): return wrap_config(args, **storeifindictlist({'tool_name': {'name': str}}, name = args[0]))
def tool_class(*args, **kwargs):
    return wrap_config(args, **storeifindictlist({
        'tool_name': {'name': str},
        'tool_desc': {'desc': str},
    }, **kwargs))
def tool_method(*args, **kwargs):
    return wrap_config(ifelex(args, 0), **storeifindictlist({
        'method_name': {'name': str},
        'method_desc': {'desc': str},
        'method_enabled': {'enabled': bool},
    }, **kwargs))
def method_arg(*args, **kwargs):
    return wrap_config(ifelex(args, 0), arguments = {
        kwargs['name']: storeifindictlist({
            'arg_desc': {'desc': str},
            'arg_type': {'type': str},
            'arg_enabled': {'enabled': bool},
        }, **kwargs)
    })