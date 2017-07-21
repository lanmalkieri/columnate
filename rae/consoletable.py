#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------#
#                                                                           #
#                 Rick Esterling <rickest@hotspringsmt.net>                 #
#                Copyright 2001 - 2016, All Rights Reserved                 #
#                                                                           #
#---------------------------------------------------------------------------#
# The 'coding' comment following the shebang above is required by the       #
# python interpreter since this file contains unicode characters.           #
#                                                                           #
#---------------------------------------------------------------------------#
# Notes:                                                                    #
#                                                                           #
# Tables can have a title (set in the constructor) and/or a header row      #
# (set in the constructor or add_header()), and multiple rows of data. The  #
# title row can be centered (default), left-, or right-justified; set in    #
# the constructor as tjustify. Headers have the same options, set with      #
# hjustify in the constructor.                                              #
#                                                                           #
# Colors for the whole table, columns, or rows can be set in order of       #
# increasing precedence.                                                    #
#                                                                           #
#     Element             Set by                                            #
#     ---------------     ------------------                                #
#     tcolor (title)      constructor                                       #
#     hcolor (header)     constructor                                       #
#     color               constructor                                       #
#     column              set_col_property()                                #
#     row                 add_row()                                         #
#                                                                           #
# If specified, these values must be the ANSI codes (numbers and semi-      #
# colons only) for the preferred color; i.e., '34', '38;5;93'               #
#                                                                           #
# set_col_property() sets properties for any given column. Valid            #
# properties are 'justify' ('center', 'left', 'right'), 'color', and        #
# 'bgcolor'.                                                                #
#                                                                           #
# Row properties are set during the call to add_row(row, props).            #
# Properties defined in this manner apply to the whole the row, including   #
# rows with embedded newlines. Valid properties are 'color' and 'bgcolor'.  #
#                                                                           #
# Normal cells may have newlines but headers and title may not.             #
#                                                                           #
# Word-wrapping must be provided by the caller.                             #
#                                                                           #
# rpad and lpad are part of the centering calculations. This means if you   #
# set lpad='     ', and rpad='', centered text will be skewed to the right  #
# even though you cannot visibly tell why.                                  #
#                                                                           #
# If the dataset is empty, nothing is output even if --heading and --title  #
# are set. It's debatable that someone would want those printed anyway; if  #
# so, change draw() accordingly.                                            #
#                                                                           #
#---------------------------------------------------------------------------#

import sys

# Default column properties.
DEF_COL_PROP_JUSTIFY = 'left'

