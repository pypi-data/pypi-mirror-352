# vikinglotto-generator

This program can generate a set of randomly picked lottery numbers 
for [Vikinglotto](https://en.wikipedia.org/wiki/Vikinglotto)
and [Eurojackpot](https://en.wikipedia.org/wiki/Eurojackpot).

The program's output supports showing the result using `cowsay` for added fun.
The generated numbers are stored in a log file and can be reviewed if necessary. 

![Demo](./img/demo.png)

[中文说明](./README_CN.md)

## Requirements

If you need the program to display the results as `cowsay`, you need to have `cowsay` installed on your system.

Take Debian & Ubuntu as an example:

```bash
sudo apt update
sudo apt install cowsay -y
```

## Installation

Use `pip`:

```
python3 -m pip install vikinglotto
```

## Usage

Run the program in `cowsay` mode:

```bash
vikinglotto
```

Without using `cowsay`, print the result directly:

```bash
vikinglotto --plain
```

Generate numbers for Eurojackpot:

```bash
vikinglotto --euro
```
