#!/bin/bash

# data directory is always mounted in the /data


check_exists() {
    if ! [ -d $1 ] ; then
        echo "Error initializing reference data; failed on: $1"
        fail=1
    fi
}

safe_execute() {
    cmd=$1
    echo "running $cmd"
    eval $cmd
    ret_code=$?
    if [ $ret_code != 0 ]; then
        echo $2
        exit $ret_code
    fi
}

fail=0

date

# Move to /data - that's got room for the big tar file.
cd /data

echo "Downloading databases from Morgan's website"
safe_execute "wget --no-verbose http://papers.genomics.lbl.gov/data/uniq.faa"  "failed to download reference data!"
safe_execute "wget --no-verbose http://papers.genomics.lbl.gov/data/stats" "failed to download reference data!"
safe_execute "wget --no-verbose http://papers.genomics.lbl.gov/data/litsearch.db"  "failed to download reference data!"
safe_execute "wget --no-verbose ftp://ftp.ncbi.nlm.nih.gov/blast/executables/legacy.NOTSUPPORTED/2.2.18/blast-2.2.18-ia32-linux.tar.gz" "failed to download reference data!"
safe_execute "tar zxvf blast-2.2.18-ia32-linux.tar.gz" "failed to untar reference data!"
safe_execute "  blast-2.2.18/bin/formatdb -p T -o T -i uniq.faa " "failed to reformat data with formatdb"
safe_execute "rm -f blast-2.2.18-ia32-linux.tar.gz" "failed to remove reference data!"
#check_exists formatdb.log
ls

if [ $fail -eq 1 ] ; then
    echo "Unable to run formatdb"
    exit 1
fi
echo "Done preparing reference data"

safe_execute "ln -sf uniq.* stats litsearch.db /kb/module/data/"
safe_execute "mv blast-2.2.18 /kb/module/data/" 

if [ -e "/kb/module/data/uniq.faa" ] ; then
    echo "uniq.faa exists"
else
    echo "uniq.faa does not exist"
    #fail=1
fi
if [ $fail -eq 1 ] ; then
    echo "Unable to move data to proper location"
    exit 1
fi
echo "Done moving reference data."


date

echo "Success.  Writing __READY__ file."
touch __READY__