#---------------------------------------------------------------------------#
# ConsoleTable                                                              #
#---------------------------------------------------------------------------#
class ConsoleTable(object):
    '''Not quite ready-for-prime-time console Table drawer.

    The table consists of an optional title row (a single full-width
    column), an optional header row, and one or more rows of data, each
    column of which is separated by vertical bars.

    By default, unicode characters are used to draw the table and data
    is highlighted in blue, but both of these options can be disabled
    via the constructor.
    '''
    #-----------------------------------------------------------------------#
    # __init__                                                              #
    #-----------------------------------------------------------------------#
    def __init__(self, 
                 title='', 
                 header=(),
                 tcolor='',
                 hcolor='',
                 color='',
                 utf8=True, 
                 strip_empty_trailing_cols=True,
                 line_separators=False, 
                 tjustify='center',
                 # This default is 'center' for normal tables, 'left'
                 # for no_borders. Therefore, set it dynamically below
                 # based on input and border[less] mode.
                 hjustify='',
                 lpad=' ', 
                 rpad=' ', 
                 vert='|', 
                 horz='-', 
                 horz_dbl='=', 
                 connector='+',
                 no_borders=False,
                 # No-borders padding
                 nb_pad=' '):
        '''The line-drawing arguments in this constructor only apply to
        ASCII tables, not utf8. rpad and lpad apply to both.
        '''
        self.rows = []
        self.rows_props = []
        self.cols_max_width = [0]
        self.cols_props = []
        self.last_col_idx = 0
        self.width = 0
        self.no_borders = no_borders
        self.nb_pad = nb_pad
        if no_borders:
            self.hjustify = hjustify if hjustify else 'left'
            utf8 = False
            horz = ''
            vert = ''
            connector = ''
            self.lpad = ''
            self.rpad = ''
        else:
            self.hjustify = hjustify if hjustify else 'center'
            self.lpad = lpad
            self.rpad = rpad
        self.title = title
        # If header was passed, self.header will be set in the call to
        # add_header() below.
        self.header = ()
        self.strip_empty_trailing_cols = strip_empty_trailing_cols
        self.line_separators = line_separators
        if tjustify not in ('left', 'right', 'center'):
            sys.stderr.write('ConsoleTable: Invalid value \'' + tjustify +
                '\' for tjustify in constructor.\n')
            sys.exit(1)
        self.tjustify = tjustify
        if not no_borders and self.hjustify not in ('left', 'right', 'center'):
            sys.stderr.write('ConsoleTable: Invalid value \'' + 
                self.hjustify + '\' for hjustify in constructor.\n')
            sys.exit(1)
        # ANSI colors.
        if color:
            self.color_on = '\x1b[' + color + 'm'
            self.color_off = '\x1b[0m'
        else:
            self.color_on = ''
            self.color_off = ''
        if tcolor:
            self.tcolor_on = '\x1b[' + tcolor + 'm'
            self.tcolor_off = '\x1b[0m'
        else:
            self.tcolor_on = ''
            self.tcolor_off = ''
        if hcolor:
            self.hcolor_on = '\x1b[' + hcolor + 'm'
            self.hcolor_off = '\x1b[0m'
        else:
            self.hcolor_on = ''
            self.hcolor_off = ''
        if (utf8):
            # Universal
            self.horz = u'\u2500'               # ─
            self.horz_connector = u'\u253c'     # ┼
            self.horz_dbl_connector = u'\u256a' # ╪ 
            self.horz_dbl = u'\u2550'           # ═
            self.vert = u'\u2502'               # │
            # North single
            self.nw = u'\u250c'                 # ┌
            self.n_connector = u'\u252c'        # ┬
            self.ne = u'\u2510'                 # ┐
            # North double
            self.nw_dbl = u'\u2552'             # ╒
            self.n_dbl_connector = u'\u2564'    # ╤
            self.ne_dbl = u'\u2555'             # ╕
            # West
            self.w_connector = u'\u251c'        # ├
            self.w_dbl_connector = u'\u255e'    # ╞
            self.sw_dbl_connector = u'\u2558'   # ╘
            # East
            self.e_connector = u'\u2524'        # ┤
            self.e_dbl_connector = u'\u2561'    # ╡
            self.se_dbl_connector = u'\u255b'   # ╛
            # South double
            self.s_dbl_connector = u'\u2567'    # ╧
            # South single
            self.sw = u'\u2514'                 # └
            self.se = u'\u2518'                 # ┘
            self.s_connector = u'\u2534'        # ┴
        else:
            # Universal
            self.horz = horz
            self.horz_connector = connector
            self.horz_dbl_connector = connector
            self.horz_dbl = horz_dbl
            self.vert = vert
            # North single
            self.nw = connector
            self.n_connector = connector
            self.ne = connector
            # North double
            self.nw_dbl = connector
            self.n_dbl_connector = connector
            self.ne_dbl = connector
            # West
            self.w_connector = connector
            self.w_dbl_connector = connector
            # East
            self.e_connector = connector
            self.e_dbl_connector = connector
            # South single
            self.sw = connector
            self.se = connector
            self.s_connector = connector
            # South double
            self.sw_dbl_connector = connector
            self.se_dbl_connector = connector
            self.s_dbl_connector = connector
        if header:
            self.add_header(header)

    #-----------------------------------------------------------------------#
    # __repr__                                                              #
    #-----------------------------------------------------------------------#
    def __repr__(self):
        return("<ConsoleTable('" + self.title + "')>")

    #-----------------------------------------------------------------------#
    # add_header                                                            #
    #-----------------------------------------------------------------------#
    def add_header(self, row):
        if self.header:
            sys.stderr.write('\nCannot add multiple headers, exiting.\n')
            sys.exit(1)
        self.header = row
        self.__add_row(self.header, None, True)

    #-----------------------------------------------------------------------#
    # add_row                                                               #
    #-----------------------------------------------------------------------#
    def add_row(self, row, props=None):
        self.__add_row(row, props, False)

    #-----------------------------------------------------------------------#
    # add_line_separator                                                    #
    #-----------------------------------------------------------------------#
    def add_line_separator(self, style='single'):
        """'style' controls which type of line-break to draw. 
        
        Valid choices are:
            n_title             # ╒═════════════════════════════════════════╕

            n_header            # ╒════════════════╤════════╤═══════╤═══════╕

            s_header_final      # ╘════════════════╧════════╧═══════╧═══════╛

            north               # ┌────────────────┬────────┬───────┬───────┐

            s_title             # ╞════════════════╤════════╤═══════╤═══════╡
            
            s_title_final       # ╘═════════════════════════════════════════╛

            double              # ╞════════════════╪════════╪═══════╪═══════╡

            single              # ├────────────────┼────────┼───────┼───────┤

            south               # └────────────────┴────────┴───────┴───────┘
            """
        self.rows.append(['__LINE_SEPARATOR__', style])
        self.rows_props.append(None)

    #-----------------------------------------------------------------------#
    # draw                                                                  #
    #-----------------------------------------------------------------------#
    def draw(self):
        '''Having collected all the data for this table, draw it.'''
        table = ''
        # Check for empty data sets.  There are four checks because of 
        # the difference between:
        #   # This creates one empty row because of the newline.
        #   echo | columnate
        #   # This command prints an error to STDERR and nothing (not
        #   # even a newline) to STDOUT
        #   this_cmd_doesnt_even_newline | columnate
        if (len(self.rows) == 0 or
                (len(self.rows) == 1 and self.header) or
                (len(self.rows) == 1 and not self.header and 
                    len(self.rows[0]) == 1 and len(self.rows[0][0]) == 0) or
                (len(self.rows) == 2 and self.header and 
                    len(self.rows[1]) == 1 and len(self.rows[1][0]) == 0)):
            return('')
        self.__pad_columns()
        self.__compute_last_col_idx()
        self.__set_default_col_props()
        self.__compute_width()
        # If line_separators are on, there may be an extra one at
        # the end of self.rows; remove it.
        if self.line_separators and self.rows[-1][0] == '__LINE_SEPARATOR__':
            self.rows.pop()
        if self.title: 
            table = self.__draw_title()
        elif self.rows and not self.header: 
            table = self.__draw_line_separator('north')
        for nr, row in enumerate(self.rows):
            color_on = ''
            color_off = ''
            # These 'static' variables allow for color setting
            # precedence as follows:
            #   contructor color for all rows
            #   set_col_property()
            #   add_row([...], {'color': '30'})
            # So, if add_row sets a color for a given row, that setting
            # has the highest precedence. If not, the property for any
            # given column has priority. If that's not set, use the
            # default global color specified in the constructor.
            color_static = False
            color_bg_static = False
            if row[0] == '__LINE_SEPARATOR__':
                table += self.__draw_line_separator(row[1])
            else:
                if nr == 0 and self.header:
                    color_on = self.hcolor_on
                    color_off = self.hcolor_off
                    if not self.title:
                        table += self.__draw_line_separator('n_header')
                else:
                    color_on = self.color_on
                    color_off = self.color_off
                if self.rows_props[nr]:
                    if 'color' in self.rows_props[nr]:
                        color_on = '\x1b[' + self.rows_props[nr]['color'] + 'm'
                        color_off = '\x1b[0m'
                        color_static = True
                    if 'bgcolor' in self.rows_props[nr]:
                        color_on += '\x1b[' + self.rows_props[nr]['bgcolor'] + 'm'
                        color_off = '\x1b[0m'
                        color_bg_static = True
                table += self.__draw_row(row, color_on, color_off, 
                        color_static, color_bg_static,
                        nr == 0 and self.header) + '\n'
                if self.header and nr == 0:
                    if len(self.rows) > 1:
                        table += self.__draw_line_separator('double')
                    else:
                        table += self.__draw_line_separator('s_header_final')
        if self.no_borders:
            # For no_borders, strip the last newline added since there
            # won't be one more line_separator as there would be with
            # borders.
            table = table[:-1]
        # Titles and Headers add their own trailing line separator.
        # Therefore, we only need to add a trailing separator to the
        # whole table if there were actual rows of data (not just title
        # or header), hence this check.
        elif (self.header and len(self.rows) > 1) or \
                (not self.header and len(self.rows) > 0):
            table += self.__draw_line_separator('south')
        return table.encode('utf-8')

    #-----------------------------------------------------------------------#
    # __add_row                                                             #
    #-----------------------------------------------------------------------#
    def __add_row(self, row, props=None, is_header=False):
        '''Add a row one column at a time.

        If the width of any column is a new maximum width for that column, 
        record it in self.cols_max_width.
        '''
        row_new = []
        row_new_multiline = []
        for idx, col in enumerate(row):
            lines = col.split('\n', 1)
            try:
                row_new_multiline.append(lines[1])
            except IndexError, e:
                row_new_multiline.append('')
            col = lines[0]
            col_width = len(col.decode('utf-8'))
            row_new.append(col)
            # An exception will be thrown if cols_max_width[idx] is
            # undefined; i.e., the first check for each column.
            try:
                if col_width > self.cols_max_width[idx]:
                    self.cols_max_width[idx] = col_width
            except IndexError:
                self.cols_max_width.append(col_width)
        if is_header:
            self.rows.insert(0, row_new) 
            self.rows_props.insert(0, props)
        else:
            self.rows.append(row_new)
            self.rows_props.append(props)
        for cols in row_new_multiline:
            if len(cols):
                self.add_row(row_new_multiline, props)
                break
        else:
            if self.line_separators and not is_header:
                self.add_line_separator()

    #-----------------------------------------------------------------------#
    # __compute_last_col_idx                                                #
    #-----------------------------------------------------------------------#
    def __compute_last_col_idx(self):
        '''Find the last column that contains non-null data in all rows.

        Some data sets may contain a number columns where the last
        column only rarely contains data. If the last column does not
        contain data for any given data set and if set
        strip_empty_trailing_cols is True (default), only show n-1
        columns. Note: columns headers count as non-empty cells.
        '''
        if self.strip_empty_trailing_cols:
            self.last_col_idx = len(self.rows[0])
            for idx in reversed(range(len(self.cols_max_width))):
                if self.cols_max_width[idx] != 0:
                    self.last_col_idx = idx
                    break
        else:
            self.last_col_idx = len(self.cols_max_width) - 1

    #-----------------------------------------------------------------------#
    # __compute_width                                                       #
    #-----------------------------------------------------------------------#
    def __compute_width(self):
        '''The title could be wider than all columns of the widest row
        combined. If so, pad the last column of each row with spaces to
        match the title's width.'''
        # One for each margin (border) and one for each each bar that
        # separates the columns...
        width = 2 + self.last_col_idx
        # ...plus the maximum width of each column, plus the length of
        # lpad and rpad in each cell.
        for i in range(self.last_col_idx + 1):
            width += (self.cols_max_width[i] + len(self.rpad) + 
                len(self.lpad))
        # If the title is wider than all the columns combined, increase
        # the recorded width of the last column for each row until they
        # all match the width of the title. This also makes centering
        # happen correctly.
        # The trailing 2 accounts for the left/right borders.
        h_width = len(self.lpad) + len(self.title) + len(self.rpad) + 2
        if width < h_width:
            # Set last cols_max_width 
            self.cols_max_width[self.last_col_idx] += (h_width - width)
            # Increment total width
            width += (h_width - width)
        self.width = width

    #-----------------------------------------------------------------------#
    # __draw_title                                                          #
    #-----------------------------------------------------------------------#
    def __draw_title(self):
        '''Draw a separator line, the title, then another separator line
        with connectors at each column.'''
        title = self.title.decode('utf-8')
        # Padding to center the title. The '-2' is to account for the
        # table border characters.
        lpad = 0
        rpad = 0
        if self.tjustify == 'center':
            lpad, mod = divmod(self.width - len(title) - 
                    len(self.lpad) - len(self.rpad) - 2, 2)
            rpad = lpad
            if mod:
                rpad += 1
        elif self.tjustify == 'left':
            rpad = (self.width - len(title) - len(self.lpad) - 
                len(self.rpad) - 2)
        else:
            lpad = (self.width - len(title) - len(self.lpad) -
                len(self.rpad) - 2)
        title = (self.__draw_line_separator('n_title') +
            (self.vert + self.lpad + 
                self.tcolor_on +
                (' ' * lpad) +
                title + 
                (' ' * rpad) +
                self.tcolor_off +
                self.rpad + self.vert + '\n'))
        if self.header or self.rows:
            title += self.__draw_line_separator('s_title')
        else:
            title += self.__draw_line_separator('s_title_final')
        return title

    #-----------------------------------------------------------------------#
    # __draw_line_separator                                                 #
    #-----------------------------------------------------------------------#
    def __draw_line_separator(self, style='single'):
        '''Draw a separator line in between rows.  See add_line_separator()
        for details.'''
        if self.no_borders:
            return('')
        if style == 'n_title' or style == 'n_header':
            west = self.nw_dbl
            horz = self.horz_dbl
            east = self.ne_dbl
            if style == 'n_title':
                connector = self.horz_dbl
            else:
                connector = self.n_dbl_connector
        elif style == 's_title' or style == 's_title_final':
            horz = self.horz_dbl
            if style == 's_title':
                west = self.w_dbl_connector
                connector = self.n_dbl_connector
                east = self.e_dbl_connector
            else:
                west = self.sw_dbl_connector
                connector = self.horz_dbl
                east = self.se_dbl_connector
        elif style == 's_header_final':
            west = self.sw_dbl_connector
            horz = self.horz_dbl
            east = self.se_dbl_connector
            connector = self.s_dbl_connector
        elif style == 'north':
            west = self.nw
            horz = self.horz
            east = self.ne
            connector = self.n_connector
        elif style == 'double':
            west = self.w_dbl_connector
            horz = self.horz_dbl
            east = self.e_dbl_connector
            connector = self.horz_dbl_connector
        elif style == 'single':
            west = self.w_connector
            horz = self.horz
            east = self.e_connector
            connector = self.horz_connector
        elif style == 'south':
            west = self.sw
            horz = self.horz
            east = self.se
            connector = self.s_connector
        else:
            sys.stderr.write('\nUnknown style "' + style + 
                '"in __draw_line_separator()\n')
            sys.exit(1)
        lpad = horz * len(self.lpad) if len(self.lpad) else ''
        rpad = horz * len(self.rpad) if len(self.rpad) else ''
        l_vbar = (self.w_dbl_connector if style == 'north' 
            else self.w_connector if style == 'middle'
            else self.sw)
        r_vbar = (self.e_dbl_connector if style == 'north' 
            else self.e_connector if style == 'middle'
            else self.se)
        return((west + lpad + 
            (rpad + connector + lpad).join(horz * c 
                    for c in self.cols_max_width[:self.last_col_idx + 1]) + 
                rpad + east) + ('\n' 
                        if style not in ('south', 's_header_final', 
                                's_tital_final')
                        else ''))

    #-----------------------------------------------------------------------#
    # __pad_columns                                                         #
    #-----------------------------------------------------------------------#
    def __pad_columns(self):
        '''Make sure all rows have the same number of columns.'''
        # Which row has the most columns?
        nr_cols = 0
        for row in self.rows:
            if len(row) > nr_cols:
                nr_cols = len(row)
        # Add extra columns to any row with < nr_cols.
        [[row.append('') for i in range(nr_cols - len(row))]
            for row in self.rows]

    #-----------------------------------------------------------------------#
    # set_col_property                                                      #
    #-----------------------------------------------------------------------#
    def set_col_property(self, nr, prop):
        # Make sure we have a dictionary in self.cols_props for every
        # column up to at least nr.
        if len(self.cols_props) < nr:
            for i in range(nr - len(self.cols_props)):
                self.cols_props.append({})
        for key, val in prop.items():
            self.cols_props[nr-1][key] = val

    #-----------------------------------------------------------------------#
    # set_default_col_props                                                 #
    #-----------------------------------------------------------------------#
    def __set_default_col_props(self):
        for i in range(len(self.rows[0])):
            if len(self.cols_props) < i + 1:
                self.cols_props.append({})
            if 'justify' not in self.cols_props[i]:
                self.cols_props[i]['justify'] = DEF_COL_PROP_JUSTIFY

    #-----------------------------------------------------------------------#
    # __draw_row                                                            #
    #-----------------------------------------------------------------------#
    def __draw_row(self, row, color_on, color_off, color_static, 
            color_bg_static, is_header=False):
        row_formatted = ''
        if not self.no_borders:
            row_formatted = self.vert
        for i in range(self.last_col_idx + 1):
            clr_on = color_on
            clr_off = color_off
            if not is_header:
                if not color_static and 'color' in self.cols_props[i]:
                    clr_on += '\x1b[' + self.cols_props[i]['color'] + 'm'
                    clr_off = '\x1b[0m'
                if not color_bg_static and 'bgcolor' in self.cols_props[i]:
                    clr_on += '\x1b[' + self.cols_props[i]['bgcolor'] + 'm'
                    clr_off = '\x1b[0m'
            fmt = self.lpad + clr_on
            justify = (self.hjustify 
                if is_header 
                else self.cols_props[i]['justify'])
            if justify == 'center':
                half, mod = divmod(self.cols_max_width[i] - 
                        len(row[i].decode('utf-8')), 2)
                fmt += ((' ' * half) + '%s' + (' ' * (half + mod)))
            else:
                fmt += ('%' + 
                    ('-' if justify == 'left' else '') + 
                    str(self.cols_max_width[i]) + 's')
                # BUG
