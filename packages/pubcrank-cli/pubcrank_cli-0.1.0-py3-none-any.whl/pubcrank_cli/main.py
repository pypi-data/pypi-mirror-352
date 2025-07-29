import sys
from pathlib import Path

from pubcrank.bin import generate_cli

def run():
  django_path = Path(__file__).parent.parent / 'django_proj'
  sys.path.append(str(django_path.resolve()))
  generate_cli(django=django_path, settings='pubsite.settings').run()


if __name__ == '__main__':
  run()
