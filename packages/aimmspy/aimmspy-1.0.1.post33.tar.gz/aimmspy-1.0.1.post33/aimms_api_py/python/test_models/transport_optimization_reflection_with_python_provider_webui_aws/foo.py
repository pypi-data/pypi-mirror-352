# print sys.path
import sys
import os
with open(os.path.join(os.path.dirname(__file__), 'foo.txt'), 'w') as f:
    f.write('Hello from foo.py!\n')
    f.write('sys.path:\n')
    f.write(f"{sys.executable}\n")
    for path in sys.path:
        f.write(f'{path}\n')