#                 print '[' + fmt + ']'
            fmt += clr_off + self.rpad + self.vert
#             print '[' + fmt + ']'
            if len(row_formatted) and self.no_borders:
                row_formatted += self.nb_pad
#             print '[' + row[i] + ']'
            row_formatted += fmt % row[i].decode('utf-8')
#             print '[' + row_formatted + ']'
        return row_formatted

    #-----------------------------------------------------------------------#
    # nr_rows                                                               #
    #-----------------------------------------------------------------------#
    def nr_rows(self):
        return len(self.rows) - (1 if self.header else 0)

#---------------------------------------------------------------------------#
# main                                                                      #
#---------------------------------------------------------------------------#
if __name__ == '__main__':
    '''If this module is called directly, it produces a short sample.'''
    import textwrap
    # See constructor above for all possible arguments.
    t = ConsoleTable(
        title='Sample ConsoleTable ©',
        header=(),
        # 256-color example
        tcolor='48;5;253',
        hcolor='34;1',
        color='34',
        utf8 =True,
        strip_empty_trailing_cols=True,
        line_separators=False,
        tjustify='center',
        lpad=' ',
        rpad=' ',
        vert='|',
        horz='-',
        horz_dbl='=',
        connector='+'
    )
    t.add_header(['Customer ™', 'IP Address', 'Hostname', 'Notes'])
    t.set_col_property(2, {'justify': 'right', 'color': '38;5;90'})
    t.set_col_property(3, {'justify': 'center'})
    t.set_col_property(3, {'color': '32', 'bgcolor': '48;5;254'})
    t.add_row(['Andy Alliterative\n\ndefault color:\nblue', 
        '10.0.0.5\n(right-justified)\n\n' +
            'This column is\nmagenta which\noverrides the\ndefault ' +
            'color\n(left), and is\nitself overridden\nby row color\n ' +
            '(below)', 
        '',
        textwrap.fill('Cells can be empty (left); trailing cells can ' +
            'even be omitted. This cell word-wrapped with ' + 
            'textwrap.fill().', 16)]) 
    t.add_row(['default colors are\nlowest precedence',
            'column colors\noverride default\ncolors',
            'row colors\noverride all\nother colors',
            'red on white'],
        {'color': '37;1', 'bgcolor': '48;5;124'})
    t.add_row(['Jack Johnson 98.6⁰\n(now with UTF-8)', 
        '192.168.3.2', 
        'green on\ngray column\ncentered',
        'color: blue'])
    print t.draw()
