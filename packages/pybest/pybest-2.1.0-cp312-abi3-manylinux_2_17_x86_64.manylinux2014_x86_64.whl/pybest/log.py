# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --

# Detailed changelog:
#
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update to new python features, including f-string, property decorators
# 2020-07-01: update to PyBEST standards
# 2020-07-01: included new HEADER and FOOTER

"""Screen logging, timing, and citation management

The screen logger tracks the progress of a calculation in a convenient
human-readable way, possibly highlighting problematic situations.
It is not intended as a computer-readable output file that contains all the
results of a calculation for restarts or postprocessing. For that purpose,
all useful data is written to a binary checkpoint file.
"""

import atexit
import datetime
import getpass
import os
import resource
import sys
import time
import traceback
import urllib
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

from pylatexenc.latex2text import LatexNodes2Text

from pybest.context import context

from . import __version__

__all__ = ["log", "timer"]


class ScreenLog:
    # log levels
    silent = 0
    warning = 1
    low = 2
    medium = 3
    high = 4
    debug = 5

    # screen parameter
    width = 100

    def __init__(
        self, name, version_, head_banner_, foot_banner_, timer_, f=None
    ):
        self.name = name
        self.version = version_
        self.head_banner = head_banner_
        self.foot_banner = foot_banner_
        self.timer = timer_

        self._biblio = None
        self.mem = MemoryLogger(self)
        self._active = False
        self.level = self.medium
        self._last_blank = False
        self.add_newline = False
        if f is None:
            _file = sys.stdout
        else:
            _file = f
        self._file = _file

    @property
    def do_warning(self):
        return self.level >= self.warning

    @property
    def do_low(self):
        return self.level >= self.low

    @property
    def do_medium(self):
        return self.level >= self.medium

    @property
    def do_high(self):
        return self.level >= self.high

    @property
    def do_debug(self):
        return self.level >= self.debug

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level < self.silent or level > self.debug:
            raise ValueError(
                "The level must be one of the ScreenLog attributes."
            )
        self._level = level

    def with_level(self, level):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                old_level = self.level
                self.level = level
                try:
                    result = fn(*args, **kwargs)
                finally:
                    self.level = old_level
                return result

            return wrapper

        return decorator

    def __call__(self, *words):
        # no logging for level 0
        if self.level == 0:
            return

        s = " ".join(w for w in words)
        if not self.do_warning:
            raise RuntimeError(
                "The runlevel should be at least warning when logging."
            )
        if not self._active:
            self.print_header()

        # Check for alignment code '&'
        pos = s.find("&")
        if pos == -1:
            lead = ""
            rest = s
        else:
            lead = s[:pos] + " "
            rest = s[pos + 1 :]
        width = self.width - len(lead)
        if width < self.width / 2:
            raise ValueError(
                "The lead may not exceed half the width of the terminal."
            )

        # Break and print the line
        first = True
        while len(rest) > 0:
            if len(rest) > width:
                pos = rest.rfind(" ", 0, width)
                if pos == -1:
                    current = rest[:width]
                    rest = rest[width:]
                else:
                    current = rest[:pos]
                    rest = rest[pos:].lstrip()
            else:
                current = rest
                rest = ""
            print(f"{lead}{current}", file=self._file)
            if first:
                lead = " " * len(lead)
                first = False

        self._last_blank = False

    def warn(self, *words):
        self.blank()
        text = f"!WARNING!&{' '.join(w for w in words)}"
        self(text)
        self.blank()

    def hline(self, char="~"):
        self(char * self.width)

    def center(self, *words, **kwargs):
        if len(kwargs) == 0:
            edge = ""
        elif len(kwargs) == 1:
            if "edge" not in kwargs:
                raise TypeError(
                    "Only one keyword argument is allowed, that is edge"
                )
            edge = kwargs["edge"]
        else:
            raise TypeError(
                "Too many keyword arguments. Should be at most one."
            )
        s = " ".join(w for w in words)
        if len(s) + 2 * len(edge) > self.width:
            raise ValueError(
                "Line too long. center method does not support wrapping."
            )
        self(f"{edge}{s.center(self.width - 2 * len(edge))}{edge}")

    def blank(self):
        if not self._last_blank:
            print(file=self._file)
            self._last_blank = True

    def deflist(self, l):
        widest = max(len(item[0]) for item in l)
        for name, value in l:
            self(f"  {name.ljust(widest)} :&{value}")

    def cite(self, reason, *key):
        if self._biblio is None:
            filename = context.get_fn("references.bib")
            self._biblio = Biblio(filename)
        self._biblio.cite(reason, *key)

    def progress(self, niter):
        # Only make the progress bar active at the medium level
        return ProgressBar(
            niter, self._file, self.width, silent=self.level != self.medium
        )

    def print_header(self):
        # Suppress any logging as soon as an exception is not caught.
        def excepthook_wrapper(type_, value, traceback_):
            self.level = self.silent
            sys.__excepthook__(type_, value, traceback_)

        sys.excepthook = excepthook_wrapper

        if self.do_warning and not self._active:
            self._active = True
            print(self.head_banner, file=self._file)
            self._print_basic_info()

    def print_footer(self):
        if self.do_warning and self._active:
            self._print_references()
            self._print_basic_info()
            self.timer._stop("Total")
            self.timer.report(self)
            print(self.foot_banner, file=self._file)

    def _print_references(self):
        if self._biblio is not None:
            self._biblio.log()

    def _print_basic_info(self):
        if self.do_low:
            self.blank()
            self(f"User:           &{getpass.getuser()}")
            self(f"Machine info:   &{' '.join(os.uname())}")
            self(f"Time:           &{datetime.datetime.now().isoformat()}")
            nl = "\n"
            self(f"Python version: &{sys.version.replace(nl, '')}")
            self(f"{self.name} version: &{self.version}")
            self(f"Current Dir:    &{os.getcwd()}")
            self(f"Command line:   &{' '.join(sys.argv)}")
            self(f"PyBEST module:  &{__file__}")
            self.blank()


