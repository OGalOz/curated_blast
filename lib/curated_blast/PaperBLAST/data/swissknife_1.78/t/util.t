# Swissknife Test Harness Script
# 
# Purpose: 
# Check utility methods.

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
my $testin = "${where}util.txl";

open (IN, $testin);

use SWISS::Entry;


# Check reply from isCurated():

# Read an entire record at a time
$/ = "\/\/\n";
 
# Read the entries
while (<IN>){
  $entry = SWISS::Entry->fromText($_);
  push @results, $entry->isCurated();
}

test 2, (join "",@results) eq "100";

