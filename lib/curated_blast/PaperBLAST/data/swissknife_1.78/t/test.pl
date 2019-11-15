#!/bin/env perl

# *************************************************************
#
# Purpose: 
# Run tests on Swissknife
#
# Usage:
# test.pl list_of_test_scripts
#
# *************************************************************
#

BEGIN {
  unless(grep /blib/, @INC) {
    chdir 't' if -d 't';
    unshift @INC, '../lib' if -d '../lib';
  }
}

use Test::Harness;

print STDERR "*** Swissknife test suite ***\n\n";

@ARGV = sort <*.t> unless @ARGV;

runtests(@ARGV);