class ProgressBar:
    def __init__(self, niter, f, width, silent):
        self.niter = niter
        self.f = f
        self.width = width
        self.silent = silent
        self.count = 0
        self.nchar = 0

    def __call__(self, inc=1):
        self.count += inc
        if not self.silent:
            new_nchar = (self.count * self.width) // self.niter
            if new_nchar > self.nchar:
                self.f.write(">" * (new_nchar - self.nchar))
                self.f.flush()
                self.nchar = new_nchar
            if self.count == self.niter:
                self.f.write("\n")
        elif self.count > self.niter:
            raise ValueError("Progress bar overflow.")


class Timer:
    def __init__(self):
        self.cpu = 0.0
        self._start = None
        # The _depth attribute is needed for timed recursive functions.
        self._depth = 0

    def start(self):
        if self._depth == 0:
            assert self._start is None
            self._start = time.perf_counter()
        self._depth += 1

    def stop(self):
        if self._depth > 0:
            assert self._start is not None
            self._depth -= 1
        if self._depth == 0:
            self.cpu += time.perf_counter() - self._start
            self._start = None


class SubTimer:
    def __init__(self, label):
        self.label = label
        self.total = Timer()
        self.own = Timer()

    def start(self):
        self.total.start()
        self.own.start()

    def start_sub(self):
        self.own.stop()

    def stop_sub(self):
        self.own.start()

    def stop(self):
        self.own.stop()
        self.total.stop()


