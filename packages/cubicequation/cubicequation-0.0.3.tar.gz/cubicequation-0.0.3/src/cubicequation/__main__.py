# pylint: disable=invalid-name
"""
Command line handling
"""

import sys

if __name__ == '__main__':
  from cubicequation import cubiccmd
  cubiccmd.CommandLine( sys.argv )
