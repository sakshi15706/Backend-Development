Measured on: Intel(R) Xeon(R) Processor @ 2.10GHz x2, Node v22.23.5, 2026-11-24T06:13:45.574Z
Settings: 50 connections, 30 s per scenario after a 3 s warm-up (discarded), fresh server process per scenario.

| Scenario | req/s | client p50 (ms) | client p99 (ms) | server p50 / p95 / p99 (ms) | errors | event-loop p99 over baseline (ms) | RSS (MB) |
|---|---|---|---|---|---|---|---|
| A. baseline /api/ping (run 1) | 9980 | 4 | 12 | 0.052 / 0.112 / 0.259 | 0 | 8.819 | 129.336 |
| B. baseline /api/ping (run 2, same settings) | 9762 | 4 | 12 | 0.052 / 0.114 / 0.255 | 0 | 9.475 | 129.848 |
| C. /api/ping + 50 ms await (slow "database") | 972 | 51 | 56 | 50.767 / 52.273 / 54.553 | 0 | 2.839 | 118.027 |
| D. /api/ping + 5 ms synchronous CPU block | 189 | 260 | 512 | 5.144 / 5.235 / 5.456 | 0 | 252.105 | 106.598 |
| E. /api/attendance (PBL endpoint, 200 rows) | 5917 | 7 | 16 | 0.116 / 0.203 / 0.282 | 0 | 11.85 | 131.867 |
