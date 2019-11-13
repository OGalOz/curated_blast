#!/bin/bash

. /kb/deployment/user-env.sh



python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cd /data
  curl http://papers.genomics.lbl.gov/data/uniq.faa
  curl http://papers.genomics.lbl.gov/data/litsearch.db
  curl http://papers.genomics.lbl.gov/data/stats
  ../lib/PaperBLAST/bin/blast/formatdb -p T -o T -i uniq.faa
  ln -s * ../lib/PaperBLAST/data/
  if [ -d uniq.faa ] ; then
    touch __READY__
  else
    echo "init failed"
  fi
  cd ..
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
