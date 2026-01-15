# Research Ideas Generation Network

A multi-agent system for generating and evaluating research ideas using OpenAgents framework. This system coordinates specialized agents to produce high-quality research proposals through collaborative workflows.

## Overview

The Research Ideas Generation Network uses a collaborative multi-agent approach to:
- Generate diverse research ideas from multiple perspectives
- Evaluate ideas based on technical feasibility and impact
- Refine and consolidate ideas based on feedback
- Score and rank ideas for final selection

## Architecture

### Agent Types

1. **Leader Agent** (`leader_agent.yaml`)
   - Coordinates the entire idea generation process
   - Delegates tasks to other agents
   - Controls workflow progression
   - Presents final results to users

2. **Generator Agents** (3 specialized agents)
   - **Domain Agent**: Deep dive into the given research domain
   - **Method Agent**: Improves methodology of research ideas
   - **Application Agent** (Experiment Agent): Improves experimental setup of research ideas

3. **Refinement Agent** (`refinement_agent.py`)
   - Checks ideas for methodology and experimental setup issues
   - Provides specific feedback for improvement
   - Coordinates with method and application agents for iterative refinement
   - Supports up to 2 rounds of optimization

4. **Evaluation Agent** (`evaluation_agent.yaml`)
   - Multi-criteria evaluation of research ideas
   - Scoring based on 5 dimensions:
     * Technical Feasibility (weight 25%)
     * Impact (weight 30%)
     * Novelty (weight 20%)
     * Relevance (weight 15%)
     * Clarity (weight 10%)
   - Ranking and selection of top-K ideas
   - Detailed evaluation reports with strengths, weaknesses, and suggestions

## Workflow

The system follows a 6-step iterative workflow:

1. **Domain Agent generates initial ideas**
   - User provides a research domain or topic
   - Domain Agent generates 5 research ideas from domain perspective
   - Ideas include basic problem statement, core idea, and initial methodology/experimental setup

2. **Method Agent improves methodology**
   - Method Agent receives the 5 ideas
   - Improves the methodology section of each idea with detailed research methods
   - Returns enhanced ideas to Leader Agent

3. **Application Agent (Experiment Agent) improves experimental setup**
   - Application Agent receives the 5 ideas with improved methodology
   - Enhances the experimental setup section with specific implementation details
   - Returns refined ideas to Leader Agent

4. **Refinement Agent checks and iteratively improves (up to 2 rounds)**
   - Refinement Agent checks all 5 ideas for methodology and experimental setup issues
   - Provides specific, domain-specific feedback for each idea
   - If issues found, sends back to Method Agent or Application Agent for improvement
   - Process repeats until all ideas pass checks or maximum 2 rounds reached

5. **Evaluation Agent scores and ranks ideas**
   - Evaluation Agent evaluates all ideas on 5 dimensions:
     * Technical Feasibility (1-10, weight 25%)
     * Impact (1-10, weight 30%)
     * Novelty (1-10, weight 20%)
     * Relevance (1-10, weight 15%)
     * Clarity (1-10, weight 10%)
   - Calculates weighted total score and ranks ideas
   - Returns top-K ranked ideas with detailed evaluation

6. **Leader Agent presents final results**
   - Leader Agent formats and presents ranked ideas to user
   - Includes detailed methodology, experimental setup, and evaluation scores
   - Shows strengths, weaknesses, and suggestions for each idea

## Installation

### Prerequisites

- Python 3.8+
- OpenAgents framework installed
- Network access to OpenAgents server

### Setup

1. Clone or navigate to the network directory:
```bash
cd demos/09_research_ideas_network
```

2. Ensure all agent files are in place:
```
demos/09_research_ideas_network/
├── network.yaml
├── agents/
│   ├── leader_agent.yaml
│   ├── domain_agent.yaml
│   ├── method_agent.yaml
│   ├── application_agent.yaml
│   ├── evaluation_agent.yaml
│   └── refinement_agent.py
├── start_all.sh
└── stop_all.sh
```

## Usage

### Starting the Network

Start the network server:

```bash
openagents network start 09_research_ideas_network/network.yaml
```

The network will start on:
- HTTP: `http://localhost:8709`
- gRPC: `localhost:8609`

### Starting Agents

#### Quick Start (Recommended)

Use the provided startup script to start all agents at once:

```bash
./start_all.sh
```

This will start all core components in the correct order:
1. Network Server
2. Leader Agent
3. Domain Agent
4. Method Agent
5. Application Agent (Experiment Agent)
6. Evaluation Agent
7. Refinement Agent

#### Manual Start (For Debugging)

Start each agent in a separate terminal:

```bash
# Leader Agent
openagents agent start 09_research_ideas_network/agents/leader_agent.yaml

# Domain Agent
openagents agent start 09_research_ideas_network/agents/domain_agent.yaml

# Method Agent
openagents agent start 09_research_ideas_network/agents/method_agent.yaml

# Application Agent
openagents agent start 09_research_ideas_network/agents/application_agent.yaml

# Evaluation Agent
openagents agent start 09_research_ideas_network/agents/evaluation_agent.yaml
```

#### Starting Python-based Agents

