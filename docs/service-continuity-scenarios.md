# Service Continuity Scenarios

## Gary Emergency

**Context**: Infrastructure failure in urban/suburban environment where local edge keeps operating but terrestrial WAN is severed. NTN provides WAN connectivity.

- **Connectivity conditions**: Local edge operational, terrestrial WAN down, NTN (LEO satellite) for backhaul
- **Device workloads affected**: Emergency dispatch, hospital data sync, utility SCADA, public safety communications
- **Service profiles stressed**: Low-latency command/control, periodic bulk sync, real-time voice/video
- **Expected degradation behavior**: Local services continue uninterrupted; WAN-dependent services experience increased latency (20-600ms added), reduced throughput, potential packet loss during handovers; priority queuing becomes critical

## Ghana Rural Fallback

**Context**: Sparse terrestrial infrastructure with satellite backhaul as primary or only WAN option for rural communities.

- **Connectivity conditions**: Limited/no terrestrial backhaul, satellite (LEO/GEO) as primary WAN, intermittent availability windows
- **Device workloads affected**: Health clinic data upload, agricultural monitoring, education content delivery, mobile money transactions
- **Service profiles stressed**: Store-and-forward, delay-tolerant bulk transfer, interactive sessions during availability windows
- **Expected degradation behavior**: Services designed around availability windows function normally; interactive services degrade significantly outside windows; local caching and pre-positioning become essential

## Guyana Flood Resilience

**Context**: Weather disruption destroying terrestrial infrastructure, creating NTN-only periods for affected regions.

- **Connectivity conditions**: Terrestrial infrastructure destroyed by flooding, NTN-only connectivity, weather-impacted link quality
- **Device workloads affected**: Disaster coordination, search and rescue communications, population tracking, supply chain logistics
- **Service profiles stressed**: Burst communications, location reporting, image/video upload for damage assessment, coordination messaging
- **Expected degradation behavior**: Complete terrestrial outage forces all traffic through NTN; weather affects link margins; priority traffic must preempt; store-and-forward for non-urgent data; energy constraints on devices

## Gaza Humanitarian

**Context**: Near-zero fixed infrastructure, mesh networking between devices with satellite uplink for external connectivity.

- **Connectivity conditions**: No terrestrial infrastructure, device-to-device mesh, satellite gateway nodes, severely constrained bandwidth
- **Device workloads affected**: Medical records, aid distribution tracking, family reunification databases, situation reporting
- **Service profiles stressed**: Minimal-bandwidth essential services, text-based communications, compressed data sync, offline-first with opportunistic upload
- **Expected degradation behavior**: Extreme bandwidth constraints force aggressive compression and prioritization; mesh introduces variable multi-hop latency; satellite windows create sync bursts; most services operate offline-first

## Graham Land Polar

**Context**: LEO satellite passes only, with store-and-forward as primary communication paradigm for polar research stations.

- **Connectivity conditions**: LEO passes only (minutes per orbit), no terrestrial, no GEO visibility at high latitude, predictable but brief windows
- **Device workloads affected**: Scientific data upload, station telemetry, personnel communications, weather observations
- **Service profiles stressed**: Scheduled bulk transfer during passes, store-and-forward messaging, time-insensitive large data, brief interactive windows
- **Expected degradation behavior**: All communications are pass-scheduled; data queues between passes; interactive services limited to pass duration; priority determines upload order; missed passes delay delivery by orbital period
