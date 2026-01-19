# Race Simulator
A Python-based Formula 1 race engine that simulates full Grand Prix weekends — including qualifying, multi-lap racing, overtakes, driver mistakes, reliability issues, pace variance, and car–track interaction.  
The project models race dynamics using probabilistic behavior, object-oriented design, and tuning parameters inspired by real F1.

---

## Overview
**Race Simulator** is a single-file Python simulation of an F1 race.  
It uses **object-oriented modeling** (Cars, Drivers, Tracks, Race) and **probabilistic event generation** to produce realistic racing scenarios:

- Lap time variation based on driver consistency  
- Overtake attempts governed by racecraft vs. awareness  
- Track-dependent performance scaling (cornering vs. straight-line speed)  
- Reliability issues and mistakes with random timing penalties  
- Multi-pass overtaking logic checked each lap until stable  
- Automatic qualifying session + race start grid with grid penalties  

The result is a dynamic and largely unpredictable race — similar to how real F1 events unfold.

## Key Features

### Car & Driver Performance Modeling
- Cars modeled with **speed**, **cornering**, **reliability**
- Drivers modeled with **pace**, **awareness**, **racecraft**, **consistency**
- Grid penalties automatically applied and compensated with pace buffs, as a high-risk high-reward system

### Probabilistic Simulation Engine
- Lap variation generated via:
  - consistency-based randomness  
  - small random oscillations for “race flow”  
  - occasional driver errors with ~1.5–4s penalty  
  - probabilistic reliability failures  

### Track Effects
Each track defines:
- **Cornering bias** (0–99 scale: 50 = equal weighting)
- **Overtake friendliness** (probability modifier)

These parameters directly influence:
- relative car performance  
- overtaking windows  
- lap time profiles  

### Multi-Pass Overtake Logic
After each lap:
- Every driver pair is checked from front → back
- Overtakes occur if:
  - gap < 0.15s **and** overtake probability is met, **or**  
  - the trailing driver has a very large pace advantage  
- If any overtake occurs, the loop repeats until stable

This produces realistic multi-pass battles.

### Qualifying Session
- Increased inconsistency, quicker raw laps   
- Greatly reduced chance of reliability events  
- Automatically sorts and displays results  
- Applies grid penalties correctly  

## Architecture

The system uses a clean, extensible OOP structure:

```
Track      → defines circuit characteristics  
Car        → defines mechanical performance  
Driver     → composes a Car and adds human factors  
Race       → orchestrates qualifying + multi-lap race  
```

Each class has a clearly defined responsibility.

## Installation

Requires Python 3.8+.

```bash
git clone https://github.com/shrisay/race-simulator
cd race-simulator
python3 simulator.py
```

No external dependencies required.

## Usage

To run the simulator, simply execute the Python file:

```bash
python simulator.py
```

Example output:

```
🏁 Qualifying Session 🏁 - Silverstone
1. Verstappen   | Red Bull  | 89.482s | +0.000s
2. Leclerc      | Ferrari   | 89.601s | +0.119s
...

🏁 Race Start! 🏁 - Silverstone
--- Lap 1 ---
Hamilton overtook Norris!
Leclerc made a mistake!
...
```

To customize the race:

```python
race = Race(drivers, 50, monza)  # List of drivers, laps, racetrack
race.qualify()
race.simulate()
```

## File Structure

Since this is a single-file project, everything is located in:

```
simulator.py
README.md
```

## Future Improvements
- Tyre model (soft/medium/hard with degradation curves)  
- Safety cars & DRS zones  
- Visualizer (matplotlib live gap chart or Tkinter GUI)  
- Constructor standings across multiple races  
- JSON/YAML input for custom driver/car/track definitions  

---

## Example
The repository includes an example output file to demonstrate what a full qualifying session and race simulation look like.


