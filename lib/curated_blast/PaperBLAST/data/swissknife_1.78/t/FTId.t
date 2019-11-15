# Checks if FTIds are handled correctly.

use Carp;
use SWISS::Entry;

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
my $testin = "${where}FTId.txl";
my $testout  = "${where}FTId.txl.out";
my $expectedout = "${where}FTId.txl";

open (IN, $testin);
open (OUT, ">$testout");

local $/ = "//\n";
 
while (<IN>){
  $entry = SWISS::Entry->fromText($_, 1, 1);
  print OUT $entry->toText();
}

close IN;
close OUT;

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";
