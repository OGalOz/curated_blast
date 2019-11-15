use ExtUtils::MakeMaker;

# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.
WriteMakefile(
    'NAME'         => 'SWISS',
    'VERSION_FROM' => 'lib/SWISS/Entry.pm', # finds $VERSION
    'PL_FILES' => {}, # avoid using Build.PL which is only for ActivePerl build
);
