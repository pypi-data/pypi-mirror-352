import errno
import gc
import mmap
import os
import time

pjoin = os.path.join

import pytest
from snakeoil import _fileutils, currying, fileutils
from snakeoil.fileutils import AtomicWriteFile
from snakeoil.test import random_str


class TestTouch:
    @pytest.fixture
    def random_path(self, tmp_path):
        return tmp_path / random_str(10)

    def test_file_creation(self, random_path):
        orig_um = os.umask(0o000)
        try:
            fileutils.touch(random_path)
        finally:
            exiting_umask = os.umask(orig_um)
        assert exiting_umask == 0o000
        assert random_path.exists()
        assert random_path.stat().st_mode & 0o4777 == 0o644

    def test_set_times(self, random_path):
        fileutils.touch(random_path)
        orig_stat = random_path.stat()
        time.sleep(1)
        fileutils.touch(random_path)
        new_stat = random_path.stat()
        assert orig_stat.st_atime != new_stat.st_atime
        assert orig_stat.st_mtime != new_stat.st_mtime

    def test_set_custom_times(self, random_path):
        fileutils.touch(random_path)
        orig_stat = random_path.stat()
        times = (1, 1)
        fileutils.touch(random_path, times=times)
        new_stat = random_path.stat()
        assert orig_stat != new_stat
        assert 1 == new_stat.st_atime
        assert 1 == new_stat.st_mtime

    def test_set_custom_nstimes(self, random_path):
        fileutils.touch(random_path)
        orig_stat = random_path.stat()
        ns = (1, 1)
        fileutils.touch(random_path, ns=ns)
        new_stat = random_path.stat()

        # system doesn't have nanosecond precision, try microseconds
        if new_stat.st_atime == 0:
            ns = (1000, 1000)
            fileutils.touch(random_path, ns=ns)
            new_stat = random_path.stat()

        assert orig_stat != new_stat
        assert ns[0] == new_stat.st_atime_ns
        assert ns[0] == new_stat.st_mtime_ns


class TestAtomicWriteFile:
    kls = AtomicWriteFile

    def test_normal_ops(self, tmp_path):
        (fp := tmp_path / "target").write_text("me")
        af = self.kls(fp)
        af.write("dar")
        assert fileutils.readfile_ascii(fp) == "me"
        af.close()
        assert fileutils.readfile_ascii(fp) == "dar"

    def test_perms(self, tmp_path):
        fp = tmp_path / "target"
        orig_um = os.umask(0o777)
        try:
            af = self.kls(fp, perms=0o644)
            af.write("dar")
            af.close()
        finally:
            exiting_umask = os.umask(orig_um)
        assert exiting_umask == 0o777
        assert os.stat(fp).st_mode & 0o4777 == 0o644

    def test_del(self, tmp_path):
        (fp := tmp_path / "target").write_text("me")
        assert fileutils.readfile_ascii(fp) == "me"
        af = self.kls(fp)
        af.write("dar")
        del af
        gc.collect()
        assert fileutils.readfile_ascii(fp) == "me"
        assert len(os.listdir(tmp_path)) == 1

    def test_close(self, tmp_path):
        # verify that we handle multiple closes; no exception is good.
        af = self.kls(tmp_path / "target")
        af.close()
        af.close()

    def test_discard(self, tmp_path):
        (fp := tmp_path / "target").write_text("me")
        assert fileutils.readfile_ascii(fp) == "me"
        af = self.kls(fp)
        af.write("dar")
        af.discard()
        assert not os.path.exists(af._temp_fp)
        af.close()
        assert fileutils.readfile_ascii(fp) == "me"

        # finally validate that it handles multiple discards properly.
        af = self.kls(fp)
        af.write("dar")
        af.discard()
        af.discard()
        af.close()


class Test_readfile:
    func = staticmethod(fileutils.readfile)

    test_cases = ["asdf\nfdasswer\1923", "", "987234"]

    default_encoding = "ascii"
    none_on_missing_ret_data = "dar"

    @staticmethod
    def convert_data(data, encoding):
        if isinstance(data, bytes):
            return data
        if encoding:
            return data.encode(encoding)
        return data

    def test_it(self, tmp_path):
        fp = tmp_path / "testfile"
        for expected in self.test_cases:
            raised = None
            encoding = self.default_encoding
            if isinstance(expected, tuple):
                if len(expected) == 3:
                    raised = expected[2]
                if expected[1] is not None:
                    encoding = expected[1]
                expected = expected[0]
            fp.write_bytes(self.convert_data(expected, encoding))
            if raised:
                with pytest.raises(raised):
                    self.assertFunc(fp, expected)
            else:
                self.assertFunc(fp, expected)

    def assertFunc(self, path, expected):
        assert self.func(path) == expected

    def test_none_on_missing(self, tmp_path):
        fp = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            self.func(fp)
        assert self.func(fp, True) is None
        fp.write_bytes(self.convert_data("dar", "ascii"))
        assert self.func(fp, True) == self.none_on_missing_ret_data

        # ensure it handles paths that go through files-
        # still should be suppress
        assert self.func(fp / "extra", True) is None


class Test_readfile_ascii(Test_readfile):
    func = staticmethod(fileutils.readfile_ascii)


