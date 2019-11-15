#!/usr/bin/perl

# *************************************************************
#
# Purpose:
# Run a Perl benchmark using the Swissknife modules.
#
# Usage: 
# benchmark.pl -file filename -repeats int
#
# *************************************************************

# ** Initialisation

use vars qw($opt_file $opt_repeats $tmpsource $tmptarget $opt_debug $opt_warn);
use SWISS::Entry;
use Benchmark;
use Getopt::Long;
use strict;
    
# * Global constants
# Read an entire record at a time
$/ = "\/\/\n";

$opt_debug = 0;
$opt_warn = 1;

$tmpsource = '/tmp/perlBenchSource' . $$;
$tmptarget = '/tmp/perlBenchTarget' . $$;


# * Variables
my ($codeStart, $codeStop, $code);

# * Read options
&GetOptions("file=s", "repeats=i");

unless ($opt_file && $opt_repeats =~ /\A\d+\Z/) {
  die "Usage: benchmark.pl -file filename -repeats int\n";
};

system "cp $opt_file $tmpsource";

# ** Main

print "*** Swissknife Benchmark and Test suite *** \n";

$codeStart = '
  open (IN, $tmpsource) || die "Could not open $opt_file";
  open (ZERO, ">/dev/null");
  open (OUT, ">$tmptarget");
  while (<IN>) {';

$codeStop = '};
  close IN;
  close OUT;
';

# Read only
$code = '$entry = SWISS::Entry->fromText($_);';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read only:             ');

# Read and write entries to /dev/null
$code = '
   $entry = SWISS::Entry->fromText($_);
   print ZERO $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write NULL:       ');

# Read and write entries to /tmp
$code = '
   $entry = SWISS::Entry->fromText($_);
   print OUT $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write:            ');

# Add AC
$code = '
   $entry = SWISS::Entry->fromText($_);
   $entry->ACs->add(Q12345);
   print OUT $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write/addAC:      ');


# Read and write entries, fullparse
$code = '
   $entry = SWISS::Entry->fromText($_,1);
   print OUT $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write/Fullparse:  ');

# Force update
$code = '
   $entry = SWISS::Entry->fromText($_,1);
   $entry->update(1);
   print OUT $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write/Fp/Update:  ');


# Compare the entry to itself
$code = '
   $entry = SWISS::Entry->fromText($_);
   $entry->equal($entry);';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/equals:           ');

# Complex modifications of entries
$code = '
$entry = SWISS::Entry->fromText($_);
$entry->ACs->add("Q1", "Q2");
$entry->IDs->list([]);
$entry->IDs->add("NEW_ID");
$pfs = $entry->Stars->pf;
$pfs->add("PFAM test line");
$entry->Stars->pf($pfs);
$entry->Stars->fl->add("TESTFLAG");
$entry->DRs->del("PFAM");
$entry->OCs;
$entry->DRs->del("EMBL");
$entry->Stars->translate;
print OUT $entry->toText;';
timethis ($opt_repeats, $codeStart . $code . $codeStop, 'Read/Write/Modify:     ');
