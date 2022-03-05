import os
import ast
from .base import *
try:
    from .local import *
except ImportError as e:
    print('Not found local.py')

# Override config variables from environment
for var in list(locals()):
    value = os.getenv(var)
    if value is None:
        continue
    try:
        locals()[var] = ast.literal_eval(value)
    except:
        locals()[var] = value