class Test_readfile_utf8(Test_readfile):
    func = staticmethod(fileutils.readfile_utf8)
    default_encoding = "utf8"


class Test_readfile_bytes(Test_readfile):
    func = staticmethod(fileutils.readfile_bytes)
    default_encoding = None
    test_cases = list(
        map(
            currying.post_curry(Test_readfile.convert_data, "ascii"),
            Test_readfile.test_cases,
        )
    )
    test_cases.append("\ua000fa".encode("utf8"))
    none_on_missing_ret_data = Test_readfile.convert_data(
        Test_readfile.none_on_missing_ret_data, "ascii"
    )


class readlines_mixin:
    def assertFunc(self, path, expected):
        expected = tuple(expected.split())
        if expected == ("",):
            expected = ()

        if "utf8" not in self.encoding_mode:
            assert tuple(self.func(path)) == expected
            return
        assert tuple(self.func(path)) == expected

    def test_none_on_missing(self, tmp_path):
        fp = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            self.func(fp)
        assert not tuple(self.func(fp, False, True))
        fp.write_bytes(self.convert_data("dar", "ascii"))
        assert tuple(self.func(fp, True)) == (self.none_on_missing_ret_data,)
        assert not tuple(self.func(fp / "missing", False, True))

    def test_strip_whitespace(self, tmp_path):
        fp = tmp_path / "data"

        fp.write_bytes(self.convert_data(" dar1 \ndar2 \n dar3\n", "ascii"))
        results = tuple(self.func(fp, True))
        expected = ("dar1", "dar2", "dar3")
        if self.encoding_mode == "bytes":
            expected = tuple(x.encode("ascii") for x in expected)
        assert results == expected

        # this time without the trailing newline...
        fp.write_bytes(self.convert_data(" dar1 \ndar2 \n dar3", "ascii"))
        results = tuple(self.func(fp, True))
        assert results == expected

        # test a couple of edgecases; underly c extension has gotten these
        # wrong before.
        fp.write_bytes(self.convert_data("0", "ascii"))
        results = tuple(self.func(fp, True))
        expected = ("0",)
        if self.encoding_mode == "bytes":
            expected = tuple(x.encode("ascii") for x in expected)
        assert results == expected

        fp.write_bytes(self.convert_data("0\n", "ascii"))
        results = tuple(self.func(fp, True))
        expected = ("0",)
        if self.encoding_mode == "bytes":
            expected = tuple(x.encode("ascii") for x in expected)
        assert results == expected

        fp.write_bytes(self.convert_data("0 ", "ascii"))
        results = tuple(self.func(fp, True))
        expected = ("0",)
        if self.encoding_mode == "bytes":
            expected = tuple(x.encode("ascii") for x in expected)
        assert results == expected


def mk_readlines_test(scope, mode):
    func_name = "readlines_%s" % mode
    base = globals()["Test_readfile_%s" % mode]

    class kls(readlines_mixin, base):
        func = staticmethod(getattr(fileutils, func_name))
        encoding_mode = mode

    kls.__name__ = "Test_%s" % func_name
    scope["Test_%s" % func_name] = kls


for case in ("ascii", "bytes", "utf8"):
    name = "readlines_%s" % case
    mk_readlines_test(locals(), case)


class TestBrokenStats:
    test_cases = ["/proc/crypto", "/sys/devices/system/cpu/present"]

    def test_readfile(self):
        for path in self.test_cases:
            self._check_path(path, fileutils.readfile)

    def test_readlines(self):
        for path in self.test_cases:
            self._check_path(path, fileutils.readlines, True)

    def _check_path(self, path, func, split_it=False):
        try:
            with open(path, "r") as handle:
                data = handle.read()
        except EnvironmentError as e:
            if e.errno not in (errno.ENOENT, errno.EPERM):
                raise
            return

        func_data = func(path)
        if split_it:
            func_data = list(func_data)
            data = [x for x in data.split("\n") if x]
            func_data = [x for x in func_data if x]

        assert func_data == data


class Test_mmap_or_open_for_read:
    func = staticmethod(fileutils.mmap_or_open_for_read)

    def test_zero_length(self, tmp_path):
        (path := tmp_path / "target").write_text("")
        m, f = self.func(path)
        assert m is None
        assert f.read() == b""
        f.close()

    def test_mmap(self, tmp_path, data=b"foonani"):
        (path := tmp_path / "target").write_bytes(data)
        m, f = self.func(path)
        assert len(m) == len(data)
        assert m.read(len(data)) == data
        m.close()
        assert f is None


class Test_mmap_and_close:
    def test_it(self, tmp_path):
        (path := tmp_path / "target").write_bytes(data := b"asdfasdf")
        fd, m = None, None
        try:
            fd = os.open(path, os.O_RDONLY)
            m = _fileutils.mmap_and_close(
                fd, len(data), mmap.MAP_PRIVATE, mmap.PROT_READ
            )
            # and ensure it closed the fd...
            with pytest.raises(EnvironmentError):
                os.read(fd, 1)
            fd = None
            assert len(m) == len(data)
            assert m.read(len(data)) == data
        finally:
            if m is not None:
                m.close()
            if fd is not None:
                os.close(fd)
