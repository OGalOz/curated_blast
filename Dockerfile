FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

RUN apt-get update

RUN apt-get install -y aptitude

RUN aptitude update -y && aptitude safe-upgrade -y

RUN apt-get install --yes \
    build-essential \
    apt-utils \
    perl5.24 

RUN apt-get install -y cpanminus


RUN apt-get install --yes \
    gcc-multilib \
    expat \ 
    libexpat-dev



RUN cpanm LWP::UserAgent \
    YAML \
    Getopt::Long \
    FindBin \
    File::Which \
    IO::Handle \
    JSON

RUN cpan XML::Parser::PerlSAX


RUN apt-get --yes install libxml-libxml-perl

RUN cpanm POSIX \
    Time::HiRes \
    LWP::Simple \
    URI::Escape \
    CGI

RUN cpanm DBI

RUN apt-get install --yes libssl-dev

RUN apt-get install --yes libnet-ssleay-perl

RUN apt-get install --yes libcrypt-ssleay-perl

RUN apt-get install --yes openssl

RUN cpanm XML::DOM::XPath

RUN chmod o+r /etc/resolv.conf
RUN mkdir /test && apt-get update && apt-get install -y git curl libio-socket-ssl-perl libnet-ssleay-perl
RUN apt-get install build-essential checkinstall zlib1g-dev -y

RUN cpanm --force Net::SSLeay

RUN cpanm IO::Socket::SSL

RUN apt-get install --yes libdb-dev

RUN cpanm DB_File

RUN cpanm LWP::Protocol::https

RUN cpanm Error XML::Writer IO::String Set::Scalar XML::Twig Test::Memory::Cycle XML::SAX::Writer Test::Most IPC::Run List::MoreUtils Test::Weaken Module::Build IO::Scalar Data::Stag Graph::Directed

#RUN cpanm DBD::SQLite module

RUN apt-get -yq install sqlite3

RUN cpanm Probe::Perl Test::Script Importer Term::Table Module::Pluggable Scope::Guard Sub::Info Test2::V0

RUN apt-get install build-essential

RUN apt-get install -y libdbd-sqlite3-perl

RUN cpanm Carton

RUN cpan install DBD::SQLite module

RUN apt-get install -y wget


#Installing Database
RUN wget http://papers.genomics.lbl.gov/data/uniq.faa

RUN wget http://papers.genomics.lbl.gov/data/litsearch.db

RUN wget http://papers.genomics.lbl.gov/data/stats

RUN wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/2.2.18/blast-2.2.18-ia32-linux.tar.gz && tar zxvf blast-2.2.18-ia32-linux.tar.gz && blast-2.2.18/bin/formatdb -p T -o T -i uniq.faa && ls

#RUN apt-get install -y python3-pip python3-dev

#RUN pip3 install biopython


# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

RUN ln /stats /litsearch.db /uniq.* /kb/module/lib/PaperBLAST/data/

RUN ls /kb/module/lib/PaperBLAST/data/

WORKDIR /kb/module

#RUN mv /root/uniq.faa /root/litsearch.db /root/stats kb/module/data

RUN make all

RUN ls

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
