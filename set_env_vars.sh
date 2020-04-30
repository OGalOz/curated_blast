#!/bin/bash

chome=$PWD
impl=$PWD/lib/curated_blast/curated_blastImpl.py
tst=$PWD/test/curated_blast_server_test.py
mymod=$PWD/lib/curated_blast/altered_files/
util_dir=$PWD/lib/cb_util
tmp_dir=$PWD/test_local/workdir/tmp/
ui_dir=$PWD/ui/narrative/methods/run_curated_blast/
udisp=$ui_dir/display.yaml
uspec=$ui_dir/spec.json
mycmd='open -a "Google Chrome" '$tmp_dir'/cb_out.html'
#test_cmd=$(eval "$mycmd")
