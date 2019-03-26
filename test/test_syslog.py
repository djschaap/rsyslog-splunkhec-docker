#!/usr/bin/python

# working directory should be base of project (NOT tests/)

import glob
import json
import re
import unittest
from subprocess import Popen, PIPE

class TestSyslog(unittest.TestCase):

  def run_lognormalizer_test(
      self,
      input_file,
      expected_file,
      rulebase_file
    ):
    self.maxDiff = 80*40 # python 2.7 default is 80*8
    input_fh = open(input_file, "r")
    p = Popen(["lognormalizer", "-T", "-r", rulebase_file],
      stdin=input_fh,
      stdout=PIPE)
    (lognorm_output, lognorm_err) = p.communicate()
    exit_code = p.wait()
    input_fh.close()
    self.assertEqual(exit_code, 0)
    self.assertEqual(lognorm_err, None)

    expect_fh = open(expected_file)
    expect_str = expect_fh.read()
    try:
      expect_json = json.loads(expect_str)
    except ValueError as e:
      self.fail("decoding JSON from " + expected_file + " failed: "
        + str(e))
    expect_fh.close()

    lognorm_output_lines = lognorm_output.splitlines()
    lognorm_output_json_array = []
    for line in lognorm_output_lines:
      try:
        lognorm_json = json.loads(line)
      except Exception as e:
        self.fail("reading JSON output from " + input_file + " failed: "
          + str(e))
      lognorm_output_json_array.append(lognorm_json)

    # may need to ensure JSON is sorted consistently during implicit
    #   conversion to string
    try:
      self.assertEqual(lognorm_output_json_array, expect_json)
    except Exception as e:
      self.fail("incorrect output from " + input_file + ": "
        + str(e))

#  def test_upper(self):
#    self.assertEqual('foo'.upper(), 'FOO')

#  def test_isupper(self):
#    self.assertTrue('FOO'.isupper())
#    self.assertFalse('Foo'.isupper())

#  def test_split(self):
#    s = 'hello world'
#    self.assertEqual(s.split(), ['hello', 'world'])
#    # check that s.split fails when the separator is not a string
#    with self.assertRaises(TypeError):
#      s.split(2)

#  def test_echo(self):
#    p = Popen(["echo", "test"], stdout=PIPE)
#    (output, err) = p.communicate()
#    exit_code = p.wait()
#    self.assertEqual(exit_code, 0)
#    self.assertEqual(output, "test\n")
#    self.assertEqual(err, None)

  def test_syslog_json_files(self):
    rulebase_file = "default/syslog.rulebase"
    json_files = glob.glob('sample/syslog/*.json')
    for json_file in json_files:
      raw_file = re.sub(r'\.json$', '.raw', json_file)
      # TODO error if raw file does not exist
      self.run_lognormalizer_test(
        input_file = raw_file,
        expected_file = json_file,
        rulebase_file = rulebase_file,
      )

  def test_lognormalizer_cat_2960x_01(self):
    raw_file = "sample/syslog/cat-2960x-01.raw"
    json_file = "sample/syslog/cat-2960x-01.json"
    rulebase_file = "default/syslog.rulebase"
    self.run_lognormalizer_test(
      input_file = raw_file,
      expected_file = json_file,
      rulebase_file = rulebase_file,
    )

if __name__ == '__main__':
  unittest.main()
