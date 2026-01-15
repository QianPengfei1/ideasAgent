#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Stopping All Agents"
echo "========================================"
echo ""

echo "Searching for agent processes..."

PIDS=()

pkill -f "openagents network start network.yaml" && PIDS+=($(pgrep -f "openagents network start network.yaml")) || true
pkill -f "openagents agent start agents/leader_agent.yaml" && PIDS+=($(pgrep -f "openagents agent start agents/leader_agent.yaml")) || true
pkill -f "openagents agent start agents/domain_agent.yaml" && PIDS+=($(pgrep -f "openagents agent start agents/domain_agent.yaml")) || true
pkill -f "openagents agent start agents/method_agent.yaml" && PIDS+=($(pgrep -f "openagents agent start agents/method_agent.yaml")) || true
pkill -f "openagents agent start agents/application_agent.yaml" && PIDS+=($(pgrep -f "openagents agent start agents/application_agent.yaml")) || true
pkill -f "openagents agent start agents/evaluation_agent.yaml" && PIDS+=($(pgrep -f "openagents agent start agents/evaluation_agent.yaml")) || true
pkill -f "python agents/refinement_agent.py" && PIDS+=($(pgrep -f "python agents/refinement_agent.py")) || true

sleep 2

echo ""
echo "========================================"
echo "Stop Summary"
echo "========================================"
echo "Processes stopped: ${#PIDS[@]}"
echo "Total processes: 7"
echo ""

if [ ${#PIDS[@]} -eq 0 ]; then
    echo "No running agent processes found."
elif [ ${#PIDS[@]} -lt 6 ]; then
    echo "Some agents may not have been stopped. Check manually if needed."
else
    echo "All agents stopped successfully!"
fi
