FROM kbase/sdkbase2:python
MAINTAINER ogaloz@lbl.gov
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.


RUN apt-get update && \
    apt-get install -y aptitude && \
    aptitude update -y && aptitude safe-upgrade -y && \
    apt-get install --yes \
    build-essential \
    apt-utils \
    perl5.24 \
    cpanminus \
    gcc-multilib \
    expat \ 
    libexpat-dev \
    libxml-libxml-perl \
    libssl-dev \
    libnet-ssleay-perl \
    openssl \
    libdb-dev \
    build-essential \
    libdbd-sqlite3-perl \
    sqlite3 \
    wget \
    cmake


RUN cpanm LWP::UserAgent \
    YAML \
    Getopt::Long \
    FindBin \
    File::Which \
    IO::Handle \
    JSON && \
    cpan XML::Parser::PerlSAX && \
    cpanm POSIX \
    Time::HiRes \
    LWP::Simple \
    URI::Escape \
    CGI \
    DBI \
    XML::DOM::XPath 

RUN chmod o+r /etc/resolv.conf && \
    mkdir /test && \
    apt-get install -y git curl libio-socket-ssl-perl libnet-ssleay-perl && \
    apt-get install build-essential checkinstall zlib1g-dev -y

RUN cpanm --force Net::SSLeay \
    IO::Socket::SSL \
    DB_File \
    LWP::Protocol::https \
    Error XML::Writer \
    IO::String \
    Set::Scalar \
    XML::Twig Test::Memory::Cycle \
    XML::SAX::Writer \
    Test::Most \
    IPC::Run \
    List::MoreUtils \
    Test::Weaken \
    Module::Build \
    IO::Scalar \
    Data::Stag \
    Graph::Directed \
    Probe::Perl \
    Test::Script \
    Importer \
    Term::Table \
    Module::Pluggable \
    Scope::Guard \
    Sub::Info \
    Test2::V0 \
    Carton && \
    cpan install DBD::SQLite module

RUN wget https://github.com/morgannprice/PaperBLAST/archive/master.zip && \
    unzip master.zip && \
    mv PaperBLAST-master PaperBLAST && rm master.zip

RUN wget https://github.com/soedinglab/MMseqs2/archive/master.zip && \
    unzip master.zip && \
    mv MMseqs2-master PaperBLAST/mmseqs && rm master.zip && \
    cd PaperBLAST/mmseqs && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=. .. && \
    make -j 4 && \
    make install

RUN mv PaperBLAST/mmseqs / && \
    mv mmseqs/build PaperBLAST/mmseqs && \
    mkdir PaperBLAST/bin/blast

RUN wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/2.2.18/blast-2.2.18-ia32-linux.tar.gz && \
    tar zxvf blast-2.2.18-ia32-linux.tar.gz && \
    mv blast-2.2.18/bin/bl2seq PaperBLAST/bin/bl2seq && \
    mv blast-2.2.18/bin/blastall PaperBLAST/bin/blast/blastall && \
    mv blast-2.2.18/bin/fastacmd PaperBLAST/bin/blast/fastacmd && \
    mv blast-2.2.18/bin/formatdb PaperBLAST/bin/blast/formatdb

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module


WORKDIR /kb/module

RUN make all

RUN ls

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
