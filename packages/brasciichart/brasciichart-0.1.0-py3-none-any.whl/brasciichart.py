#!/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 cthulhu
"""Module to generate ascii charts.

This module provides a single function `plot` that can be used to generate an
ascii chart from a series of numbers with using braille font.
The chart can be configured via several options to tune the output.
"""
from __future__ import division

from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from collections import defaultdict, Counter
from math import ceil, floor, isnan, cos

black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
magenta = '\033[35m'
cyan = '\033[36m'
lightgray = '\033[37m'
default = '\033[39m'
darkgray = '\033[90m'
lightred = '\033[91m'
lightgreen = '\033[92m'
lightyellow = '\033[93m'
lightblue = '\033[94m'
lightmagenta = '\033[95m'
lightcyan = '\033[96m'
white = '\033[97m'
reset = '\033[0m'

__version__ = '0.1.0'
__all__ = [
    'plot', 'black', 'red',
    'green', 'yellow', 'blue',
    'magenta', 'cyan', 'lightgray',
    'default', 'darkgray', 'lightred',
    'lightgreen', 'lightyellow', 'lightblue',
    'lightmagenta', 'lightcyan', 'white', 'reset',
]

DEFAULT_FORMAT = '{:7.2f} '


def _isnum(n):
    return n is not None and not isnan(n)


def colored(char, color):
    if not color or color == reset:
        return char
    else:
        return color + char + reset


class Pixels(list):
    def __init__(self, width, height):
        super().__init__(
            [defaultdict(list) for _ in range(width)]
            for _ in range(height))

    @staticmethod
    def iterline(x1, y1, x2, y2):
        xdiff = abs(x2 - x1)
        ydiff = abs(y2 - y1)
        xdir = 1 if x1 <= x2 else -1
        ydir = 1 if y1 <= y2 else -1

        r = ceil(max(xdiff, ydiff))
        if r == 0:  # point, not line
            yield x1, y1
        else:
            x, y = floor(x1), floor(y1)
            i = 0
            while i < r:
                x += xdir * xdiff / r  # with floating point can be > x2
                y += ydir * ydiff / r  #

                yield x, y
                i += 1

    def getAttr(self, x, y) -> str:
        r = self[y][x]
        if not r:
            return ''
        c = [(len(vals), vals, attr)
             for attr, vals in r.items() if attr]
        if not c:
            return ''
        _, _, attr = max(c)
        return attr

    def plotpixel(self, x, y, attr, val=None):
        self[y][x][attr].append(val)

    def plotline(self, x1, y1, x2, y2, attr, val=None):
        prev_x, prev_y = None, None
        for x, y in self.iterline(x1, y1, x2, y2):
            if x != prev_x or y != prev_y:
                self.plotpixel(round(x), round(y), attr, val)


