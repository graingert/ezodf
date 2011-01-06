#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: text processing
# Created: 06.01.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .xmlns import register_class, CN
from .base import BaseClass


@register_class
class Tabulator(BaseClass):
    TAG = CN('text:tab')

    def __str__(self):
        return self.plaintext()

    @property
    def textlen(self):
        return 1

    def plaintext(self):
        return '\t'

@register_class
class LineBreak(Tabulator):
    TAG = CN('text:line-break')

    def plaintext(self):
        return '\n'

@register_class
class Spaces(Tabulator):
    TAG = CN('text:s')
    def __init__(self, count=1, xmlroot=None):
        super(Spaces, self).__init__(xmlroot)
        if xmlroot is None:
            self.count = count

    @property
    def count(self):
        count = self.getattr(CN('text:c'))
        return int(count) if count is not None else 1
    @count.setter
    def count(self, value):
        if int(value) > 1:
            self.setattr(CN('text:c'), str(value))

    @property
    def textlen(self):
        return self.count

    def plaintext(self):
        return ' ' * self.count

class _ODFTextEncoder:
    result = []
    stack = []
    space_counter = 0

    def encode(self, plaintext):
        self.result = []
        self.stack=[]
        self.space_counter = 0
        for char in plaintext:
            if char == '\n':
                self.add_brk()
            elif char == '\t':
                self.add_tab()
            elif char == ' ':
                self.add_spc()
            else:
                self.add_char(char)
        if self.space_counter > 1:
            self.append_space()
        else:
            self.append_stack()
        return self.result

    @staticmethod
    def decode(taglist):
        return "".join( (str(tag) for tag in taglist) )

    def append_stack(self):
        if not self.stack:
            return
        txt = ''.join(self.stack)
        self.stack = []
        self.result.append(txt)

    def append_space(self):
        spaces = self.space_counter - 1
        # remove last spaces from stack
        self.stack = self.stack[: -spaces]
        self.append_stack()
        self.result.append(Spaces(spaces))
        self.space_counter = 0

    def add_brk(self):
        if self.space_counter > 1:
            self.append_space()
        else:
            self.append_stack()
        self.space_counter = 0
        self.result.append(LineBreak())

    def add_tab(self):
        if self.space_counter > 1:
            self.append_space()
        else:
            self.append_stack()
        self.space_counter = 0
        self.result.append(Tabulator())

    def add_spc(self):
        self.add_char(' ')
        self.space_counter += 1

    def add_char(self, char):
        if char != ' ':
            if self.space_counter > 1:
                self.append_space()
            else:
                self.space_counter = 0
        self.stack.append(char)

ODFTextEncoder = _ODFTextEncoder()

def encode(plaintext):
    return ODFTextEncoder.encode(plaintext)

def decode(taglist):
    return ODFTextEncoder.decode(taglist)