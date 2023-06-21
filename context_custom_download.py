import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from plugin import doPlayDownload

if __name__ == '__main__':
    doPlayDownload("download", True)
