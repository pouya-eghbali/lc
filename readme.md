# lc

`lc` is `ls` but with colors and icons.

![lc screenshot](https://github.com/pouya-eghbali/lc/raw/master/lc.png)

## Install

To install do

```
pip install lcls
```

## Usage

The executable is named `lcls` to prevent conflicts with `ls` and mono `lc`, you can make an alias and name it however you want.

```
lcls -[al] [directory]
```

Multiple directories can be provided. Currently lc recognizes `-a` and `-l` options.
Directory is optional (defaults to current working directory)

## Configuration

`lc` first tries to read `~/.lc.rules.yaml` and if it fails it will load the default configuration from where it is installed.

To customize icons and colors you can copy `.lc.rules.yaml` to your home folder and modify its contents.

For color, either provide a [number (8bit color number)](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit),
a list of numbers (rgb), or the color name.

## Dependencies

You need nerd fonts (or equivalent) to make this work properly. Python dependencies are `sty` and `ruamel.yaml`
