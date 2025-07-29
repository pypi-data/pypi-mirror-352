# brasciichart

Console ASCII line charts with Braille characters, no dependencies. 

## Install
```
$ pip install brasciichart
```

## Usage
```console
usage: brasciichart [-h] [-v] 
  [-s SERIES_ADD [SERIES_ADD ...]]
  [-c  [...]]
  [-f FORMAT] [-o OFFSET]
  [-H HEIGHT] [-W WIDTH]
  [-m MIN] [-M MAX]
  [series ...]

Console ASCII line charts with Braille characters.

positional arguments:
  series                float number series, "NaN" for null-values

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s SERIES_ADD [SERIES_ADD ...], --series SERIES_ADD [SERIES_ADD ...]
                        additional series
  -c  [ ...], --colors  [ ...]
                        available series colors: black, red, green, yellow,
                        blue, magenta, cyan, lightgray, default, darkgray,
                        lightred, lightgreen, lightyellow, lightblue,
                        lightmagenta, lightcyan, white
  -f FORMAT, --format FORMAT
                        format for tick numbers, default: "{:7.2f} "
  -o OFFSET, --offset OFFSET
                        chart area offset
  -H HEIGHT, --height HEIGHT
                        rows in chart area
  -W WIDTH, --width WIDTH
                        columns in chart area
  -m MIN, --min MIN     min y value
  -M MAX, --max MAX     max y value
```

```console
$ brasciichart --height 1 --offset 0 -s 1 2 3 4 3 2 1 2 3 4 3 2 1
⡠⠊⠢⡠⠊⠢⡀
```

```console
$ brasciichart --height 10 --min 0 --format '{:5.3f} ' \
  `rrdtool xport -s e-2month -e 20250518 --json \
    DEF:load1=system.rrd:system_load1:AVERAGE \
    XPORT:load1:"System Load 1 min average" \
  | jq -r '[.data[][]] | join(" ")'`
 0.024 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.021 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.019 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⡇
 0.016 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⣇
 0.013 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⢸⢸
 0.011 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⡎⡇⠀⠀⠀⠀⠀⠀⢸⢸
 0.008 ┤⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⣇⢀⡇⡇⠀⠀⠀⠀⠀⠀⢸⢸
 0.005 ┤⠀⢠⣀⣠⠳⡀⡀⠀⡏⡆⡔⢆⣸⢸⡎⡇⡇⡀⡄⣀⠔⠤⠲⣸⠘⡄⣀⠦⡄⢀⣀
 0.003 ┤⠉⠃⠁⠀⠀⠉⠈⠉⠀⠉⠀⠈⠙⠈⠀⠀⠘⠉⠈⠀⠀⠀⠀⠁⠀⠈⠀⠀⠈⠁
 0.000 ┼
```

```console
$ brasciichart --height 5 \
  `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done`
    1.00 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠊⠉⠉⠉⠒⠤⡀
    0.50 ┤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
    0.00 ┤⠈⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊
   -0.50 ┤⠀⠀⠈⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠉
   -1.00 ┤⠀⠀⠀⠀⠀⠉⠢⠤⣀⣀⣀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠒⠤⢄⣀⣀⡠⠤⠊⠁
```

```console
$ brasciichart -H 5 -W 30 -c red green \
  -s `for i in {-50..50..1}; do awk '{printf cos($1/10) " "}' <<< $i; done` \
  -s `for i in {-50..50..1}; do awk '{printf sin($1/10) " "}' <<< $i; done`
    1.00 ┤⠉⠉⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⢠⠔⠉⠉⠢⡤⠚⠉⠑⠦⡀
    0.50 ┤⡀⠀⠀⠈⢣⠀⠀⠀⠀⠀⠀⡔⠁⠀⠀⢀⠎⠈⢢⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⢀
    0.00 ┤⠘⡄⠀⠀⠀⠱⡀⠀⠀⢀⠜⠀⠀⠀⡠⠎⠀⠀⠀⠣⡀⠀⠀⠈⢆⠀⠀⠀⢠⠃
   -0.50 ┤⠀⠈⢣⠀⠀⠀⠑⢄⢠⠊⠀⠀⠀⡰⠁⠀⠀⠀⠀⠀⠑⡄⠀⠀⠀⢣⡀⡜⠁
   -1.00 ┤⠀⠀⠀⠑⢤⣀⡠⠜⠳⢄⣀⡤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⢄⣀⡤⠚⢦⣀⣀
```
