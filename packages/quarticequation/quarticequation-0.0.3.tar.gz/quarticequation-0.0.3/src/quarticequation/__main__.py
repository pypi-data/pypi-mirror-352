# pylint: disable=invalid-name
"""
Command line handling
"""

import sys

if __name__ == '__main__':
  from quarticequation import quarticcmd
  quarticcmd.CommandLine( sys.argv )