class TimerGroup:
    def __init__(self):
        self.parts = {}
        self._stack = []
        self._start("Total")

    def reset(self):
        for timer_ in self.parts.values():
            timer_.total.cpu = 0.0
            timer_.own.cpu = 0.0

    @contextmanager
    def section(self, label):
        self._start(label)
        try:
            yield
        finally:
            self._stop(label)

    def with_section(
        self, label: str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                with self.section(label):
                    return fn(*args, **kwargs)

            return wrapper

        return decorator

    def _start(self, label):
        assert len(label) <= 20
        # get the right timer object
        timer_ = self.parts.get(label)
        if timer_ is None:
            timer_ = SubTimer(label)
            self.parts[label] = timer_
        # start timing
        timer_.start()
        if len(self._stack) > 0:
            self._stack[-1].start_sub()
        # put it on the stack
        self._stack.append(timer_)

    def _stop(self, label):
        timer_ = self._stack.pop(-1)
        assert timer_.label == label
        timer_.stop()
        if len(self._stack) > 0:
            self._stack[-1].stop_sub()

    def get_max_own_cpu(self):
        result = None
        for part in self.parts.values():
            if result is None or result < part.own.cpu:
                result = part.own.cpu
        return result

    def report(self, log_):
        max_own_cpu = self.get_max_own_cpu()
        # if max_own_cpu == 0.0:
        #    return
        log_.blank()
        log_("Overview of CPU time usage.")
        log_.hline()
        log_("Label                    Total     Own")
        log_.hline()
        bar_width = log_.width - 39
        for label, timer_ in sorted(self.parts.items()):
            # if timer.total.cpu == 0.0:
            #    continue
            if max_own_cpu > 0:
                cpu_bar = "W" * int(timer_.own.cpu / max_own_cpu * bar_width)
            else:
                cpu_bar = ""
            log_(
                f"{label.ljust(20):<20} {timer_.total.cpu:> 8.1f} {timer_.own.cpu:8.1f} "
                f"{cpu_bar.ljust(bar_width)}"
            )
        log_.hline()
        ru = resource.getrusage(resource.RUSAGE_SELF)
        log_.deflist(
            [
                ("CPU user time", f"{ru.ru_utime:10.2f}"),
                ("CPU sysem time", f"{ru.ru_stime:10.2f}"),
                ("Page swaps", f"{ru.ru_nswap:> 7}"),
            ]
        )
        log_.hline()


class Reference:
    def __init__(self, kind, key):
        self.kind = kind
        self.key = key
        self.tags = {}

    def get_url(self):
        if "doi" in self.tags:
            return f"http://dx.doi.org/{self.tags['doi']}"
        if "url" in self.tags:
            return self.tags["url"]
        return ""

    def format_text(self):
        if self.kind.lower() == "article":
            url = self.get_url()
            if len(url) > 0:
                url = f"; {url}"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}; {self.tags['journal']} "
                f"{self.tags['volume']}, {self.tags['pages']} ({self.tags['year']})"
                f"{url}"
            )
        if self.kind.lower() == "misc":
            url = self.get_url()
            if len(url) > 0:
                url = f"; {url}"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['title']))} "
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}; "
                f"({self.tags['year']}) "
                f"{url}"
            )
        if self.kind.lower() == "incollection":
            url = self.get_url()
            if len(url) > 0:
                url = f"; {url}"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}; {self.tags['booktitle']} "
                f"{self.tags['pages']}, ({self.tags['year']}),  "
                f"{(LatexNodes2Text().latex_to_text(self.tags['title']))} "
                f"{url}"
            )
        raise NotImplementedError

    def format_rst(self):
        if self.kind.lower() == "article":
            url = self.get_url()
            if len(url) > 0:
                url = f", `{url} <{url[:8] + urllib.parse.quote(url[8:])}>`_"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['title']))}. "
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}, *{self.tags['journal']}* "
                f"**{self.tags['volume']}**, {self.tags['pages']} ({self.tags['year']})"
                f"{url}"
            )
        if self.kind.lower() == "incollection":
            url = self.get_url()
            if len(url) > 0:
                url = f", `{url} <{url[:8] + urllib.parse.quote(url[8:])}>`_"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}; {self.tags['booktitle']} "
                f"{self.tags['pages']}, ({self.tags['year']}),  "
                f"{(LatexNodes2Text().latex_to_text(self.tags['title']))} "
                f"{url}"
            )
        if self.kind.lower() == "misc":
            url = self.get_url()
            if len(url) > 0:
                url = f", `{url} <{url[:8] + urllib.parse.quote(url[8:])}>`_"
            return (
                f"{(LatexNodes2Text().latex_to_text(self.tags['title']))}. "
                f"{(LatexNodes2Text().latex_to_text(self.tags['author'])).replace(' and', ';')}; "
                f"({self.tags['year']})"
                f"{url}"
            )
        raise NotImplementedError


