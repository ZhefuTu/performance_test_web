#!/bin/bash
cwd=$(cd `dirname $0` && pwd)
cd $cwd
last_time=$(cat ./last_time.txt)
last_time=${last_time:0}
now_time=$(date +%s)
[[ "$now_time" -lt "$last_time + 300" ]] && exit 1
echo $now_time > ./last_time.txt
files=$(aws s3 ls s3://release-package-stats/performance_data/ --recursive | awk '{print $4}')
for file in $files
do
  local_file=$(echo $file | sed -e 's|performance_data|\/home\/graphsql\/performance_test_web\/perf|g')
  if [[ "$file" == */ ]]
  then
    [[ ! -d "$local_file" ]] && mkdir -p $local_file
  else
    [[ ! -f "$local_file" ]] && curl -o $local_file https://release-package-stats.s3-us-west-1.amazonaws.com/$file 
  fi
done
