"""Shared test configuration and fixtures.

The sys.path cleanup ensures tests use the installed eight_sleep_client
package and don't accidentally traverse into the parent HA integration.
"""

import sys

# Remove parent directories that contain HA integration code from sys.path.
# Without this, Python's import system walks up through __init__.py files
# in custom_components/eight_sleep/ and tries to import pyEight, which has
# dependencies we don't want in our test environment.
_parent_paths_to_remove = [
    p for p in sys.path
    if "custom_components" in p and "eight_sleep_client" not in p
]
for p in _parent_paths_to_remove:
    sys.path.remove(p)
