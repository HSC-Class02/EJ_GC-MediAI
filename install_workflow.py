"""Run locally after extracting the ZIP; never requires an API key."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
source=root/'workflow_templates/dart-update.yml'
target=root/'.github/workflows/dart-update.yml'
if target.exists() and target.read_bytes()!=source.read_bytes():
 raise SystemExit('Existing workflow differs. Back it up and remove it yourself before installing.')
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,target)
print('Installed .github/workflows/dart-update.yml. Commit and push this file to the default branch.')
