#!/bin/bash
NUM_FRONTEND=10
NUM_STORAGE=10
REDUNDANCY=3
CONTROLLER_PORT=12000
STORAGE_PORT=12500
FRONTEND_PORT=12080

trap "jobs -p | xargs kill ; echo ; echo Shutdown" sigint sigterm

echo Starting controller on port $CONTROLLER_PORT, nodes=$NUM_STORAGE, redundancy=$REDUNDANCY
python controller.py $CONTROLLER_PORT $NUM_STORAGE $REDUNDANCY &
sleep 1

echo Starting $NUM_STORAGE storage nodes on port $STORAGE_PORT and up
for i in $(seq $STORAGE_PORT $((STORAGE_PORT + NUM_STORAGE - 1))); do
python storagenode.py localhost:$CONTROLLER_PORT localhost:$i &
done

echo Starting $NUM_FRONTEND frontend nodes on port $FRONTEND_PORT and up
for i in $(seq $FRONTEND_PORT $((FRONTEND_PORT + NUM_FRONTEND - 1))); do
python frontend.py localhost:$CONTROLLER_PORT localhost:$i &
done

sleep $((NUM_FRONTEND + NUM_STORAGE))
echo
echo
echo "All nodes started up"
echo "Friendly shutdown of all nodes: kill $$"
echo "or ctrl-c in this terminal."

wait

