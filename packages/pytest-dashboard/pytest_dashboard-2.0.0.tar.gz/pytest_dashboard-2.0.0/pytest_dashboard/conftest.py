"""Create and update [datetime]-progress.yaml file as processing progresses."""


import os
import datetime

from pytest import (
    Session,
    TestReport,
)


progress_path = None


def set_log_path(root, specified_path=None):
    global progress_path
    if specified_path is None:
        progress_path = os.path.join(
            root,
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S-progress.yaml'),
        )
    else:
        progress_path = specified_path


def pytest_addoption(parser):
    parser.addoption(
        '--progress-path', action='store', default=None, help='pytest progress file path (.yaml)'
    )


def pytest_collection_finish(session: Session):
    specified_path = session.config.getoption('progress_path')
    set_log_path(session.startpath, specified_path)  # if None, directory where pytest is launched

    item_names = set([item.name for item in session.items])
    assert len(item_names) == len(session.items), 'The test name must not be duplicated.'

    with open(progress_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'items:\n')
        f.writelines([f'  - {item.name}\n' for item in session.items])
        f.write(f'results:\n')


def pytest_runtest_logreport(report: TestReport):
    with open(progress_path, 'a', encoding='utf-8', newline='\n') as f:

        if report.when == 'setup' and report.outcome == 'skipped':
            f.write(f'  {report.location[2]}: skipped\n')

        elif report.when == 'call':
            f.write(f'  {report.location[2]}: {report.outcome}\n')
