# Change History

## 2022.8.21

* Flattened the API for labeling (to ease keyword API)
* Refactored all transactions into functions to prepare keyword library creation
* Added atomic versions for most REST transactions
* Added clocking decoration for all scenario functions
* Added the reason for the cleanup upon failed issue-component association to the logging
* Reduced response log for component creation
* Fenced server info log to a line
* Harmonized the purge me comment, shortedned the response logs for comments
* Added tests for all non-main functions (mocked) reaching 2/3 test coverage
* Extended and bumped dev and test dependencies
* Maximized pyproject.toml content (only had to keep flake8 config in setup.cfg until upstream project opens up ...)

## 2022.8.17

* Added new dict based memoizing extractor (examples)
* Added dict based analyzer with less wordy labels and larger symbols (examples)

## 2022.8.16

* Added examples scripts for log extraction and graphical reporting durations per target and scenario
* Bumped dev and test deps
* Made README and docs landing page lobby for the distributed in dvcs (git), codeberg, and sourcehut
* Fixed a state literal ...
* Added node incator log line
* Enhanced code quality
* Added the either cloud or on-site upstream info to the log
* Unlittered the code and added more info to created issues as well as to the log

## 2022.8.11

* Initial release on PyPI
