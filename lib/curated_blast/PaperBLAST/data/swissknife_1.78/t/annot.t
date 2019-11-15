# Swissknife Test Harness Script for annotators jobs
# 
# Purpose: 
# Check if the parsing of wild ** comments and indented
# lines is performed correctly.

use Carp;

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
my $testin = "${where}annot.txl";
my $testout  = "${where}annot.txl.out";
my $expectedout = "${where}annot.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;
use Data::Dumper;

# Read an entire record at a time
$/ = "\/\/\n";
 
while (<IN>){
  # Read the entry
  $entry = SWISS::Entry->fromText($_, 1, 1);
  $entry->GNs->set(); #perturbate the entry
  $entry->CCs->del("MISCELLANEOUS"); #perturbate the entry
  $entry->update(1);
  $entry->FTs($entry->FTs->copy);
  $entry->DRs($entry->DRs->copy);
  print OUT $entry->toText(); #no indented / wild ** lines
  print OUT $entry->toText(1);#add indented / wild ** lines
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





