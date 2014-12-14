#!/usr/bin/env zsh

scp -r "$1" p-stt-cloud3:vespa-fuzz/vespa
scp -r "$1" p-stt-cloud-sharednode1:vespa-fuzz/vespa
