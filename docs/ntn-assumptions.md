# NTN Assumptions

All parameters documented here are modeled from published specifications (3GPP TR 38.811, TR 38.821, ITU-R recommendations, and peer-reviewed literature). These are **not** measured from operational systems.

## LEO Satellite

- **Altitude**: 550–1200 km
- **One-way propagation delay**: 20–600 ms (depending on altitude and elevation angle)
- **Orbital pass duration**: 5–15 minutes visible per pass (elevation-dependent)
- **Doppler shift**: Up to ±24 ppm at 550 km altitude
- **Beam footprint**: 50–1000 km diameter
- **Throughput**: Modeled at 1–100 Mbps per beam (shared)
- **Availability**: Intermittent, predictable based on orbital mechanics

## HAPS (High Altitude Platform Station)

- **Altitude**: 20 km (stratospheric)
- **Position**: Quasi-stationary over coverage area
- **One-way propagation delay**: 20–50 ms
- **Coverage diameter**: Up to 200 km
- **Throughput**: Modeled at 10–500 Mbps per platform
- **Availability**: Continuous while deployed (maintenance cycles apply)
- **Advantage**: Lower latency than LEO, wider coverage than terrestrial

## UAV-Assisted

- **Altitude**: 100 m – 10 km
- **Duration**: Short (hours), localized coverage
- **One-way propagation delay**: <5 ms
- **Coverage**: Small cell equivalent, hundreds of meters to few km
- **Throughput**: Modeled at 10–100 Mbps
- **Availability**: Limited by flight time, weather, and operational constraints
- **Use case**: Emergency/temporary coverage augmentation

## Link Budget Margins

- **Clear sky margin**: 3–6 dB
- **Rain fade (LEO, Ka-band)**: 5–20 dB depending on climate zone
- **Atmospheric absorption**: 0.5–2 dB
- **Scintillation**: 1–3 dB at low elevation angles
- **Building penetration**: Not modeled (outdoor terminals assumed)

## Handover Parameters

### Between Satellite Beams

- **Handover trigger**: Signal quality threshold or beam boundary crossing
- **Handover duration**: 50–500 ms modeled
- **Data loss during handover**: 0–2% packet loss modeled
- **Frequency**: Every 1–5 minutes for LEO (beam sweeps ground)

### Terrestrial-to-NTN Transition

- **Detection of terrestrial failure**: 1–10 seconds (configurable)
- **NTN acquisition time**: 1–30 seconds (satellite search and sync)
- **Total switchover time**: 2–40 seconds modeled
- **Service interruption**: Dependent on application buffering and retry logic

## Disclaimer

These are modeled parameters from published specifications, not measured from operational systems. Simulation results characterize expected behavior under these modeled conditions.
