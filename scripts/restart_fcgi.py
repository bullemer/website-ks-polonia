"""Switch Apache to a new FastCGI path after the backend has been deployed."""
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

revision = sys.argv[1]
if not re.fullmatch(r'[0-9a-f]{40}', revision):
    raise SystemExit('Invalid git revision')
directory = Path('/usr/home/trusteei/public_html/ks-polonia/api')
script = directory / ('api-runtime-' + revision + '.fcgi')
shutil.copyfile(directory / 'api.fcgi', script)
script.chmod(0o755)
htaccess = directory / '.htaccess'
source, count = re.subn(
    r'api(?:-v[0-9]+|-runtime-[a-f0-9]+)?\.fcgi/\$1',
    'api-runtime-' + revision + '.fcgi/$1', htaccess.read_text())
if count != 1:
    raise SystemExit('Unexpected API rewrite configuration; active path unchanged')
fd, name = tempfile.mkstemp(prefix='.htaccess-', dir=directory)
try:
    os.fchmod(fd, 0o644)
    with os.fdopen(fd, 'w') as out:
        out.write(source)
    os.replace(name, htaccess)
finally:
    if os.path.exists(name): os.unlink(name)
print('FCGI switched to new version')
