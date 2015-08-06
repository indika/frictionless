#!/usr/bin/python -utWall
# -*- coding: utf-8 -*-

import os, sys, re, errno

class Modifier(object):
    rows = None
    filename = None
    is_changed = False

    regexp = re.compile('^(.*\(\s*define-key.*map.*\[\([^,]*,\s*osxkeys-command-key\s+)([^)]+)(\)\].*)$')

    def __init__(self, filename):
        self.filename = filename

        fd = file(filename, 'r')
        self.rows = [x.rstrip() for x in fd.readlines()]
        fd.close()

    def write(self, filename):
        if not self.is_changed:
            print "No changes to write."
            return

        # Backup
        if os.path.exists(filename):
            backname = filename + '.bak'
            try:
                os.unlink(backname)
            except OSError, err:
                if err.errno != errno.ENOENT:
                    raise
            os.link(filename, backname)

        # Write
        fd = file(filename, 'w')
        fd.writelines(["%s\n" % x for x in self.rows])
        fd.close()

    def check(self, map):
        keys = set(map.keys())
        values = set(map.values())
        value_not_a_key = values.difference(keys)
        key_not_a_value = keys.difference(values)
        diff = keys.symmetric_difference(values)
        if diff:
            print
            print "Key but not a value: %r" % key_not_a_value
            print "Value but not a key: %r" % value_not_a_key
            print
            raise ValueError("Unbalanced keys: %r" % diff)

    def fix(self, map):
        alreadydone = " ; @@CHANGED "
        rows = self.rows

        for i in range(len(rows)):
            line = rows[i]
            if alreadydone in line:
                continue

            match = self.regexp.match(line)
            if match:
                start, char, end = match.groups()
                char = char.strip()
                newchar = map.get(char, char)
                if char == newchar:
                    tail = "%s no change" % alreadydone
                else:
                    tail = "%s %s -> %s" % (alreadydone, char, newchar)

                rows[i] = "".join((start, newchar, end, tail))
                self.is_changed = True

def escape(c):
    mod = None
    parts = c.split(' ',1)
    if parts[0] == 'shift':
        mod = parts[0]
        c = parts[1]
    if len(c) == 1:
        if c in "?;`',<>][":
            c = '\\%s' % c
    if mod:
        return " ".join((mod,c))
    else:
        return c

if __name__ == '__main__':
    src = "/Applications/Aquamacs.app/Contents/Resources/lisp/aquamacs/macosx/osxkeys.el"
    m = Modifier(src)

    # Dvorak to QWERTY mappings
    # It was easier for me to type it this way...
    dvorak_to_qwerty = {
        #dv    qw        dv           qw
        "[":   '-',      '{':         '_',
        ']':   '=',      '}':         '+',

        "'":   'q',      '"':         'shift q',
        ',':   'w',      '< ':         'shift w',
        '.':   'e',      '>':         'shift e',
        'p':   'r',      'shift p':   'shift r',
        'y':   't',      'shift y':   'shift t',
        'f':   'y',      'shift f':   'shift y',
        'g':   'u',      'shift g':   'shift u',
        'c':   'i',      'shift c':   'shift i',
        'r':   'o',      'shift r':   'shift o',
        'l':   'p',      'shift l':   'shift p',
        '/':   '[',      '?':         '{',
        '=':   ']',      '+':         '}',
        '\\':  '\\',     '|':         '|',

        'a':   'a',      'shift a':   'shift a',
        'o':   's',      'shift o':   'shift s',
        'e':   'd',      'shift e':   'shift d',
        'u':   'f',      'shift u':   'shift f',
        'i':   'g',      'shift i':   'shift g',
        'd':   'h',      'shift d':   'shift h',
        'h':   'j',      'shift h':   'shift j',
        't':   'k',      'shift t':   'shift k',
        'n':   'l',      'shift n':   'shift l',
        's':   ';',      'shift s':   ':',
        '-':   "'",      '_':         '"',

        ';':   'z',      ':':          'shift z',
        'q':   'x',      'shift q':    'shift x',
        'j':   'c',      'shift j':    'shift c',
        'k':   'v',      'shift k':    'shift v',
        'x':   'b',      'shift x':    'shift b',
        'b':   'n',      'shift b':    'shift n',
        'm':   'm',      'shift m':    'shift m',
        'w':   ',',      'shift w':    '< ',
        'v':   '.',      'shift v':    '>',
        'z':   '/',      'shift z':    '?',

        }

    dvorak_to_qwerty = dict([(escape(x),escape(y)) for x,y in dvorak_to_qwerty.items()])

    m.check(dvorak_to_qwerty)

    # Flip it...
    qwerty_to_dvorak = dict([(y,x) for x,y in dvorak_to_qwerty.items()])
    m.fix(qwerty_to_dvorak)

    # Write out the changes.
    dst = os.path.expanduser("~/Library/Preferences/Aquamacs Emacs/osxkeys.el")
    if os.path.exists(dst):
        os.unlink(dst)
    m.write(dst)
