#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cdsimplegenestoterm
----------------------------------

Tests for `cdsimplegenestoterm` module.
"""

import os
import sys
import unittest
import tempfile
import shutil
from cdsimplegenestoterm import cdsimplegenestotermcmd


class TestCdsimplegenestoterm(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_inputfile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            tfile = os.path.join(temp_dir, 'foo')
            with open(tfile, 'w') as f:
                f.write('hellothere')
            res = cdsimplegenestotermcmd.read_inputfile(tfile)
            self.assertEqual('hellothere', res)
        finally:
            shutil.rmtree(temp_dir)

    def test_parse_args(self):
        myargs = ['inputarg']
        res = cdsimplegenestotermcmd._parse_arguments('desc',
                                                      myargs)
        self.assertEqual('inputarg', res.input)
        self.assertEqual(0.00001, res.maxpval)
        self.assertEqual('/tmp/cdsimplegenestoterm.pickle', res.db)

    def test_run_iquery_no_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            tfile = os.path.join(temp_dir, 'foo')
            myargs = [tfile]
            theargs = cdsimplegenestotermcmd._parse_arguments('desc',
                                                              myargs)
            try:
                cdsimplegenestotermcmd.run_simple(tfile,
                                                  theargs)
                self.fail('Expected FileNotFoundError')
            except FileNotFoundError:
                pass
        finally:
            shutil.rmtree(temp_dir)

    def test_run_iquery_empty_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            tfile = os.path.join(temp_dir, 'foo')
            open(tfile, 'a').close()
            myargs = [tfile]
            theargs = cdsimplegenestotermcmd._parse_arguments('desc',
                                                              myargs)
            res = cdsimplegenestotermcmd.run_simple(tfile,
                                                    theargs)
            self.assertEqual(None, res)
        finally:
            shutil.rmtree(temp_dir)

    def test_main_invalid_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            tfile = os.path.join(temp_dir, 'foo')
            myargs = ['prog', tfile]
            res = cdsimplegenestotermcmd.main(myargs)
            self.assertEqual(2, res)
        finally:
            shutil.rmtree(temp_dir)

    def test_main_empty_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            tfile = os.path.join(temp_dir, 'foo')
            open(tfile, 'a').close()
            myargs = ['prog', tfile]
            res = cdsimplegenestotermcmd.main(myargs)
            self.assertEqual(0, res)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    sys.exit(unittest.main())
