# Dynamic Priority Queue Simulation for Emergency Room

## Author

Priel Tiran

## AI Usage Disclosure

AI tools were used during the development of this project using Chat GPT for assistance with code structure, debugging, documentation, and improving the explanation of the simulation.

The final implementation was reviewed, tested, and understood by the author.  
All design choices, simulation logic, data structures, and results were checked and explained by the author.

---

## Project Overview

This project simulates an emergency-room queue system and compares different queue management strategies.

The goal of the project is to demonstrate how the choice of data structure affects the behavior and performance of a real system.

In an emergency room, treating patients only by arrival order is not always reasonable. A patient with high urgency should usually be treated before a patient with a minor issue, even if the minor case arrived earlier.

For this reason, the project compares a regular FIFO queue with two priority-based queue strategies.

---

## Simulation Model

The simulation generates patients randomly over time.

Each patient has:

- Patient ID
- Arrival time
- Urgency level
- Case type
- Service time

The arrival process is dynamic. Patients do not all arrive at the beginning of the simulation. Instead, they enter the system at different times, which makes the simulation closer to a real queue system.

The case types used in the simulation include:

- Minor injury
- Regular check
- High fever
- Chest pain
- Breathing issue

Each case type has a different priority bonus and a different service-time range.

For example, a breathing issue receives a higher case-type bonus than a minor injury because it represents a more urgent medical condition.

---

## Queue Strategies Compared

The simulation compares three queue management strategies.

### 1. FIFO Queue

FIFO means First In, First Out.

In this strategy, patients are treated only according to arrival order.

The first patient who arrives is the first patient treated.

This strategy is simple and fair in terms of arrival time, but it does not consider medical urgency.

Implementation:

- Python data structure: `collections.deque`
- New patients are inserted using `append()`
- The next patient is selected using `popleft()`

---

### 2. Static Priority Queue

In this strategy, patients are treated according to their urgency level.

Patients with higher urgency are selected before patients with lower urgency.

This strategy improves the treatment of urgent patients, but it may cause less urgent patients to wait for a very long time.

This problem is known as starvation.

Implementation:

- Python data structure: `heapq`
- Priority is based mainly on urgency level
- Since Python `heapq` is a min-heap, negative priority values are used so that higher-priority patients are selected first

---

### 3. Dynamic Priority Queue

In this strategy, the priority is not based only on urgency.

The priority score is recalculated over time using:

- Urgency level
- Case type bonus
- Waiting time

The purpose of this strategy is to balance between medical urgency and fairness.

Static priority is very good for urgent patients, but it can push low-priority patients backward for too long.  
Dynamic priority solves this by allowing waiting time to gradually increase a patient’s priority.

---

## Dynamic Priority Formula

The dynamic priority score is calculated as:

score = 10 * urgency + 3 * case_type_bonus + 0.3 * waiting_time

Where:

- `urgency` is the medical urgency level of the patient
- `case_type_bonus` gives extra weight to more serious case types
- `waiting_time` increases the priority of patients who have waited longer

The urgency level receives the largest weight because medical urgency should remain the most important factor.

Waiting time receives a smaller weight because it should improve fairness without completely overriding medical urgency.

---

## Why Dynamic Priority Is Needed

A static priority queue can strongly reduce the waiting time of urgent patients.

However, it may create a fairness problem: patients with lower urgency can wait for a very long time if new urgent patients keep arriving.

The dynamic priority queue was added to address this problem.

It keeps urgent patients near the front of the queue, but also increases the priority of patients who have waited for a long time.

This creates a trade-off between:

- Treating urgent patients quickly
- Reducing extreme waiting times
- Making the queue more fair

---

## Data Structures Used

The project uses the following data structures:

### Queue

Used for the FIFO strategy.

Implemented with:

`collections.deque`

This allows efficient insertion at the end of the queue and removal from the front.

### Priority Queue

Used for the static and dynamic priority strategies.

Implemented with:

`heapq`

A heap allows efficient selection of the next highest-priority patient.

Because Python’s `heapq` is a min-heap, the code inserts negative priority scores in order to select the highest-priority patient first.

### Dictionaries

Used to store case-type information, such as:

- Priority bonus
- Minimum service time
- Maximum service time

---

## Output Files

After running the program, an `output` folder is created.

The program generates the following files:

### Main CSV Files

- `patients.csv`  
  Contains the randomly generated patients.

- `treatment_order.csv`  
  Shows the order in which patients were treated under each strategy.

- `simulation_results.csv`  
  Contains the main statistical comparison between the strategies.

- `waiting_distribution.csv`  
  Contains the distribution of waiting times by time ranges.

- `arrival_timeline.csv`  
  Shows how many patients arrived in each time interval.

### Summary File

- `results_summary.txt`  
  A readable text summary of the simulation results.

### HTML Visualization Files

- `results_chart.html`  
  Shows the main comparison between the strategies.

- `arrival_timeline.html`  
  Shows the patient arrival process over time.

- `waiting_distribution.html`  
  Shows the distribution of waiting times for each strategy.

The HTML files can be opened directly in a browser.

No external Python libraries are required.

---

## Metrics Compared

The strategies are compared using several metrics:

- Average waiting time
- Average waiting time of urgent patients
- Maximum waiting time
- Number of urgent patients who waited more than 15 time units
- Distribution of waiting times
- Patient arrival timeline

The distribution analysis is important because averages alone can hide extreme cases.

For example, two strategies may have similar average waiting time, but one strategy may still cause many patients to wait for a very long time.

---

## Example Result

Example output from one simulation run:

Strategy                  Avg wait     Urgent avg     Max wait     Urgent > 15
FIFO                        94.75          98.48       191.00              23
Static Priority Queue       98.94           7.60       251.00               5
Dynamic Priority Queue      98.69          17.64       213.00              10

---

## Result Interpretation

The FIFO strategy is simple, but it performs poorly for urgent patients.

In FIFO, urgent patients may wait a long time because the queue only follows arrival order.

The Static Priority Queue greatly improves the waiting time of urgent patients. However, it may create starvation for less urgent patients, which is reflected in a high maximum waiting time.

The Dynamic Priority Queue creates a more balanced result. It does not treat urgent patients as aggressively as the static priority method, but it reduces the maximum waiting time and improves fairness by considering waiting time.

The main conclusion is that the choice of data structure and priority model changes the behavior of the system.

---

## How to Run

Make sure Python is installed.

Run the following command:

python emergency_queue_simulation.py

The program uses only built-in Python libraries.

No installation of external packages is needed.

After running the program, open the generated `output` folder and view the HTML files in a browser.

---

## Project Files

Recommended repository structure:

emergency-queue-priority-simulation/
│
├── emergency_queue_simulation.py
├── README.md
│
└── sample_output/
    ├── results_chart.html
    ├── arrival_timeline.html
    ├── waiting_distribution.html
    ├── simulation_results.csv
    ├── waiting_distribution.csv
    └── arrival_timeline.csv

The `sample_output` folder is optional, but it is useful for showing example results without requiring the user to run the program first.

---

## Why This Project Fits a Data Structures Course

This project fits a Data Structures course because it demonstrates:

- FIFO queue behavior
- Priority queue behavior
- Heap usage
- Dynamic priority calculation
- Simulation of a real-world system
- Comparison between different data structure choices
- Analysis of performance and fairness
- The effect of algorithmic design on real system behavior

The project shows that data structures are not only theoretical tools.  
They directly affect how a system behaves in practice.
