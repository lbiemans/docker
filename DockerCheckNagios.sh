#!/bin/bash

for arg in "$@"
do
    case $arg in
        -t|--type)
        TYPE=$2
        shift
        ;;
        -s|--state)
        STATE=$2
        shift
        shift # Remove argument value from processing
        ;;
        *)
        shift # Remove generic argument from processing
        ;;
    esac
done

workercheck (){
if docker info --format '{{json .}}' | jq '.Swarm.LocalNodeState' | grep -q active
 then echo "OK - node is active as a worker in a swarm"
  exit 0
   elif docker info --format '{{json .}}' | jq '.Swarm.LocalNodeState' | grep -q inactive
    then echo "CRITICAL - node is not active as a worker in a swarm"
     exit 2
      else
       echo "UNKNOWN - Should this node be a member in a swarm?"
fi 
}

mastercheck (){
if docker info --format '{{json .}}' | jq '.Swarm.LocalNodeState, .Swarm.ControlAvailable' | grep -q true
 then echo "OK - node is active as a manager in a swarm"
  exit 0
   elif docker info --format '{{json .}}' | jq '.Swarm.LocalNodeState, .Swarm.ControlAvailable' | grep -q false
    then echo "CRITICAL - node is not active as a manager in a swarm"
     exit 2
      else
       echo "UNKNOWN - Should this node be a member in a swarm?"
fi 
}

case "$TYPE" in
	worker) workercheck;;
	master) mastercheck;;
	*) echo START;;
esac

