# Swissknife Test Harness Script for fullparse
# 
# Purpose: 
# After a full parse, the output file should be identical 
# to the input.

# * Test loading
BEGIN { 
  $| = 1; print "1..2\n"; 
  use vars qw($loaded); 
  $^W = 1;
}

BEGIN {
	if ($] >= 5.008 and $] < 5.008002) {
		warn "

WARNING: You are running perl version 5.8.0 or 5.8.1.  There is a
bug in these perl versions that may causes a crash when Swissknife
is run on certain entries. If you get a 'Segmentation fault' or a
funny output such as ('int'  \$__val) in the following test
(identity), you should use either an older or a more recent
version of perl, or use Swissknife at your own risk.

";
	}
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
  $entry = SWISS::Entry->fromText($_, 1);
  $entry->reformat;
  $entry -> CCs -> filter(&SWISS::CCs::ccTopic('ALTERNATIVE PRODUCTS'));
  $entry->DRs->sort;
	$entry->FTs->sort($entry->SQs->length);
 
  print OUT $entry->toText;
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





