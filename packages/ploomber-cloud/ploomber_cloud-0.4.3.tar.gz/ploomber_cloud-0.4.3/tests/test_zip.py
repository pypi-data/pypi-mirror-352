from pathlib import Path
import zipfile
from functools import partial

import pytest

from ploomber_cloud import zip_


def _git_directory(base_dir):
    Path("a").touch()
    Path("b").touch()
    Path(".env").touch()
    somehiddendir = Path(".somehiddendir")
    somehiddendir.mkdir()
    (somehiddendir / "somefile").touch()

    somedir = Path("somedir")
    somedir.mkdir()
    (somedir / "anotherfile").touch()

    dot_git = Path(base_dir, ".git")
    dot_git.mkdir(parents=True)
    (dot_git / "somegitfile").touch()
    (dot_git / "anothergitfile").touch()

    Path("somefile.pyc").touch()
    pycache = Path("__pycache__")
    pycache.mkdir()
    (pycache / "somefile.pyc").touch()


def _ign_directory(base_dir):
    Path("a").touch()
    Path("b").touch()
    somehiddendir = Path(".somehiddendir")
    somehiddendir.mkdir()
    (somehiddendir / "somefile").touch()
    (somehiddendir / "env").touch()

    envdir = Path("env")
    envdir.mkdir()
    (envdir / "a").mkdir()
    (envdir / "a" / "b").touch()

    somedir = Path("somedir")
    somedir.mkdir()
    (somedir / "anotherfile").touch()
    (somedir / "env").mkdir()
    (somedir / "env" / "file").touch()
    (somedir / "a").touch()

    anotherdir = Path("anotherdir")
    anotherdir.mkdir()
    (anotherdir / "b").mkdir()
    (anotherdir / "b" / "file").touch()


git_directory_root = partial(_git_directory, base_dir="")
git_directory_subdir = partial(_git_directory, base_dir="subdir")
ign_directory_root = partial(_ign_directory, base_dir="")


@pytest.mark.parametrize(
    "init_function",
    [
        git_directory_root,
        git_directory_subdir,
    ],
)
def test_zip_app(tmp_empty, init_function):
    init_function()

    with zip_.zip_app(verbose=True) as (path_to_zip, _):
        with zipfile.ZipFile(path_to_zip) as app_zip:
            namelist = app_zip.namelist()

    assert not Path(path_to_zip).exists()
    assert set(namelist) == {
        "a",
        "b",
        ".env",
        ".somehiddendir/somefile",
        "somedir/anotherfile",
    }


@pytest.mark.parametrize(
    "user_ignore, result",
    (
        [
            [],
            {
                "a",
                "b",
                ".somehiddendir/somefile",
                ".somehiddendir/env",
                "env/a/b",
                "somedir/anotherfile",
                "somedir/env/file",
                "somedir/a",
                "anotherdir/b/file",
            },
        ],
        [
            ["/"],
            set(),
        ],
        [
            ["nonexistent", "", None],
            {
                "a",
                "b",
                ".somehiddendir/somefile",
                ".somehiddendir/env",
                "env/a/b",
                "somedir/anotherfile",
                "somedir/env/file",
                "somedir/a",
                "anotherdir/b/file",
            },
        ],
        [
            ["env"],
            {
                "a",
                "b",
                ".somehiddendir/somefile",
                "somedir/anotherfile",
                "somedir/a",
                "anotherdir/b/file",
            },
        ],
        [
            ["env/", "anotherdir", "somefile"],
            {"a", "b", ".somehiddendir/env", "somedir/anotherfile", "somedir/a"},
        ],
        [
            [
                "a",
                "b/",
                "env/",
                "somefolder/somefile",
                "somedir/anotherfile",
                ".somehiddendir/env/",
            ],
            {"b", ".somehiddendir/somefile", ".somehiddendir/env"},
        ],
    ),
    ids=[
        "test-no-ignore",
        "test-ignore-root",
        "test-ignore-file-not-exist",
        "test-ignore-single-name",
        "test-ignore-name-and-dir",
        "test-ignore-name-dir-and-combined",
    ],
)
def test_zip_ignore_files(tmp_empty, user_ignore, result):
    ign_directory_root()

    with zip_.zip_app(verbose=True, user_ignored=user_ignore) as (path_to_zip, _):
        with zipfile.ZipFile(path_to_zip) as app_zip:
            namelist = app_zip.namelist()

    assert not Path(path_to_zip).exists()
    assert set(namelist) == result


@pytest.mark.parametrize(
    "path, user_ignored, result",
    (
        ["user", [], False],
        ["user", [""], False],
        ["user.txt", ["user.txt"], True],
        ["user/hello/world.txt", ["user"], True],
        ["hello/world/world2/world3/user.txt", ["user.txt"], True],
        ["hello/world/world2/world3/user/hello.txt", ["user"], True],
        ["user.txt", ["user.txts", "_user.txt"], False],
        ["user/hello.txt", ["user/"], True],
        ["hello/world/world2/user/hello.txt", ["user/"], True],
        ["user", ["user/"], False],
        ["hello/world.txt", ["hello/world.txt"], True],
        ["world.txt", ["hello/world.txt"], False],
        ["user/hello/test.txt", ["user/hello"], True],
        ["user/hello", ["user/hello/", "user/world/hello"], False],
        ["user/hello/world/world2/world3/hi.txt", ["user/hello/world"], True],
        ["hello/user/hello/world/hi.txt", ["user/hello", "hello/world/hi.txt"], False],
        ["hello/.user/_hello/world/hi.txt", ["hello/.user/_hello"], True],
    ),
    ids=[
        "test-blacklisted-no-ignore",
        "test-blacklisted-no-ignore-2",
        "test-blacklisted-single-part",
        "test-blacklisted-single-part-dir",
        "test-blacklisted-single-part-recursive",
        "test-blacklisted-single-part-recursive-dir",
        "test-blacklisted-single-part-misspell",
        "test-blacklisted-single-dir",
        "test-blacklisted-single-dir-recursive",
        "test-blacklisted-single-dir-file-not-removed",
        "test-blacklisted-multi",
        "test-blacklisted-multi-same-file-not-same-dir",
        "test-blacklisted-multi-file",
        "test-blacklisted-multi-file-not-removed",
        "test-blacklisted-multi-children",
        "test-blacklisted-multi-no-recursive",
        "test-blacklisted-special-char",
    ],
)
def test_blacklisted_file(tmp_empty, path, user_ignored, result):
    assert zip_._is_blacklisted_file(path, user_ignored) == result


@pytest.mark.parametrize(
    "init_function",
    [
        git_directory_root,
        git_directory_subdir,
    ],
)
def test_zip_passes_empty_env_file(tmp_empty, init_function):
    init_function()
    with open(Path(".env"), "w") as env_file:
        env_file.write("ENV_VAR_1=value")

    with zip_.zip_app(verbose=True) as (path_to_zip, _):
        with zipfile.ZipFile(path_to_zip) as app_zip:
            with app_zip.open(".env") as env_in_zip:
                lines = env_in_zip.readlines()

    assert len(lines) == 0


@pytest.mark.parametrize(
    "init_function",
    [
        git_directory_root,
        git_directory_subdir,
    ],
)
def test_zip_doesnt_erase_local_env_file(tmp_empty, init_function):
    init_function()
    with open(Path(".env"), "w") as env_file:
        env_file.write("ENV_VAR_1=value")

    zip_.zip_app(verbose=True)

    with open(Path(".env"), "r") as env_file:
        lines = env_file.readlines()

    assert lines == ["ENV_VAR_1=value"]
