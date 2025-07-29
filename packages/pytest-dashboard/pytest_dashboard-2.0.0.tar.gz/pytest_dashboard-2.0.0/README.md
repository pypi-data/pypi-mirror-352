# pytest-dashboard

## example
- Download project
- Run some pytest with `--progress-path` option. The value should end with `-progress.yaml`.
    - i.e.) `pytest <path_to_project>\sample-tests --progress-path=<path_to_project>\sample-tests\sample-progress.yaml`
    - You will get a `sample-progress.yaml` file.
- Run pytest dashboard
    - i.e.) `tally-pytest <path_to_project>\sample-tests`
    - You will get a `entire-progress.yaml` file in working folder.

## usage
`pytest`

By this command, you get `[datetime]-progress.yaml` file on working directory as realtime pytest progress report.

---

`pytest --progress-path=[path/to/some-progress.yaml]`

By this command, you get `path/to/some-progress.yaml` file.
The value should end with `-progress.yaml`.
