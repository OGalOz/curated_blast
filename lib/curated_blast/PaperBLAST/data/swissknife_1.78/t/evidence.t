## Swissknife Test Harness Script for evidence tags
##

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
my $testin = "${where}evidence.txl";
my $testout  = "${where}evidence.txl.out";
my $expectedout = "${where}evidence.txl.expected";

open (IN, $testin);
open (OUT, ">$testout");

use SWISS::Entry;

# Read an entire record at a time
$/ = "\/\/\n";

while (<IN>){
  # Read the entry
  $entry = SWISS::Entry->fromText($_, 1);
 
  #${$entry->DEs->list}[3]->deleteEvidenceTag('EC3'); #evidence tagging the DE elements currently not supported
  #${$entry->DEs->list}[2]->addEvidenceTag('EC3');
  foreach $ref ($entry->Refs->elements()) {
    $ref->addEvidenceTag('ECO:0000269|PubMed:11433298');
  }

  $ev1 = $entry->Stars->EV->addEvidence('ECO:0000269', 
					'PubMed:11433298', 
					'XXX', 
					'28-Aug-2014'); # p.s. EV->add/updateEvidence now only work with new style evidences!...
  $ev2 = $entry->Stars->EV->addEvidence('ECO:0000269', 
					'PubMed:12665801', 
					'XXX', 
					'28-Aug-2014');
  $ev3 = $entry->Stars->EV->addEvidence('ECO:0000312', 
					'EMBL:EAL60914.1', 
					'XXX', 
					'28-Aug-2014');
  
  $entry->DEs->setEvidenceTags($ev3);
  $entry->DEs->addEvidenceTag($ev2);
  if ($entry->DEs->hasEvidenceTag($ev2)){
	print OUT "Has evidence $ev2.\n";
  }	
  # test changed as no longer makes sense for revised CC module
  
  @CCs = $entry->CCs->elements();
  foreach $cc (@CCs) {
    if (!$cc->isa('SWISS::ListBase')) {
      $cc->addEvidenceTag($ev1);
    }
  }
  
  foreach $dr ($entry->DRs->elements) {
    $entry->DRs->addEvidenceTag($dr, 'ECO:0000269|PubMed:11433298');
    $entry->DRs->deleteEvidenceTag($dr, 'ECO:0000303');
  }
  
  # Check conditional delete
  $entry->DRs->add(['ZFIN', 'P123', 'Q1234', ' {ECO:0000312|EMBL:EAL60914.1}']);
  $entry->DRs->add(['ZFIN', 'P123', 'Q1234', ' {ECO:0000269|PubMed:12527781}']);

  foreach $ft ($entry->FTs->elements) {
    $entry->FTs->addEvidenceTag($ft, 'ECO:0000269|PubMed:11433298');
    $entry->FTs->deleteEvidenceTag($ft, 'ECO:0000305');
  }
  foreach $kw ($entry->KWs->elements) {
    $kw->addEvidenceTag($ev2);
    $kw->deleteEvidenceTag('EC2');
  }
  my $newkw = new SWISS::KW;
  $newkw->text('Key1');
  $entry->KWs->add($newkw);
  $newkw->setEvidenceTags($ev3);
  $newkw = new SWISS::KW;
  $newkw->text('Key2');
  $newkw->setEvidenceTags($ev3);
  $newkw->deleteEvidenceTag($ev3);  
  $entry->KWs->add($newkw);

  my $newTax = new SWISS::OX;
  $newTax->text(3332);
  $entry->OXs->NCBI_TaxID->add($newTax);

  foreach $os ($entry->OSs->elements) {
    $os->addEvidenceTag('ECO:0000269|PubMed:11433298');
    $os->deleteEvidenceTag('ECO:0000269|PubMed:11433298');
  }

  # Test if the Swiss-Prot style evidence (POTENTIAL etc) and the
  # evidence tags are properly separated. 
  foreach $ft ($entry->FTs->elements()) {
    print OUT join ",", @$ft, "\n";
  }
  print OUT $entry->toText;
}

close IN;
close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