Start the Refinement Agent:

```bash
python 09_research_ideas_network/agents/refinement_agent.py
```

#### Stopping All Agents

Use the provided stop script:

```bash
./stop_all.sh
```

### Using the System

Once all agents are connected, interact with the Leader Agent to generate research ideas:

1. Send a direct message to the Leader Agent with your research domain/topic
2. The system will automatically:
   - Generate 5 initial ideas from domain perspective
   - Improve methodology using Method Agent
   - Enhance experimental setup using Application Agent
   - Refine ideas through iterative checks (up to 2 rounds)
   - Evaluate all ideas on 5 dimensions and rank them
3. Receive the top-K research ideas with detailed evaluations

## Messaging

- All agents post progress updates to the `discussion` channel (similar to Refinement Agent).
- Channel posting uses `send_channel_message(channel, content)` (note: parameter name is `channel`, not `channel_id`).

## Tool Argument Format

- Tool args must be strict JSON and must be a single line (no raw newlines inside strings; use `\n`).
- Escape any double quotes inside string values (`\"`).
- Do not include extra fields like `reason` in tool arguments; call `finish` with `{}`.

Example interaction:
```
User: I need gait recognition research ideas
Leader: I'll coordinate the generation of research ideas on gait recognition. Let me delegate tasks to our specialized agents...
[... agents work sequentially ...]
Leader: Here are the top 5 research ideas for gait recognition:
1. [Idea 1 with score and details]
2. [Idea 2 with score and details]
...
```

## Configuration

### Network Configuration

Edit `network.yaml` to customize:
- Network ports (HTTP: 8709, gRPC: 8609)
- Agent groups and permissions

### Agent Configuration

Edit individual agent YAML files to customize:
- Model selection
- Instructions and behavior
- Max iterations
- Response patterns

### Evaluation Configuration

Edit the evaluation agent configuration in `agents/evaluation_agent.yaml` to adjust:
- Evaluation dimensions (technical_feasibility, impact, novelty, relevance, clarity)
- Weights for each dimension
- Score ranges (1-10)
- Top-K selection criteria

## Data Structure

### Research Idea Format

```json
{
  "idea_id": "unique_identifier",
  "title": "Research Idea Title",
  "problem": "Problem statement",
  "core_idea": "Core innovation",
  "why_interesting": "Why this is interesting",
  "methodology": "Detailed research methodology",
  "experimental_setup": "Experimental design and setup",
  "challenges": "Potential challenges"
}
```

### Evaluation Result Format

```json
{
  "idea_id": "unique_id",
  "idea_title": "Idea Title",
  "scores": {
    "technical_feasibility": 8.5,
    "impact": 9.0,
    "novelty": 7.5,
    "relevance": 8.0,
    "clarity": 9.0
  },
  "total_score": 8.4,
  "evaluation": {
    "technical_feasibility": {
      "score": 8.5,
      "reasoning": "Detailed reasoning for technical feasibility score"
    },
    "impact": {
      "score": 9.0,
      "reasoning": "Detailed reasoning for impact score"
    },
    "novelty": {
      "score": 7.5,
      "reasoning": "Detailed reasoning for novelty score"
    },
    "relevance": {
      "score": 8.0,
      "reasoning": "Detailed reasoning for relevance score"
    },
    "clarity": {
      "score": 9.0,
      "reasoning": "Detailed reasoning for clarity score"
    }
  },
  "strengths": ["Excellent impact", "Good technical feasibility"],
  "weaknesses": ["Moderate novelty"],
  "suggestions": ["Consider incorporating more innovative elements"]
}
```

## Troubleshooting

### Agents Not Connecting

- Verify the network is running: `openagents network status`
- Check network URL and port in agent configurations
- Ensure passwords match between network and agents

### Ideas Not Generated

- Verify all generator agents are connected
- Check Leader Agent logs for delegation errors
- Ensure agent groups have correct permissions

### Evaluation Not Working

- Verify Evaluation Agent is running: Check agent startup logs
- Check evaluation_agent.yaml configuration
- Ensure event names match: `idea.evaluate` and `idea.evaluated`

## Development

### Adding New Generator Agents

1. Create a new YAML file in `agents/` directory
2. Follow the structure of existing generator agents
3. Add the agent to the appropriate agent group in `network.yaml`
4. Update Leader Agent workflow to include the new agent

### Modifying Evaluation Criteria

Edit the evaluation criteria in `agents/evaluation_agent.yaml` to adjust:
- Evaluation dimensions and their weights
- Score ranges and thresholds
- Evaluation prompts and instructions

The current evaluation uses 5 dimensions:
- Technical Feasibility (weight 25%)
- Impact (weight 30%)
- Novelty (weight 20%)
- Relevance (weight 15%)
- Clarity (weight 10%)

### Customizing Workflow

Modify the workflow in `agents/leader_agent.yaml` to change:
- Agent sequence and coordination
- Number of refinement rounds
- Top-K selection criteria
- Event names and payloads

## License

This project is part of the OpenAgents framework.

## Contributing

Contributions are welcome! Please submit issues and pull requests to the OpenAgents repository.
