# Swissknife Test Harness Script for DEs
# 
# Purpose: 
# Check whether the advanced parser in DEs works well.

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
my $testin = "${where}DEs.txl";
my $testout  = "${where}DEs.txl.out";
my $expectedout = "${where}DEs.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;

# Read an entire record at a time
$/ = "\/\/\n";

while (<IN>){
  # Read the entry
  my $entry = SWISS::Entry->fromText($_,1);

  my $i;
    print OUT $entry->DEs->toString;
    for my $DEs ($entry->DEs)
    {
	print OUT "\nlist : ", join ', ', map {'"'.$_->text.'"'} $DEs->elements;
	print OUT "\nhasFragment : ", $DEs->hasFragment;
	print OUT "\nchildType : ", "";
     }
  print OUT "\n>";
	for my $p (["Includes", $entry->DEs->Includes], ["Contains", $entry->DEs->Contains]) {
		my ($type, $obj) = @$p;
		for my $child ($obj->elements) {
			print OUT "\nlist : ", join ', ', map {'"'.$_->text.'"'} $child->elements;
			print OUT "\nhasFragment : ", $child->hasFragment;
			print OUT "\nchildType : ", $type;
		}
	}
  print OUT "\n//\n";
  unless ($is_not_first_entry++) {
	  print OUT $entry->toText;
	  $entry->DEs->text("Some strange protein (Fragment)  (Version 2)");
	  print OUT $entry->toText;
  }
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





