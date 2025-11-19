# AgentOS Usage

Documentation is found at: https://buildermethods.com/agent-os/shape-spec

However, I have found that slight modifcations are required to make the best use of AgentOS with OpenAI Codex.

There are two main phases: Create Spec and Implemenation

## Create Spec

```
:: Shape Spec ::

Follow the multi-phase instructions in agent-os/commands/shape-spec/shape-spec.md to shape a new spec called “<Spec name>” Feature description: <description>



:: Write Spec ::
@agent-os/commands/write-spec/write-spec.md run this to write a spec

@agent-os/commands/create-tasks/create-tasks.md run this to create tasks
```

## Implementation

Run the below interatively until all tasks are complete.

```
@agent-os/commands/implement-tasks/implement-tasks.md run this to implement the next task group
```
