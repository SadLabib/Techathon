# System Diagram

Deliverable #1 (15%). **Do not use Mermaid** — the brief forbids it. Draw it in
**Excalidraw** or **draw.io** and export a PNG here.

## What to put in this folder

- `system-diagram.png` — the exported image (referenced from the root README)
- `system-diagram.excalidraw` (or `.drawio`) — the editable source

## What the diagram must show

The full flow of information, matching [`../architecture.md`](../architecture.md):

```
[Simulated Device Layer] -> [Backend: Store + Simulator + Alert Engine + API/WS]
      -> [ Web Dashboard ] && [ Discord Bot ] -> [ User ]
```

Include, with labelled arrows:

- Simulator → State Store (the single source of truth)
- State Store → Alert Engine
- Backend → Dashboard over **WebSocket** (live) and **REST** (initial load)
- Backend → Discord Bot over **REST**
- The **proactive alert** path: Alert Engine → Bot → Discord channel

A reviewer should be able to trace one device flip all the way to both a
dashboard tile and a Discord message.
