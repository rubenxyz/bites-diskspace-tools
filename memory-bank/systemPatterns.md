# System Patterns

The `prores-tools` application follows a modular, command-based architecture. The core logic is decoupled from the command-line interface, which allows for easier testing and maintenance.

## Architecture Diagram

```mermaid
graph TD
    subgraph "prores_tools"
        A[cli.py] --> B[converter.py];
        A --> C[trasher.py];
        A --> D[reporter.py];
        A --> E[utils.py];

        B[converter.py] --> E[utils.py];
        C[trasher.py] --> E[utils.py];
        D[reporter.py] --> E[utils.py];
    end

    subgraph "Commands"
        F[convert] --> B;
        G[cleanup] --> C;
        H[report] --> D;
        I[verify] --> E;
    end

    A --> F;
    A --> G;
    A --> H;
    A --> I;
```

