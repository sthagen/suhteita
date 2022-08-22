# Usage

To use suhteita in a project:

```python
import suhteita.suhteita as api
```

For the commandline (for now) please add the help option like so:

```console
❯ suhteita --help
usage: __main__.py [-h] [--user USER] [--target TARGET_URL] [--is-cloud] [--project TARGET_PROJECT] [--scenario SCENARIO] [--identity IDENTITY] [--out-path OUT_PATH]

suhteita

options:
  -h, --help            show this help message and exit
  --user USER, -u USER  user (default: stefan@dilettant.eu)
  --target TARGET_URL, -t TARGET_URL
                        target URL (default: https://dilettant.atlassian.net)
  --is-cloud            target is cloud instance (default: False, set SUHTEITA_IS_CLOUD for a different default)
  --project TARGET_PROJECT, -p TARGET_PROJECT
                        target project (default: None, set SUHTEITA_PROJECT for default)
  --scenario SCENARIO, -s SCENARIO
                        scenario for recording (default: unknown)
  --identity IDENTITY, -i IDENTITY
                        identity of take for recording (default: adhoc, set SUHTEITA_IDENTITY for default)
  --out-path OUT_PATH, -o OUT_PATH
                        output folder path for recording (default: store, set SUHTEITA_STORE for default)
```
