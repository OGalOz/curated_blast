use strict;
use Module::Build;

#PPM archive build script
#to build ActivePerl distribution

my $build=Module::Build->new
  ( module_name => 'Swissknife',
    requires => { 'perl' => '5.6.1' },
    dist_version_from => 'lib/SWISS/Entry.pm',
    create_makefile_pl => 'traditional',
    create_readme => 'README',
    license => 'gpl',
    dist_author =>    [
               'Edouard de Castro <edouard.decastro@isb-sib.ch>',
               'Paul Kersey <pkersey@ebi.ac.uk>',
               'Henning Hermjakob <hhe@ebi.ac.uk>',
               'Wolfgang Fleischmann <wfl@ebi.ac.uk>',
             ],
    dist_abstract=> 'Handle entries in Swiss-Prot format',
  );



$build->create_build_script;

