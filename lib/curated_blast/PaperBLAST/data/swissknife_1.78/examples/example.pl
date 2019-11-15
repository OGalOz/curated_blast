#!/usr/bin/env perl

use SWISS::Entry;
use SWISS::KW;

# Read an entire record at a time
local $/ = "\n//\n";

while (<>){
  # Read the entry
  $entry = SWISS::Entry->fromText($_);

  # Print the primary accession number of each entry.
  print $entry->AC, "\n";

  # If the entry has a SWISS-2DPAGE crossreference
  if ($entry->DRs->get('SWISS-2DPAGE')) {
    
    # Add the pseudo-keyword 'Gelelectrophoresis'
    my $kw = new SWISS::KW;
    $kw->text('Gelelectrophoresis');
    $entry->KWs->add($kw);
  };
  
  # Print all keywords
  foreach my $kw ($entry->KWs->elements) {
    print $kw->text, ", ";
  }
  print "\n";

  # Print number and Comments for all references
  # (courtesy of Dan Bolser)
  foreach my $ref ($entry->Refs->elements){
    my $rn = $ref->RN;      # Reference Number
    print "RN:\t$rn\n"; 

    my $rc = $ref->RC;      # Reference Comment(s)
    foreach my $type (keys %$rc){ # Comment type
      foreach (@{$rc->{$type}}){  # Comment text
        print join( "\t", "RC:", $type, $_->text), "\n";
      }
    }
  }

  print "\n\n";
}
