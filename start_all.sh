#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Research Ideas Generation Network"
echo "========================================"
echo ""

PIDS=()

echo "[1/7] Starting Network Server..."
openagents network start network.yaml &
NETWORK_PID=$!
PIDS+=($NETWORK_PID)
sleep 3
echo "Network Server started (PID: $NETWORK_PID)"
echo ""

echo "[2/7] Starting Leader Agent..."
openagents agent start agents/leader_agent.yaml &
LEADER_PID=$!
PIDS+=($LEADER_PID)
echo "Leader Agent started (PID: $LEADER_PID)"
sleep 1

echo "[3/7] Starting Domain Agent..."
openagents agent start agents/domain_agent.yaml &
DOMAIN_PID=$!
PIDS+=($DOMAIN_PID)
echo "Domain Agent started (PID: $DOMAIN_PID)"
sleep 1

echo "[4/7] Starting Method Agent..."
openagents agent start agents/method_agent.yaml &
METHOD_PID=$!
PIDS+=($METHOD_PID)
echo "Method Agent started (PID: $METHOD_PID)"
sleep 1

echo "[5/7] Starting Experiment Agent..."
openagents agent start agents/application_agent.yaml &
APPLICATION_PID=$!
PIDS+=($APPLICATION_PID)
echo "Experiment Agent started (PID: $APPLICATION_PID)"
sleep 1

echo "[6/7] Starting Evaluation Agent..."
openagents agent start agents/evaluation_agent.yaml &
EVALUATION_PID=$!
PIDS+=($EVALUATION_PID)
echo "Evaluation Agent started (PID: $EVALUATION_PID)"
sleep 1

echo "[7/7] Starting Refinement Agent..."
python agents/refinement_agent.py &
REFINEMENT_PID=$!
PIDS+=($REFINEMENT_PID)
echo "Refinement Agent started (PID: $REFINEMENT_PID)"
sleep 2

echo ""
echo "========================================"
echo "All agents started successfully!"
echo "========================================"
echo ""
echo "Network running at:"
echo "  - HTTP: http://localhost:8709"
echo "  - gRPC: localhost:8609"
echo ""
echo "Available channels:"
echo "  - leader"
echo "  - discussion"
echo ""
echo "Press Ctrl+C to stop all agents..."
echo ""

cleanup() {
    echo ""
    echo "Stopping all agents..."
    
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "Stopped process $pid"
        fi
    done
    
    sleep 2
    
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
            echo "Force killed process $pid"
        fi
    done
    
    echo "All agents stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

while true; do
    sleep 1
done
