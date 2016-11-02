#! /usr/bin/env python3

# BCK - Oct 2016 - Regex parse test 

import ast
import re
import timeit

class timeitReturnTimer(timeit.Timer):
    timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""

def _template_func(setup, func):
    """Create a timer function. Used if the "statement" is a callable.
    http://stackoverflow.com/questions/24812253/how-can-i-capture-return-value-with-python-timeit-module
    """
    def inner(_it, _timer, _func=func):
        setup()
        _t0 = _timer()
        for _i in _it:
            retval = _func()
        _t1 = _timer()
        return _t1 - _t0, retval
    return inner


timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""

# timeit._template_func = _template_func

def mane():
    # this strings works in python as taken from RegexGenerator which marks them (JS)
    regex_strs = ["\d(?=((?:(?=(\w+))\2:)+))\1(?=(\w+))\3",
                  "\w\w:\w\w:(?=((?:(?=(\w+))\2:\w)*))\1\w",
                  "\w+"]
    # regex_str2 = "\\d(?:\\w++:)++\\w++" # this one does not (JAVA)
    # tree = ast.parse(regex_str)
    # print(ast.dump())

    # compreg = re.compile(regex_str, re.DEBUG)
    # time_regex(regex_str,search_string)
    for regex_str in regex_strs:
        time_regex(regex_str)
    
def get_function(regex_str):
    search_string = "Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)" 
    compiled_reg = re.compile(regex_str)
    regex_match = compiled_reg.match(search_string)
    def wrap():
        return compiled_reg.match(search_string)
#    t = timeit.Timer(wrap)
#    print(t.timeit())
#    eval_results = t.timeit()
    return wrap

def time_regex(regex_str):
    a_function = get_function(regex_str)
    print("Timing a function")
    t = timeitReturnTimer(a_function)
    eval_results = t.timeit(number=1000)
    print(eval_results)
    # print(min(t.repeat(repeat=3)))
    
if __name__ == "__main__":
    mane()
