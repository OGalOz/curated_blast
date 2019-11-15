# Swissknife Test Harness Script for fullparse
# 
# Purpose: 
# After a full parse, the output file should be identical 
# to the input.

# * Test loading
BEGIN { 
  $| = 1; print "1..2\n"; 
  use vars qw($loaded); 
  $^W = 0;
}

END {print "not ok 1\n" unless $loaded;}


$loaded = 1;
print "ok 1\n";    # 1st test passes.

sub test ($$;$) {
    my($num, $true,$msg) = @_;
    print($true ? "ok $num\n" : "not ok $num $msg\n");
}

my $where = -d 't' ? "t/" : "";
my $testin = "${where}identity.txl";
my $testout  = "${where}identity.txl.out";
my $expectedout = "${where}identity.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;

# Read an entire record at a time
$/ = "\/\/\n";

while (<IN>){
  # Read the entry
  $entry = SWISS::Entry->fromText($_);
  $entry->reformat;
  $entry->DRs->update();	
  $entry->SQs->update(); 
  print OUT $entry->toText;
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";

