### Columnate

This script is designed to prettify columnar data for easier readability. 

Installation: 

1. Clone this repo
2. Move columnate to your bin path ~/bin or /usr/local/bin/ or wherever you want
3. Move the directory rae/ to your python library path
        - This could be /usr/local/lib/python2.7/site-packages/ or something like that
4. Update your python path to include this library directory if it's not already included   by putting this in your .bashrc file
       - export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH


usage: columnate [OPTION]... [FILE]...

positional arguments:
  FILE                  Filename to read; default=STDIN

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -a, --ascii           ASCII (non-Unicode) table
  -b 1-5,10-15,..., --bytes 1-5,10-15,...
                        specify columns by fixed byte positions; use a
                        trailing "-" or "+" to include all remaining bytes
  -c 1,3+5,6-9,..., --columns 1,3+5,6-9,...
                        show specified columns only; use "x+y+..." or "x-y" to
                        merge two or more columns, or a trailing "-" or "+" to
                        merge all remaining columns
  --header H1,H2,...    column headers
  -i, --ignore          ignore parsing errors; see -p
  -n, --no-borders      no ConsoleTable borders; see --pad
  -p, --partial         add partial rows that did not parse; implies -i
  --pad PAD             pad character(s) for -n; default=' '
  --properties PROP=VAL1[:[:]VAL2],...
                        table, row, and column properties (colors and
                        justification) passed directly to ConsoleTable
  -s PATTERN, --separator PATTERN
                        PATTERN that separates columns; default='\s+'
  -t TITLE, --title TITLE
                        title of the table
  -w, --whitespace      strip leading and trailing whitespace from column data
  -x 2,4,..., --exclude 2,4,...
                        exclude (skip) these columns

Options -b, -c, and -x are mutually exclusive.

See opening code comments for '--properties' examples.
