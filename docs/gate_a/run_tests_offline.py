"""Fallback when macOS refuses nested sandbox-exec; block socket connects."""
from pathlib import Path
import os
import socket
import sys
import unittest
from unittest.mock import patch

root=Path(__file__).resolve().parents[2]
os.chdir(root)
sys.path.insert(0,str(root))
with patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')):
    suite=unittest.defaultTestLoader.discover('tests/audit',top_level_dir='.')
    result=unittest.TextTestRunner().run(suite)
    raise SystemExit(not result.wasSuccessful())
