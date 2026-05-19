# Dynamic Priority Queue Simulation for Emergency Room

## Project Overview

This project simulates an emergency-room queue system and compares different queue management strategies.

The goal is to show how different data structures affect the behavior and performance of a real system.

In an emergency room, treating patients only by arrival order is not always reasonable. A patient with high urgency should usually be treated before a patient with a minor issue, even if the minor case arrived earlier.

## Strategies Compared

The simulation compares three queue strategies:

1. **FIFO Queue**  
   Patients are treated according to arrival order.

2. **Static Priority Queue**  
   Patients are treated according to urgency level.

3. **Dynamic Priority Queue**  
   Patients are treated according to urgency, case type, and waiting time.

## Dynamic Priority Formula

The dynamic priority score is calculated as:

score = 10 * urgency + 3 * case_type_bonus + 0.3 * waiting_time

This formula gives high importance to urgency, while also allowing waiting time to increase a patient’s priority.

## Data Structures Used

- `deque` is used for the FIFO queue.
- `heapq` is used for the priority queues.
- A heap is used because it allows efficient selection of the next highest-priority patient.

Since Python’s `heapq` is a min-heap, the program uses negative priority values so that higher-priority patients are selected first.

## Patient Model

Each patient has:

- patient ID
- arrival time
- urgency level
- case type
- service time

Patients are generated randomly to simulate a dynamic system where patients arrive over time.

## Output Files

When running the program, it creates:

- `patients.csv` – generated patients
- `treatment_order.csv` – treatment order for each strategy
- `simulation_results.csv` – statistical comparison
- `results_summary.txt` – text summary of the results
- `results_chart.html` – visual chart that can be opened in a browser

## Metrics Compared

The strategies are compared using:

- average waiting time
- average waiting time of urgent patients
- maximum waiting time
- number of urgent patients who waited more than 15 time units

## Example Result

Strategy                  Avg wait     Urgent avg     Max wait     Urgent > 15  
FIFO                        94.75          98.48       191.00              23  
Static Priority Queue       98.94           7.60       251.00               5  
Dynamic Priority Queue     100.09           8.24       240.00               6  

## Result Interpretation

FIFO is simple, but it does not handle urgent patients well.

Static Priority Queue greatly improves the waiting time of urgent patients, but it can cause less urgent patients to wait longer.

Dynamic Priority Queue gives a more balanced approach. It still gives high priority to urgent patients, but it also considers waiting time to reduce unfairness.

## How to Run

Run:

python emergency_queue_simulation.py

No external Python libraries are required.

The program uses only built-in Python libraries.

## Why This Project Fits Data Structures

This project demonstrates:

- regular queue behavior
- priority queue behavior
- heap usage
- dynamic priority calculation
- simulation of a real-world system
- comparison between data structure choices
- analysis of performance and fairness

The main idea is that the choice of data structure changes the behavior of the system, not only the implementation.

## Author

Priel Tiran
