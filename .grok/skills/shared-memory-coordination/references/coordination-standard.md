# Shared Memory Coordination Standard

This standard defines how all Hermes agents coordinate tasks and state via the shared Mem0 coordination bus.

## 1. Task List Representation
- Tasks are represented as JSON blobs stored in Mem0.
- All agents must adhere to the following schema for active tasks:
  `{ "id": "task-id", "category": "category", "description": "task description", "status": "pending|in_progress|completed", "assigned_to": "agent_id" }`

## 2. Shared Todo Coordination
- Agents must prefix todo logs with `[MEM0_TODO_LOG]` before writing to the shared bus.
- When an agent updates a task status, it must write `[MEM0_STATUS_UPDATE]` to signal the change.

## 3. End of Day Reconciliation
- At the end of each day, the Automation Manager (this profile) reconciles the active list in `tracking/standup.md` and pushes the final state to Mem0 as `[MEM0_EOD_STATE]`.
- All agents should append their completed tasks to the daily `[MEM0_COMPLETED_LOG]` memory.
