import os
import re
import sys
import sty
import pwd
import grp
import stat
import itertools
from datetime import datetime
from ruamel import yaml

def get_rules():
    try:
        return yaml.safe_load(open('~/.lc.rules.yaml'))
    except:
        this_directory = os.path.abspath(os.path.dirname(__file__))
        default_config = os.path.join(this_directory, '.lc.rules.yaml')
        return yaml.safe_load(open(default_config))

def colorize(color, icon, file):
    if type(color) == list:
        color = sty.fg(*color)
    else:
        color = sty.fg(color)
    return f'{color}{icon} {file}{sty.fg.rs}'

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def get_terminal_size(fallback=(80, 24)):
    for i in range(0,3):
        try:
            columns, rows = os.get_terminal_size(i)
        except OSError:
            continue
        break
    else:  # set default if the loop completes which means all failed
        columns, rows = fallback
    return columns, rows

def get_table_size(table):
    width, _ = get_terminal_size()
    for i in reversed(range(1, 11)):
        rows = list(chunks(table, i))
        cols = itertools.zip_longest(*rows, fillvalue='')
        col_widths = [max(len(item) + 4  for item in col) for col in cols]
        row_width = sum(col_widths) - 2
        item_widths = [[len(item) + 2 for item in row] for row in rows]
        if row_width <= width:
            return i, col_widths, item_widths

def lpad_equal(items):
    pad_size = max(len(item) for item in items)
    return [item.rjust(pad_size, ' ') for item in items]

perm_map = {
    "0": "---",
    "1": "--x",
    "2": "-w-",
    "3": "-wx",
    "4": "r--",
    "5": "r-x",
    "6": "rw-",
    "7": "rwx",
}

def num2sym(num):
    return perm_map[num]

def get_perm(file):
    octal = str(oct(stat.S_IMODE(file.stat().st_mode)))[2:]
    isdir = file.is_dir()
    perm = isdir and 'd' or '-'
    return perm + ''.join(map(num2sym, octal))

def print_with_options(files, colorized_files, size, options):
    rows = chunks(colorized_files, size[0])
    if 'l' in options:
        stats = [file.stat() for file in files]
        # left pad
        sizes = lpad_equal([str(stat.st_size) for stat in stats])
        users = lpad_equal([pwd.getpwuid(stat.st_uid)[0] for stat in stats])
        groups = lpad_equal([grp.getgrgid(stat.st_gid)[0] for stat in stats])
        nlinks = lpad_equal([str(stat.st_nlink) for stat in stats])
        # permissions
        permissions = map(get_perm, files)
        # zip all the info
        zipped = zip(files, sizes, users, groups, nlinks, permissions, colorized_files)
        for file, size, user, group, nlink, permission, colorized in zipped:
            last_modified = datetime.utcfromtimestamp(file.stat().st_mtime).strftime('%b %d %H:%M').replace(' 0', '  ')
            print(f'{permission} {nlink} {user} {group} {size} {last_modified} {colorized}')
    else:
        for row_number, row in enumerate(rows):
            row_size = size[2][row_number]
            new_row = []
            for col_number, item in enumerate(row):
                width = len(item)
                original_width = row_size[col_number]
                controls = width - original_width
                new_width = size[1][col_number] + controls - 2
                new_item = item.ljust(new_width, ' ')
                new_row.append(new_item)
            print('  '.join(new_row))

def is_hidden(directory, filename):
    filepath = os.path.join(directory, filename)
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    try:
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    except:
        return False

def main():
    rules = get_rules()
    argv = sys.argv[1:]
    directories = [arg for arg in argv if not arg.startswith('-')] or ['.']
    options = [option for arg in argv if arg.startswith('-') for option in arg[1:]]
    for index, directory in enumerate(directories):
        with os.scandir(directory) as scan:
            files = [entry for entry in scan]
            if not 'a' in options:
                files = [file for file in files if not is_hidden(directory, file.name)]
        files = sorted(files, key = lambda e: e.name)
        file_names = [file.name for file in files]
        size = get_table_size(file_names)
        colorized_files = []
        for file in file_names:
            path = os.path.join(directory, file)
            for rule in rules:
                if re.search(rule, file):
                    color, icon = rules[rule]
                    colorized = colorize(color, icon, file)
                    colorized_files.append(colorized)
                    break
                if rule.startswith('$'):
                    if os.path.isdir(path):
                        color, icon = rules['$dir']
                    elif os.path.isfile(path):
                        color, icon = rules['$file']
                    colorized = colorize(color, icon, file)
                    colorized_files.append(colorized)
                    break
        if len(directories) > 1:
            print(f'{directory}:')
        print_with_options(files, colorized_files, size, options)
        if len(directories) > 1 and index != len(directories) - 1:
            print()

if __name__ == '__main__':
    main()