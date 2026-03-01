"""Compatibility launcher for the original script with spaces in filename.

Why:
- Some shells split unquoted paths by spaces, causing:
  `python: can't open file '.../evaluate_Dumbledore_Affirmative': [Errno 2]`

Usage:
- Preferred: `python evaluate_Dumbledore_Affirmative_Suffix.py`
- Original (also works if quoted):
  `python "evaluate_Dumbledore_Affirmative Suffix.py"`
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).with_name("evaluate_Dumbledore_Affirmative Suffix.py")
    runpy.run_path(str(target), run_name="__main__")
