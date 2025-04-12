# Traffic Rules Games Dashboard & Games

## Overview

This repository contains three main components:

1. **Car Mode Game** (`main.py`):  
   A traffic rules simulator built with the **Ursina** game engine.  
2. **Pedestrian Crossing Game** (`pedestrian.py`):  
   A AAA‑style pedestrian crossing game built with **Pygame**.  
3. **Dashboard Launcher** (`dashboard.py`):  
   A **PyQt5**‑based graphical dashboard to launch either game.

A `requirements.txt` file is provided to install all necessary dependencies.

---

## Prerequisites

- Python 3.7 or higher
- Git (optional, for cloning the repo)

---

## Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/Praveen17143/traffic_smart
   cd traffic-rules-games
   ```

2. **Create and activate a virtual environment**:
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Running the Games

### 1. Dashboard Launcher

The easiest way to launch either game is via the PyQt5 dashboard:

```bash
python dashboard.py
```

- Click **Car Mode** to start the Ursina-based car game.
- Click **Pedestrian Mode** to start the Pygame-based pedestrian crossing game.

### 2. Direct Game Launch

Alternatively, you can run each game directly:

- **Car Mode**:
  ```bash
  python main.py
  ```

- **Pedestrian Crossing**:
  ```bash
  python pedestrian.py
  ```

---

## Project Structure

```
.
├── assets/
│   ├── background.jpg
│   ├── car_icon.png
│   └── ped_icon.png
├── main.py            # Ursina car game
├── pedestrian.py      # Pygame pedestrian game
├── dashboard.py       # PyQt5 dashboard launcher
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## Dependencies

All Python dependencies are listed in `requirements.txt`, including:

- **ursina**  
- **pygame**  
- **PyQt5**  
- (Optional) **pillow**, **numpy**  

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Ursina Engine** for making 3D Python game development accessible.  
- **Pygame** community for tutorials and support.  
- **Qt** for the powerful cross-platform GUI toolkit.  
