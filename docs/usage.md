# Usage

To use suhteita in a project:

```python
import suhteita.suhteita as api
```

For the commandline (for now) please add the help option like so:

```console
❯ suhteita --help
usage: __main__.py [-h] [--user USER] [--token TOKEN] [--target TARGET_URL] [--is-cloud] [--project TARGET_PROJECT]
                   [--scenario SCENARIO] [--workflow WORKFLOW_CSV] [--identity IDENTITY] [--out-path OUT_PATH]
                   [--debug] [--trace] [--version]

suhteita

options:
  -h, --help            show this help message and exit
  --user USER, -u USER  user (default: stefan@dilettant.eu)
  --token TOKEN, -T TOKEN
                        token (default: set {APP_ENV}_TOKEN for default)
  --target TARGET_URL, -t TARGET_URL
                        target URL (default: https://dilettant.atlassian.net)
  --is-cloud            target is cloud instance (default: False, set SUHTEITA_IS_CLOUD for a different default)
  --project TARGET_PROJECT, -p TARGET_PROJECT
                        target project (default: None, set SUHTEITA_PROJECT for default)
  --scenario SCENARIO, -s SCENARIO
                        scenario for recording (default: unknown)
  --workflow WORKFLOW_CSV, -w WORKFLOW_CSV
                        workflow triplet as comma separated values(default: "to do,in progress,done")
  --identity IDENTITY, -i IDENTITY
                        identity of take for recording (default: adhoc, set SUHTEITA_IDENTITY for default)
  --out-path OUT_PATH, -o OUT_PATH
                        output folder path for recording (default: store, set SUHTEITA_STORE for default)
  --debug, -d           emit debug level information (default: False, set SUHTEITA_DEBUG for a different default)
  --trace               hand down debug level request to imported modules (default: "False")
  --version, -V         print version info and exit
```
