import os
import sys
import logging
import functools
import threading
from contextlib import contextmanager

from recept.types import Path
from recept.apps.app import app


logger = logging.getLogger(__name__)


def with_lock(lock):
    """Protect a function call with a lock."""

    def decorator(fn):
        @contextmanager
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with lock:
                with fn(*args, **kwargs):
                    yield

        return wrapper

    return decorator


def cwd() -> str:
    """Return the absolute path to the current working directory."""
    return os.path.abspath(os.getcwd())


def cd(path: Path, create: bool = False):
    """Change directory.

    Args:
        path: Path to the directory we want to enter.
        create: Create the directory if it doesn't exist.
    """
    if create:
        os.makedirs(path, exist_ok=True)

    logger.debug("cd -> %s", path)
    os.chdir(str(path))


PUSHD_LOCK = threading.RLock()


@with_lock(PUSHD_LOCK)
@contextmanager
def pushd(path: Path, create: bool = False):
    """Context object for changing the current working directory.

    Args:
        path: Directory to go to.
        create: Create directory if it doesn't exists.

    Usage::

        >>> from recept.apps.shell import cwd, pushd
        >>> cwd()
        '/Users/alefnula/projects/recipes'
        >>> with pushd("recept"):
        ...     print(cwd())
        ...
        /Users/alefnula/projects/recept/recept
        >>> cwd()
        '/Users/alefnula/projects/recept'

        # If the director doesn't exist.

        >>> with pushd("foo", create=True):
        ...     print(cwd())
        ...     with pushd("bar", create=True):
        ...         print(cwd())
        ...         with pushd("baz", create=True):
        ...             print(cwd())
        ...         print(cwd())
        ...     print(cwd())
        ...
        /Users/alefnula/projects/recept/foo
        /Users/alefnula/projects/recept/foo/bar
        /Users/alefnula/projects/recept/foo/bar/baz
        /Users/alefnula/projects/recept/foo/bar
        /Users/alefnula/projects/recept/foo
        >>> cwd()
        '/Users/alefnula/projects/recept'


    `pushd` is thread-safe in a very basic way: Only one thread can use it at
    a time. This means that if one thread is using re-entrant calls to `pushd`
    all other threads will have to wait for that thread to exit the last
    `with` statement so they can get hold of the re-entrant `pushd` lock.

    Since the application can only have one current working directory, this is
    the only way to achieve thread safety.
    ```

    """

    cwd = os.getcwd()
    path = os.path.abspath(path)

    # If create is True, create the directory if it doesn't exist.
    if create:
        os.makedirs(path, exist_ok=True)

    logger.debug("pushd -> %s", path)
    os.chdir(path)
    try:
        yield
    finally:
        logger.debug("pushd <- %s", path)
        os.chdir(cwd)


# Shell commands
ls = app("ls")
rm = app("rm", "-rf")
cp = app("cp", "-rf")
find = app("find", _out=None)
mount = app("mount")
umount = app("umount", "-f")


# Python commands
python = app(sys.executable)
pip = app("pip")
pytest = app("py.test", "-s", _tee=False, _ok_code=[0, 1, 2, 3, 4, 5])
black = app("black")
flake8 = app("flake8", _ok_code=[0, 1])
pydocstyle = app("pydocstyle", _ok_code=[0, 1])


# Docker
docker = app("docker")
