# Training Planner

**Author:** Кирилл

## Description
Training Planner is a desktop GUI application built with Python and Tkinter.  
It helps users log their workouts, filter them by type and date, and persist data using JSON files.

### Features
- Add new workouts (date, type, duration)
- Filter by workout type and by exact date
- Input validation:
  - Date must be in `YYYY-MM-DD` format
  - Duration must be a positive number
- Automatic save after each addition (also manual Save/Load buttons)
- Persistent storage in `workouts.json`
- Clean and simple interface

## Requirements
- Python 3.6 or higher (no external libraries – only `tkinter` which is included with standard Python)

## Installation & Usage

1. Clone the repository or download the files:
   ```bash
   git clone https://github.com/yourusername/training_planner.git
   cd training_planner
