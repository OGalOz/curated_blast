# Test for FASTA output

use Carp;

# * Test loading
BEGIN { 
  $| = 1; print "1..2\n"; 
  use vars qw($loaded); 
  $^W = 0;
}

END { print "not ok 1\n" unless $loaded; }

$loaded = 1;
print "ok 1\n";    # 1st test passes.

sub test ($$;$) {
    my($num, $true,$msg) = @_;
    print($true ? "ok $num\n" : "not ok $num $msg\n");
}

my $where = -d 't' ? "t/" : "";
my $testin = "${where}fasta.txl";
my $testout  = "${where}fasta.txl.out";
my $expectedout = "${where}fasta.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;
use Data::Dumper;

# Read an entire record at a time
$/ = "\/\/\n";
 
while (<IN>){
  $entry = SWISS::Entry->fromText($_);
  print OUT $entry->toFasta();
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";
