
FROM perl:5.24-slim-threaded

MAINTAINER Omree Gal-Oz <ogaloz@lbl.gov>

RUN apt-get update


RUN apt-get install --yes \
    build-essential \
    gcc-multilib \
    apt-utils \
    perl \
    expat \ 
    libexpat-dev

RUN apt-get install -y cpanminus

RUN cpanm LWP::UserAgent \
    XML::Parser::PerlSAX \
    YAML \
    Getopt::Long \
    FindBin \
    File::Which \
    IO::Handle \
    XML::LibXML \
    JSON
    
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

#RUN apt-cache search libdb

RUN apt-get install --yes libdb-dev

RUN cpanm DB_File

RUN cpanm LWP::Protocol::https

RUN cpanm Error XML::Writer IO::String Set::Scalar XML::Twig Test::Memory::Cycle XML::SAX::Writer Test::Most IPC::Run List::MoreUtils Test::Weaken Module::Build IO::Scalar Data::Stag Graph::Directed

#RUN cpanm BioPerl

COPY . .

RUN bash main_cgi_command.sh  
