# Change History

## 2022.8.28

* Added helper keyword functions for result projections
* Added jmespath dependency to ease test writing
* Added experimental source server support
* Updated baseline, SBOM, and third-party docs
* Completed initial test coverage of robot ticket system API with added self reflection test

## 2022.8.27

* Adapted creator example to changed package structure
* Adapted extract example to new log format
* Adapted logger module name for ping
* Adapted ping and creator examples to the new package structure; Linter happiness abound
* Adapted ping example to changed structure of package
* Added a robotframework ticket system library
* Added CPSR style example for creator store report
* Added CPSR style example for ping store report
* Added example creator connecting, requesting server info, requesting projects, and creating an issue
* Added example robot test file
* Added examples to linting and format targets
* Added new test deps (pytest-check==1.0.9)
* Added ping example
* Added robot related dependencies
* Added robotframework artifacts to git ignores
* Bumped dev deps (types-setuptools==65.3.0)
* Bumped test deps (dirty-equals==0.4)
* Fixed prelude log for ping
* Fixed setup counters for ping example
* Fixed timedelta calculation for steps taking a second or longer
* Prepared next release and added robot related dependencies
* Refactored common parts into init and storage into new store module
* Refactored further functionality and adapted tests
* Refactored implementation of 27-steps scenario to prepare for keyword use, add setup to store, and increase test coverage
* Removed superfluous shebang lines
* Simplified the setup function
* Updated baseline
* Updated SBOM
* Updated third-party docs

## 2022.8.24

* Added missing log lines for link, effort, set issue steps, and moved calculation of component name out of function
* Added remaining forgotten timing store lines for the prototype scenario
* Added microsecond resolution logging timestamps
* Simplified and minimized log lines
* Added generator version to logs
* Moved long data extracts to references section
* Made the example store grep script diagnostics less noisy
* Enhanced and extended the summarizer example script
* Updated third party docs and the SBOM
* Updated baseline
* Fixed types for create duplicate issue link function
* Moved the component name generation out of the function (input parameter)
* Bumped development dependencies (setuptools==65.3.0)
* Adapted tests to changed function signatures
* Added version adhoc to the implementation for logging (TODO)

## 2022.8.23

* Made all calls atomic (no more molecules like create issue pairs)
* Changed order of 2 x create issue - 2 x existence check to more canonical interlaced mode (early feedback)
* Replaced specifc key reference in JQL query log with generic identifier
* Wrapped deepcopy around all API calls to ensure no reference type is lazily filled (skewing the timing)
* Added a store analyzer example script

## 2022.8.22

* Fixed unprocessed vars in help strings for arguments
* Fixed mistaking clocking tuple for status return values
* Still not auto-detect for cloud vs. on-site (mode) default may claim on-site regardless
* Made all atomic transactions fully observable
* Added store implementation (JSON)
* Implemented collection of transaction results in context to database (JSON)
* Amended API and usage docs
* Bumped implementation dependencies

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