class Biblio:
    def __init__(self, filename):
        self.filename = filename
        self._records = {}
        self._cited = {}
        self._done = set()
        self._load(filename)

    def _load(self, filename):
        with open(filename, encoding="utf8") as f:
            current = None
            for line in f:
                line = line[: line.find("%")].strip()
                if len(line) == 0:
                    continue
                if line.startswith("@"):
                    assert current is None
                    kind = line[line.find("@") + 1 : line.find("{")]
                    key = line[line.find("{") + 1 : line.find(",")]
                    current = Reference(kind, key)
                elif line == "}":
                    assert current is not None
                    self._records[current.key] = current
                    current = None
                elif current is not None:
                    tag = line[: line.find("=")].strip()
                    value = line[line.find("=") + 1 :].strip()
                    assert value[0] == "{"
                    assert value[-2:] == "}," or value[-1] == "}"
                    if value[-1] == "}":
                        value = value[1:-1]
                    else:
                        value = value[1:-2]
                    current.tags[tag] = value

    def cite(self, reason, *key):
        self._cited.setdefault(reason, tuple(key))

    def log(self):
        if log.do_low:
            log.hline("+")
            log.blank()
            log("Please, cite the following references:")
            log.hline()
            for reason, keys in sorted(self._cited.items()):
                log.blank()
                log(f" *&For {reason}")
                for key in keys:
                    log(f"   -&{self._records[key].format_text()}")
                    log.blank()
                log.blank()
            log.hline()
            log(f"Details can be found in the file {self.filename}")
            log.blank()
            log.hline("+")


class MemoryLogger:
    def __init__(self, log_):
        self._big = 0
        self.log = log_

    @staticmethod
    def _assign_unit(amount):
        unitKB = float(1024)
        unitMB = float(1024 * unitKB)
        unitGB = float(1024 * unitMB)

        if amount / unitGB > 1.0:
            unit = unitGB
            label = "GB"
        elif amount / unitMB > 1.0:
            unit = unitMB
            label = "MB"
        elif amount / unitKB > 1.0:
            unit = unitKB
            label = "KB"
        else:
            unit = 1
            label = "B"

        return unit, label

    def announce(self, amount):
        if self.log.do_debug:
            result = {}

            unit, label = self._assign_unit(amount)
            result["allc_val"] = amount / unit
            result["allc_lbl"] = label

            unit, label = self._assign_unit(self._big)
            result["cur_val"] = self._big / unit
            result["cur_lbl"] = label

            unit, label = self._assign_unit(self.get_rss())
            result["rss_val"] = self.get_rss() / unit
            result["rss_lbl"] = label

            self.log(
                f"Allocated:    {result['allc_val']: .3f} {result['allc_lbl']}s. "
                f"Current: {result['cur_val']: .3f} {result['cur_lbl']}s. "
                f"RSS: {result['rss_val']: .3f} {result['rss_lbl']}s"
            )
            self._big += amount
        if self.log.do_debug:
            traceback.print_stack()
            self.log.blank()

    def denounce(self, amount):
        if self.log.do_debug:
            result = {}

            unit, label = self._assign_unit(amount)
            result["allc_val"] = amount / unit
            result["allc_lbl"] = label

            unit, label = self._assign_unit(self._big)
            result["cur_val"] = self._big / unit
            result["cur_lbl"] = label

            unit, label = self._assign_unit(self.get_rss())
            result["rss_val"] = self.get_rss() / unit
            result["rss_lbl"] = label

            self.log(
                f"Deallocated:  {result['allc_val']: .3f} {result['allc_lbl']}s. "
                f"Current: {result['cur_val']: .3f} {result['cur_lbl']}s. "
                f"RSS: {result['rss_val']: .3f} {result['rss_lbl']}s"
            )
            self._big -= amount
        if self.log.do_debug:
            traceback.print_stack()
            self.log.blank()

    @staticmethod
    def get_rss():
        return (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * resource.getpagesize()
        )


