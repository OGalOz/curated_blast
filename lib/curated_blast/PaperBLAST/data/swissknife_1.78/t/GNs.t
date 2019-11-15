# Swissknife Test Harness Script for GNs
# 
# Purpose: 
# Check whether the advanced parser in GNs works well.

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

use SWISS::GNs;
my $where = -d 't' ? "t/" : "";
my $testout  = "${where}GNs.txl.out";
my $expectedout = "${where}GNs.txl.expected";

open (OUT, ">$testout");

my $out="";
my $text = "GN   (A{EA1} OR B{EI2}) And C.\n";
my $gn=SWISS::GNs->fromText(\$text,1);
$gn->toText(\$out);
print OUT $out;

#ev tags
for my $gg ($gn->elements) {
 for(my $i=0;$i<$gg->size;$i++) {
  ${$gg->list}[$i]->evidenceTags($1.($2+1).$3) if
${$gg->list}[$i]->evidenceTags =~ /^(.*)(\d+)(.*)$/;
;
 }
}
$out="";
$gn->toText(\$out);
print OUT $out;


#delimiter
$gn->lowercase;
$out="";
$gn->toText(\$out);
print OUT $out;

my $gn2=SWISS::GNs->fromText(\"GN   A{EA1} or B{EA2}.\n",1);
$out="";
$gn2->toText(\$out);
print OUT $out;

$gn2=SWISS::GNs->fromText(\"GN   Timeo danaos, and dona ferentes.\n",1);
$gn2->and(" et ");
$out="";
$gn2->toText(\$out);
print OUT $out;

#remove GN
$gn->head->pop;
$out="";
$gn->toText(\$out);
print OUT $out;


$gn->head->set;
$out="";
$gn->toText(\$out);
print OUT $out;


$gn->head->set;
$out="";
$gn->toText(\$out);
print OUT $out || "(Nothing)\n";


#remove genegroups
$gn=SWISS::GNs->fromText(\$text,1);
@{$gn->list}=();
$out="";
$gn->toText(\$out);
print OUT $out || "(Nothing)\n";

#adding genegroups
@{$gn->list} = SWISS::GeneGroup->fromText("Wallace OR Gromit");
$out="";
$gn->toText(\$out);
print OUT $out;


#wrapping
push @{$gn->list}, SWISS::GeneGroup->fromText("So long vict OR ious, happy 'n gl OR ious, long to reign over us");
$out="";
$gn->toText(\$out);
print OUT $out;

unshift @{$gn->list}, SWISS::GeneGroup->fromText("Foobar");
$out="";
$gn->toText(\$out);
print OUT $out;

$gn->is_old_format(0);
$out="";
$gn->toText(\$out);
print OUT $out;

$out = ' ' . $out;
$gn = SWISS::GNs->fromText(\$out);
$gn->item(2)->Names->splice (1,1);
$out="";
$gn->toText(\$out);
print OUT $out;


close OUT;
print "checking expected output...\n";

test 2, system('diff', $testout, $expectedout) == 0, "diff $testout $expectedout";





