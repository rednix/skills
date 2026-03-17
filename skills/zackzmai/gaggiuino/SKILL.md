---
name: gaggiuino
description: Professional control and deep analysis skill for Gaggiuino-modified espresso machines. Supports real-time monitoring, 2Hz high-fidelity shot analysis (Flow vs Pressure profiles), profile management, and full hardware settings configuration. Triggers on keywords like 咖啡机, coffee machine, 咖啡豆, espresso, 萃取, Gaggiuino, 配方, 曲线, shot, brewing, 拉花, 冲煮, turbo shot, 超萃, extraction analysis.
---

# Gaggiuino Skill

Professional tool for monitoring, controlling, and performing deep diagnostic analysis on Gaggiuino-modified Gaggia Classic espresso machines via the REST API.

## Core Analysis Protocol (Target vs Limit)
To prevent misinterpretation of advanced espresso profiles (like Turbo Shots), you **MUST** differentiate between "Targets" and "Limits" based on the phase `type`:

> [!IMPORTANT]
> - **Flow Profiles (`type: flow`)**:
>     - **Primary Target**: `tf` (targetPumpFlow).
>     - **Static Limit**: `tp` (targetPressure). 
>     - **Evaluation**: The shot is successful if actual flow `f` aligns with `tf`. Low pressure is expected and correct unless it hits the `tp` ceiling. Do NOT suggest increasing pressure if flow targets are met.
> - **Pressure Profiles (`type: pressure`)**:
>     - **Primary Target**: `tp` (targetPressure).
>     - **Static Limit**: `restriction` / `tf`.
>     - **Evaluation**: The shot is successful if actual pressure `p` aligns with `tp`.

## Prerequisites
- **Network**: Gaggiuino must be on the same Local Area Network (LAN) as the OpenClaw host.
- **Base URL**: Defaults to `http://gaggiuino.local`. 
    - *Tip*: If connection fails (mDNS issues), guide the user to find the machine's IP address in their router settings. Once provided, update the `GAGGIUINO_BASE_URL` environment variable or the script's default.
- **Firmware**: Requires Gaggiuino firmware with REST API support (v3.0+ recommended for Settings API).

## Commands Reference

All interactions are handled via the wrapper script: `scripts/gaggiuino.sh`

| Command | Argument | Description |
| :--- | :--- | :--- |
| `status` | - | Real-time sensor data (Temp, Pressure, Weight, Water) |
| `profiles` | - | Lists all stored brewing profiles with IDs |
| `select-profile` | `<id>` | Activates a specific profile for the next shot |
| `latest-shot` | - | High-fidelity (2Hz) analysis of the most recent extraction |
| `shot` | `<id>` | Detailed analysis of a specific historical shot |
| `get-settings` | `[cat]` | View hardware config (boiler, system, led, scales, display, theme) |
| `update-settings`| `<cat> <json>`| Update hardware settings (Requires full category JSON) |

## Units & Data Handling
The API returns data in "deci-units" (1/10th), which this skill automatically converts to standard units for AI analysis:
- **Pressure**: bar
- **Temperature**: °C
- **Weight**: grams (g)
- **Flow**: ml/s (Pump) and g/s (Weight Flow)

## AI Behavior & Analysis Guidelines

- **Response Language**: Always respond in the **same language used by the user** in their prompt (e.g., return Chinese analysis if asked in Chinese, English if asked in English).
- **Shot Diagnostics**: 
    - **Phase Alignment & Transitions**: Correlate the **2Hz `data_2hz`** time-series with the defined `phases`. Pay strict attention to exit conditions (e.g., stopping Pre-infusion at a specific weight or pressure). If a weight-based transition happens too quickly, flag the grind as potentially too coarse.
    - **Bloom & Saturation Health**: For profiles featuring a "Bloom" or "Hold" phase (e.g., Low-High-Low, Phiynic), analyze the pressure decay. A smooth, gradual pressure drop indicates proper puck saturation. A rapid pressure crash to 0 indicates severe channeling or a fractured puck.
    - **Channeling vs. Normal Puck Degradation**:
        - *Pressure Profiles*: A sudden spike in `wf` (Weight Flow) accompanied by a struggle to maintain `p` (Pressure) = **Channeling**.
        - *Flow Profiles*: A smooth, continuous decline in `p` while actual flow `f` matches target `tf` = **Normal puck degradation** (decreasing resistance as solubles extract). Do NOT flag this as channeling. A sudden, cliff-edge drop in `p` = **Puck fracture / Channeling**.
    - **Scale Noise Tolerance**: Understand that vibration pumps introduce mechanical noise to the drip tray scales. When analyzing `wf` for channeling, evaluate moving average trends over 1-1.5 seconds (2-3 data points) rather than reacting to a single 0.5s anomalous spike.
    - **Thermal Stability Check (Brew Delta)**: For high-yield, high-flow profiles (e.g., The Soup Kitchen, Turbo Shots), check if the temperature `t` significantly sags below the target during the main extraction phase. If persistent sag is detected, suggest the user review their `Brew Delta` hardware settings.
- **Settings Safety**: When updating settings, ALWAYS `get-settings <category>` first to capture the current state, modify only the delta, and then `update-settings` with the full payload.
- **Readiness**: When asked if the machine is "ready", check `status` for temperature stability and water level.
- **Connection Troubleshooting**: If a connection error occurs, explain that `gaggiuino.local` might not be supported by their router and proactively offer to help the user set a manual IP once they retrieve it from their router's device list.

---
*Path to script: `skills/gaggiuino/scripts/gaggiuino.sh`*
