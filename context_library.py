import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from plugin import doLibraryAction

if __name__ == '__main__':
    if len(sys.argv) > 1:
        doLibraryAction(sys.argv[1])
