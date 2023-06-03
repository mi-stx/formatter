#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @id           $Id$
# @rev          $Format:%H$ ($Format:%h$)
# @tree         $Format:%T$ ($Format:%t$)
# @date         $Format:%ci$
# @author       $Format:%an$ <$Format:%ae$>
# @copyright    Copyright (c) 2019-present, Duc Ng. (bitst0rm)
# @link         https://github.com/bitst0rm
# @license      The MIT License (MIT)

import os
import logging
import tempfile
from . import common


log = logging.getLogger('root')
INTERPRETER_NAMES = ['node']
EXECUTABLE_NAMES = ['prettier']


class PrettierFormatter:
    def __init__(self, view, identifier, region, is_selected):
        self.view = view
        self.identifier = identifier
        self.region = region
        self.is_selected = is_selected
        self.pathinfo = common.get_pathinfo(view.file_name())


    def get_cmd(self, filename):
        interpreter = common.get_interpreter_path(INTERPRETER_NAMES)
        executable = common.get_executable_path(self.identifier, EXECUTABLE_NAMES)

        if not interpreter or not executable:
            return None

        cmd = [interpreter, executable]

        args = common.get_args(self.identifier)
        if args:
            cmd.extend(args)

        config = common.get_config_path(self.view, self.identifier, self.region, self.is_selected)
        if config:
            cmd.extend(['--config', config])

        cmd.extend(['--write', filename])

        return cmd


    def format(self, text):
        # Prettier automatically infers which parser to use based on the file extension.
        # ext ref: https://github.com/prettier/prettier/blob/master/.pre-commit-hooks.yaml
        suffix = '.' + common.get_assign_syntax(self.view, self.identifier, self.region, self.is_selected)

        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=suffix, dir=self.pathinfo[1], encoding='utf-8') as file:
                file.write(text)
                file.close()
                result = self._format(file.name)
        finally:
            if os.path.isfile(file.name):
                os.unlink(file.name)

        return result


    def _format(self, filename):
        cmd = self.get_cmd(filename)
        if not cmd:
            return None

        try:
            proc = common.exec_cmd(cmd, self.pathinfo[0])
            stderr = proc.communicate()[1]

            errno = proc.returncode
            if errno > 0:
                log.error('File not formatted due to an error (errno=%d): "%s"', errno, stderr.decode('utf-8'))
            else:
                with open(filename, 'r', encoding='utf-8') as file:
                    result = file.read()
                    return result
        except OSError:
            log.error('Error occurred when running: %s', ' '.join(cmd))

        return None
