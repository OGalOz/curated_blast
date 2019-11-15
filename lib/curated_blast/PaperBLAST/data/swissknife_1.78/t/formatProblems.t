# Swissknife Test Harness Script for fullparse
# 
# Purpose: 
# Check if a set of tricky entries are correctly (re-)formatted.

# * Test loading
BEGIN { 
  $| = 1; print "1..2\n"; 
  use vars qw($loaded); 
  $^W = 1;
}

END {print "not ok 1\n" unless $loaded;}


$loaded = 1;
print "ok 1\n";    # 1st test passes.

sub test ($$;$) {
    my($num, $true,$msg) = @_;
    print($true ? "ok $num\n" : "not ok $num $msg\n");
}

my $where = -d 't' ? "t/" : "";
my $testin = "${where}formatProblems.txl";
my $testout  = "${where}formatProblems.txl.out";
my $expectedout = "${where}formatProblems.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;

# Read an entire record at a time
$/ = "\/\/\n";
 
while (<IN>){
  # Read the entry
  $entry = SWISS::Entry->fromText($_, 1);
  $entry->reformat;

  #the following three lines give duplicate **\n and **...INTERNAL SECTION
  #lines in Swissknife 1.1
  $entry->toText;
  $entry->Stars->update;
  
  # check that adding non-existing synonyms to alternative products lines
  # does not produce blank events where the comment/name does not exist
  
  foreach $CC ($entry -> CCs -> elements()) {
  
     if ($CC -> topic eq 'ALTERNATIVE PRODUCTS') {
      
       $CC -> addEvidenceTag('EP1', "Alternative splicing", "Name", "E");
       $CC -> addEvidenceTag('EP1', "Alternative splicing", "Name", "Wrong");
       my @events = $CC -> getEventNames();
       
       foreach $event (@events) {
       
         if ($event eq "Alternative splicing") {
         
           # check that a synonym lists and sequence lists are wrapped 
           # sucessfully
         
           my @synonyms = ("Alice", "Barbara", "Chloe", "Deborah", "Emily",
                           "Frida");
           $CC -> setSynonyms("Alternative splicing", "E", \@synonyms);
           my @sequences = 
             ("VSP_02391", "VSP_02392", "VSP_02393",  "VSP_02394", "VSP_02395");
           $CC -> setFeatIds( "Alternative splicing", "E", \@sequences);
         }
       }
     }
   }
  
  $entry->toText();
  $entry->update(1);

  $entry->CCs->sort;
  $entry->CCs->unique;
  
  $entry->DRs->del('PROSITE','PS01117');	
map {$_->rc_sort; $_->reformat} $entry->Refs->elements;
map {$_->rc_sort; $_->reformat} $entry->Refs->elements;
 
  print OUT $entry->toText;
  print OUT $entry->isCurated(), "\n";
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