def plot(series, cfg=None):
    """Generate an ascii chart for a series of numbers.

    `series` should be a list of ints or floats. Missing data values in the
    series can be specified as a NaN. In Python versions less than 3.5, use
    float("nan") to specify an NaN. With 3.5 onwards, use math.nan to specify a
    NaN.

    >>> series = [cos(n / 10) for n in range(-50, 50, 1)]
    >>> print(plot(series, {'height': 5}))
        1.00 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠊⠉⠉⠉⠒⠤⡀
        0.50 ┤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢄
        0.00 ┤⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊
       -0.50 ┤⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉
       -1.00 ┤⠀⠀⠀⠀⠀⠉⠢⠤⣀⣀⣀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠒⠤⢄⣀⣀⡠⠤⠊⠁

    >>> series = [1, 2, 3, 4, float("nan"), 4, 3, 2, 1]
    >>> print(plot(series))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⢸⠀⠀⢸
        1.00 ┤⡎⠀⠀⠈⡆

    `series` can also be a list of lists to support multiple data series.

    >>> series = [[10, 20, 30, 40, 30, 20, 10], [40, 30, 20, 10, 20, 30, 40]]
    >>> print(plot(series, {'height': 3}))
       40.00 ┤⢇⡜⣄⠇
       25.00 ┤⢸⡇⣿
       10.00 ┤⡎⢣⠋⡆

    `cfg` is an optional dictionary of various parameters to tune the appearance
    of the chart. `min` and `max` will clamp the y-axis and all values:

    >>> series = [1, 2, 3, 4, float("nan"), 4, 3, 2, 1]
    >>> print(plot(series, {'min': 0}))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⢸⠀⠀⢸
        1.00 ┤⠇⠀⠀⠀⠇
        0.00 ┼

    >>> print(plot(series, {'min': 2}))
        4.00 ┤⠀⡸⠸⡀
        3.00 ┤⠀⡇⠀⡇
        2.00 ┤⣰⠁⠀⢸⡀

    >>> print(plot(series, {'min': 2, 'max': 3}))
        3.00 ┤⠀⡏⠈⡇
        2.00 ┤⣸⠀⠀⢸⡀

    `height` specifies the number of rows the graph should occupy. It can be
    used to scale down a graph with large data values:

    >>> series = [10, 20, 30, 40, 50, 40, 30, 20, 10]
    >>> print(plot(series, {'height': 5}))
       50.00 ┤⠀⢀⢇
       40.00 ┤⠀⡸⠸⡀
       30.00 ┤⠀⡇⠀⡇
       20.00 ┤⢸⠀⠀⢸
       10.00 ┤⡎⠀⠀⠈⡆

    `width` specifies the number of columns the graph should occupy. It can be
    used to scale down a graph with large data values:

    >>> series = [cos(n / 10) for n in range(-50, 50, 1)]
    >>> print(plot(series, {'height': 5, 'width': 10}))
        1.00 ┤⠀⠀⠀⠀⡜⢳
        0.50 ┤⡀⠀⠀⢰⠁⠈⡇
        0.00 ┤⢣⠀⠀⡸⠀⠀⢣⠀⠀⡸
       -0.50 ┤⠘⡄⢀⠇⠀⠀⠘⡄⢀⠇
       -1.00 ┤⠀⢧⡼⠀⠀⠀⠀⢣⡼

    >>> series = [[10, 20, 30, 40, 30, 20, 10], [40, 30, 20, 10, 20, 30, 40]]
    >>> print(plot(series, {'height': 3, 'width': 30}))
       40.00 ┤⠉⠒⠤⢄⡀⠀⠀⠀⠀⠀⠀⣀⠤⠔⠊⠉⠒⠤⣀⠀⠀⠀⠀⠀⠀⢀⡠⠤⠒⠉
       25.00 ┤⠀⠀⠀⠀⢈⣉⠶⠶⠶⢎⣉⠀⠀⠀⠀⠀⠀⠀⠀⣉⡱⠶⠶⠶⣉⡁
       10.00 ┤⣀⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠉⠒⠢⢄⣀⠤⠒⠉⠀⠀⠀⠀⠀⠀⠈⠑⠒⠤⣀

    `format` specifies a Python format string used to format the labels on the
    y-axis. The default value is "{:7.2f} ". This can be used to remove the
    decimal point:

    >>> series = [-10, 20, 30, 40, 50, 40, 30, 20, -10]
    >>> print(plot(series, {'height': 5, 'format':'{:8.0f} '}))
           50 ┤⠀⢠⢣
           35 ┤⠀⡎⠈⡆
           20 ┤⢸⠀⠀⢸
            5 ┤⡜⠀⠀⠸⡀
          -10 ┤⡇⠀⠀⠀⡇
    """
    if len(series) == 0:
        return ''

    if not isinstance(series[0], list):
        if all(isnan(n) for n in series):
            return ''
        else:
            series = [series]

    cfg = cfg or {}
    minimum = cfg.get('min', min(filter(_isnum, [y for s in series for y in s])))
    maximum = cfg.get('max', max(filter(_isnum, [y for s in series for y in s])))
    if minimum > maximum:
        raise ValueError('The min value cannot exceed the max value.')

    interval = maximum - minimum
    offset = cfg.get('offset', 3)
    height = cfg.get('height', ceil(interval) + 1)
    height = int((height or 1) * 4)
    ratio = ((height - 1) or 1) / (interval or 1)

    colors = cfg.get('colors', [reset])
    symbols = cfg.get('symbols', ['┼', '┤'])

    def scaled_y(y):
        y = min(max(y, minimum), maximum)
        return int(round((y - minimum) * ratio))

    series_width = 0
    for i in range(0, len(series)):
        series_width = max(series_width, len(series[i]))
    width = cfg.get('width')
    width = width * 2 if width else series_width
    xratio = (width - 1) / (series_width - 1 or 1)
    width += width % 2

    def scaled_x(x):
        return int(round(x * xratio))

    pixels = Pixels(width, height)

    polylines = []
    for s, ser in enumerate(series):
        prev_y = None
        for x, y in enumerate(ser):
            attr = colors[s] if len(colors) > s else reset
            if _isnum(y):
                if not _isnum(prev_y):
                    polylines.append(([(x, y)], attr, y))
                else:
                    polylines.append(([(x - 1, prev_y), (x, y)], attr, y))
            prev_y = y

    for vertexes, attr, row in polylines:
        if len(vertexes) == 1:  # single point
            x, y = vertexes[0]
            pixels.plotpixel(scaled_x(x),
                             height - scaled_y(y) - 1, attr, row)
            continue

        prev_x, prev_y = vertexes[0]
        for x, y in vertexes[1:]:
            x1 = scaled_x(prev_x)
            y1 = height - scaled_y(prev_y) - 1
            x2 = scaled_x(x)
            y2 = height - scaled_y(y) - 1
            pixels.plotline(x1, y1, x2, y2, attr, row)
            prev_x, prev_y = x, y

    result = [[' '] * offset + [chr(0x2800)] * (width // 2)
              for _ in range(height // 4)]

    # axis and labels
    if offset > 0:
        fmt = cfg.get('format', DEFAULT_FORMAT)
        func = cfg.get('format_func', None)
        for y in range(height // 4):
            mark = maximum - y * (interval / (((height - 1) // 4) or 1))
            label = fmt.format(func(mark) if func else mark)
            result[y][max(offset - 2, 0)] = label
            result[y][max(offset - 1, 0)] = symbols[1] if mark else symbols[0]

    for y in range(height // 4):
        for x in range(width // 2):
            # @formatter:off
            block_attrs = [
                pixels.getAttr(x * 2,     y * 4),
                pixels.getAttr(x * 2,     y * 4 + 1),
                pixels.getAttr(x * 2,     y * 4 + 2),
                pixels.getAttr(x * 2 + 1, y * 4),
                pixels.getAttr(x * 2 + 1, y * 4 + 1),
                pixels.getAttr(x * 2 + 1, y * 4 + 2),
                pixels.getAttr(x * 2,     y * 4 + 3),
                pixels.getAttr(x * 2 + 1, y * 4 + 3),
            ]
            # @formatter:on
            braille_num = sum(int(bool(attr)) * (1 << i)
                              for i, attr in enumerate(block_attrs))
            if braille_num:
                ch = chr(0x2800 + braille_num)
                c = Counter(c for c in block_attrs if c).most_common(1)[0][0]
                result[y][x + offset] = colored(ch, c)

    return '\n'.join([''.join(row).rstrip(chr(0x2800)) for row in result])


COLORS = {
    'black': black,
    'red': red,
    'green': green,
    'yellow': yellow,
    'blue': blue,
    'magenta': magenta,
    'cyan': cyan,
    'lightgray': lightgray,
    'default': default,
    'darkgray': darkgray,
    'lightred': lightred,
    'lightgreen': lightgreen,
    'lightyellow': lightyellow,
    'lightblue': lightblue,
    'lightmagenta': lightmagenta,
    'lightcyan': lightcyan,
    'white': white,
}


class SeriesAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not getattr(namespace, 'series_add', None):
            setattr(namespace, 'series_add', [])
        namespace.series_add.append(list(map(float, values)))


class ColorsAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not getattr(namespace, 'colors', None):
            setattr(namespace, 'colors', [])
        namespace.colors += list(map(lambda c: COLORS[c], values))


def argparse():
    parser = ArgumentParser(
        prog='brasciichart',
        formatter_class=RawDescriptionHelpFormatter,
        description='Console ASCII line charts with Braille characters.')

    parser.add_argument(
        '-v', '--version', action='version',
        version=f'brasciichart {__version__}')
    parser.add_argument(
        'series', type=float, nargs='*',
        help='float number series, "NaN" for null-values')
    parser.add_argument(
        '-s', '--series', action=SeriesAction, type=float, nargs='+',
        dest='series_add', help='additional series')
    parser.add_argument(
        '-c', '--colors', action=ColorsAction, nargs='+', metavar='',
        choices=COLORS.keys(),
        help='available series colors:'
             ' black, red, green, yellow, blue, magenta, cyan, lightgray,'
             ' default, darkgray, lightred, lightgreen, lightyellow, lightblue,'
             ' lightmagenta, lightcyan, white')
    parser.add_argument(
        '-f', '--format', default=DEFAULT_FORMAT,
        help='format for tick numbers')
    parser.add_argument('-o', '--offset', type=int, help='chart area offset')
    parser.add_argument('-H', '--height', type=int, help='rows in chart area')
    parser.add_argument('-W', '--width', type=int, help='columns in chart area')
    parser.add_argument('-m', '--min', type=float, help='min y value')
    parser.add_argument('-M', '--max', type=float, help='max y value')

    parser.epilog = """
Example:
./brasciichart.py --height 2 --offset 0 \\
  `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done`
Output:
⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠔⠒⠊⠉⠉⠉⠉⠉⠒⠒⠤⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀
⠀⠈⠉⠒⠢⠤⠤⣀⣀⣀⣀⣀⡠⠤⠔⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠤⠤⣀⣀⣀⣀⣀⡠⠤⠤⠒⠊⠉
"""
    return parser


def main():
    parser = argparse()
    args = vars(parser.parse_args())
    series = args.pop('series')
    series_add = args.pop('series_add')
    if not series and not series_add:
        parser.print_help()
        exit(1)
    series = ([series] if series else []) + (series_add or [])
    cfg = {k: v for k, v in args.items() if v is not None}
    print(plot(series, cfg))


if __name__ == '__main__':
    main()
