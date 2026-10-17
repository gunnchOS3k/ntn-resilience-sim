# Metrics and Baselines

## Metrics

| Metric | Unit | Description |
|--------|------|-------------|
| Latency | ms | End-to-end delay from source to destination |
| Jitter | ms | Variation in latency over time |
| Packet loss | % | Fraction of packets not delivered |
| Throughput | Mbps | Effective data rate achieved |
| Reliability | % | Fraction of transmissions successfully completed |
| NTN handover delay | ms | Service interruption during beam or satellite handover |
| Outage duration | s | Total time without connectivity |
| Recovery time | s | Time from failure detection to restored service |
| Availability windows | min/hour | Fraction of time NTN link is usable |
| Energy per transmission | mJ | Energy consumed per successful data delivery |

## Baselines

### Terrestrial-Only (No NTN)

No satellite or HAPS fallback available. When terrestrial fails, service is lost until terrestrial recovers. Represents worst-case for NTN-relevant scenarios.

### Local-Only / Offline (No WAN)

Edge node operates independently with no wide-area connectivity. Services limited to locally cached data and local compute. Represents isolation behavior.

### No-Adaptation (Static Network)

Network configuration does not change in response to link failure or degradation. Fixed routing, fixed timeouts, no priority adjustment. Represents naive deployment.

### Cloud-Only (No Local Edge)

All processing and storage in remote cloud. No local fallback when WAN is disrupted. Represents maximum WAN dependency.

## Sample Evaluation Table

| Scenario | Metric | Terrestrial-Only | Local-Only | No-Adaptation | Cloud-Only | NTN-Adaptive |
|----------|--------|-----------------|------------|---------------|------------|--------------|
| Gary Emergency | Recovery time (s) | — | — | — | — | — |
| Ghana Rural | Availability (%) | — | — | — | — | — |
| Guyana Flood | Outage duration (s) | — | — | — | — | — |
| Gaza Humanitarian | Throughput (kbps) | — | — | — | — | — |
| Graham Land | Delivery delay (min) | — | — | — | — | — |

## Limitations

- **Simulated environment**: All metrics are collected from simulation, not live networks
- **Modeled parameters**: NTN link characteristics are derived from published specifications
- **No live access required**: Results do not depend on operational satellite or HAPS systems
- **Reproducibility**: All experiments are designed to be reproducible from configuration files and scripts
