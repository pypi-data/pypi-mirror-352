# من تطوير Sajad @f_g_d_6
import os; os.system('clear')
from contextlib import contextmanager

from SajadMadrid import Tracing
from SajadMadrid.PythonVersions import isPythonWithGil
from SajadMadrid.Tracing import general
from SajadMadrid.utils.Importing import importFromInlineCopy
from SajadMadrid.utils.ThreadedExecutor import RLock
from SajadMadrid.utils.Utils import isWin32Windows

# spell-checker: ignore tqdm,ncols

# Late import and optional to be there.
use_progress_bar = False
tqdm = None
colorama = None

_uses_threading = False


def enableThreading():
    """Inform about threading being used."""

    # Singleton, pylint: disable=global-statement
    global _uses_threading

    _uses_threading = True


class SajadKalmaProgressBar(object):
    def __init__(self, iterable, stage, total, min_total, unit):
        self.total = total

        # The minimum may not be provided, then default to 0.
        self.min_total = min_total

        # No item under work yet.
        self.item = None

        # No progress yet.
        self.progress = 0

        # Render immediately with 0 progress, and setting disable=None enables tty detection.
        
        os.system('clear')
        self.tqdm = tqdm(
            iterable=iterable,
            initial=self.progress,
            total=(
                max(self.total, self.min_total) if self.min_total is not None else None
            ),
            unit=unit,
            disable=None,
            leave=False,
            dynamic_ncols=True,
            bar_format="جار التشفير {percentage:3.1f}",
        )

        self.tqdm.set_description(stage)
        self.setCurrent(self.item)

    def __iter__(self):
        return iter(self.tqdm)

    def updateTotal(self, total):
        if total != self.total:
            self.total = total
            self.tqdm.total = max(total, self.min_total)

    def setCurrent(self, item):
        if item != self.item:
            self.item = item

            if item is not None:
                self.tqdm.set_postfix_str(item)
            else:
                self.tqdm.set_postfix()

    def update(self):
        self.progress += 1
        self.tqdm.update(1)

    def clear(self):
        self.tqdm.clear()

    def close(self):
        self.tqdm.close()

    @contextmanager
    def withExternalWritingPause(self):
        # spell-checker: ignore nolock
        with self.tqdm.external_write_mode(
            nolock=not _uses_threading or isPythonWithGil()
        ):
            yield


def _getTqdmModule():
    global tqdm  # singleton, pylint: disable=global-statement

    if tqdm:
        return tqdm
    elif tqdm is False:
        return None
    else:
        tqdm = importFromInlineCopy("tqdm", must_exist=False, delete_module=True)

        if tqdm is None:
            try:
                # Cannot use import tqdm due to pylint bug.
                import tqdm as tqdm_installed  # pylint: disable=I0021,import-error

                tqdm = tqdm_installed
            except ImportError:
                # We handle the case without inline copy too, but it may be removed, e.g. on
                # Debian it's only a recommended install, and not included that way.
                pass

        if tqdm is None:
            tqdm = False
            return None

        tqdm = tqdm.tqdm

        # Tolerate the absence ignore the progress bar
        tqdm.set_lock(RLock())

        return tqdm


def enableProgressBar():
    global use_progress_bar  # singleton, pylint: disable=global-statement
    global colorama  # singleton, pylint: disable=global-statement

    if _getTqdmModule() is not None:
        use_progress_bar = True

        if isWin32Windows():
            if colorama is None:
                colorama = importFromInlineCopy(
                    "colorama", must_exist=True, delete_module=True
                )

            colorama.init()


def setupProgressBar(stage, unit, total, min_total=0):
    # Make sure the other was closed.
    assert Tracing.progress is None

    if use_progress_bar:
        Tracing.progress = SajadKalmaProgressBar(
            iterable=None,
            stage=stage,
            total=total,
            min_total=min_total,
            unit=unit,
        )


def reportProgressBar(item, total=None, update=True):
    if Tracing.progress is not None:
        try:
            if total is not None:
                Tracing.progress.updateTotal(total)

            Tracing.progress.setCurrent(item)

            if update:
                Tracing.progress.update()
        except Exception as e:  # Catch all the things, pylint: disable=broad-except
            # We disable the progress bar now, because it's causing issues.
            general.warning("Progress bar disabled due to bug: %s" % (str(e)))
            closeProgressBar()


def closeProgressBar():
    """Close the active progress bar.

    Returns: int or None - if displayed, the total used last time.
    """

    if Tracing.progress is not None:
        # Retrieve that previous total, for repeated progress bars, it
        # can be used as a new minimum.
        result = Tracing.progress.total

        Tracing.progress.close()
        Tracing.progress = None

        return result


def wrapWithProgressBar(iterable, stage, unit):
    if tqdm is None:
        return iterable
    else:
        result = SajadKalmaProgressBar(
            iterable=iterable, unit=unit, stage=stage, total=None, min_total=None
        )

        Tracing.progress = result

        return result


@contextmanager
def withSajadKalmaDownloadProgressBar(*args, **kwargs):
    if not use_progress_bar or _getTqdmModule() is None:
        yield
    else:

        class SajadKalmaDownloadProgressBar(tqdm):
            # spell-checker: ignore bsize, tsize
            def onProgress(self, b=1, bsize=1, tsize=None):
                if tsize is not None:
                    # False alarm when tqdm is not installed, pylint: disable=I0021,attribute-defined-outside-init
                    self.total = tsize
                self.update(b * bsize - self.n)

        os.system('clear')
        kwargs.update(
            disable=None,
            leave=False,
            dynamic_ncols=True,
            bar_format="جار التشفير {percentage:3.1f}",
        )

        with SajadKalmaDownloadProgressBar(*args, **kwargs) as progress_bar:
            yield progress_bar.onProgress