head_banner = rf"""
====================================================================================================

 Welcome to

                                 ____        ____  _____ ____ _____
                                |  _ \ _   _| __ )| ____/ ___|_   _|
                                | |_) | | | |  _ \|  _| \___ \ | |
                                |  __/| |_| | |_) | |___ ___) || |
                                |_|    \__, |____/|_____|____/ |_|
                                       |___/

 version {__version__}!

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@        @@              @@@@@             #@@        @@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@            @@@       @@@       @@,       @@@           @@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@               @@@   @@           @@   @@@               @@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@                   @@@             @@@                   @@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@                     @@           @@                     @@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@                     @@,       @@@                     @@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@.                     @@@@@@@                     @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         @@\     @@\  @@@  @@@@@@      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         @  @    @  @     @   @        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          @@/ @ @ @@:  @@@ \@  @         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@           @    @  @  @       @ @          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@            @    @  @@/  @@@ @@/ @           @@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@                                                 @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@                                                   @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@                                                   @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@                       @@@                       @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@               @@@@@@@@@@@@@@&              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

 PyBEST is written and maintained at Nicolaus Copernicus University (NCU) in Torun.
 It contains contributions from (in alphabetic order)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         Developers                             Affiliation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Somayeh Ahmadkhani             Institute of Physics, NCU in Torun, Poland
 Saman Behjou                   Institute of Physics, NCU in Torun, Poland
 Katharina Boguslawski          Institute of Physics, NCU in Torun, Poland
 Iulia Brumboiu                 Institute of Physics, NCU in Torun, Poland
 Filip Brzęk                    Institute of Physics, NCU in Torun, Poland
 Rahul Chakraborty              Institute of Physics, NCU in Torun, Poland
 Kacper Cieślak                 Institute of Engineering and Technology, NCU in Torun, Poland
 Marta Gałyńska                 Faculty of Chemistry, NCU in Torun, Poland
 Antonina Dobrowolska           Institute of Engineering and Technology, NCU in Torun, Poland
 Seyedehdelaram Jahani          Institute of Physics, NCU in Torun, Poland
 Zahra Karimi                   Institute of Physics, NCU in Torun, Poland
 Dariusz Kędziera               Faculty of Chemistry, NCU in Torun, Poland
 Michał Kopczyński              Institute of Engineering and Technology, NCU in Torun, Poland
 Maximilian Kriebel             Institute of Physics, NCU in Torun, Poland
 Aleksandra Leszczyk            Institute of Physics, NCU in Torun, Poland
 Artur Nowak                    Institute of Physics, NCU in Torun, Poland
 Ram Dhari Pandey               Institute of Physics, NCU in Torun, Poland
 Julia Szczuczko                Institute of Engineering and Technology, NCU in Torun, Poland
 Lena Szczuczko                 Institute of Physics, NCU in Torun, Poland
 Emil Sujkowski                 Institute of Engineering and Technology, NCU in Torun, Poland
 Julian Świerczyński            Institute of Engineering and Technology, NCU in Torun, Poland
 Paweł Tecmer                   Institute of Physics, NCU in Torun, Poland
 Piotr Żuchowski                Institute of Physics, NCU in Torun, Poland
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
         Contributors                           Affiliation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 More information about PyBEST can be found on this website: https://hd.fizyka.umk.pl/~pybest/

 This log file allows you to track the progress of a calculation. It does not contain any data
 that can be used for restarting. Useful numerical data is written to checkpoint files during
 the calculation and can be accessed through the Python scripting interface.

===================================================================================================="""


foot_banner = rf"""
====================================================================================================

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@        @@              @@@@@           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@            @@@       @@@       @@,       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@               @@@   @@           @@   @@@      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@                   @@@             @@@               @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@                     @@           @@                  @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@                     @@,       @@@                   @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@.                     @@@@@@@                     @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         @@\     @@\  @@@  @@@@@@      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         @  @    @  @     @   @        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          @@/ @ @ @@:  @@@ \@  @         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@           @    @  @  @       @ @          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@            @    @  @@/  @@@ @@/ @           @@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@                                                 @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@                                                   @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@                                                   @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@                       @@@                       @@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@               @@@@@@@@@@@@@@&              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

 End of PyBEST. Program finished SUCCESSFULLY. Please read this output file carefully and watch out
 for possible WARNINGS!

 Thank you for using PyBEST {__version__}! See you soon!
===================================================================================================="""

timer: TimerGroup = TimerGroup()
log = ScreenLog("PyBEST", __version__, head_banner, foot_banner, timer)
atexit.register(log.print_footer)
