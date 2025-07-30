import sys
def test_path():
  assert '/workspaces/sdtp/src' in sys.path
  from sdtp import SDML_BOOLEAN 