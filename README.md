# zero-copy-vwap-engine
```
[Simulated WebSocket Feed]
        │  asyncio — catches raw ticks fast, never blocks
        ▼
[Shared Memory Ring Buffer]  ← mmap'd memory, all processes see it
        │
   ┌────┴────┬─────────┐
[Worker 0] [Worker 1] [Worker 2]  ← real OS processes, real cores
     │           │          │        each does vectorized VWAP math
     └────┬──────┘          │        on their slice of ticks
          ▼                 ▼
    [Results Table]   [Results Table]
          │
          ▼
    [Main Process — merge all results → final VWAP per ticker]
```
