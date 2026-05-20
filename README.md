Dynamic Priority Queue Simulation for Emergency Room
Project Overview
This project simulates an emergency-room queue system and compares three queue management strategies.
The goal is to show how choosing a data structure and a priority model changes the behavior of a real system.
In an emergency room, treating patients only by arrival order is not always reasonable. A patient with a serious case should usually be treated before a patient with a minor issue, even if the minor case arrived earlier.
The project is implemented in Python and uses only built-in Python libraries.
---
What the Simulation Does
The program randomly generates patients over time. Each patient has:
patient ID
arrival time
urgency level from 1 to 10
case type
service time
The same generated patients are then tested using three different queue strategies. This makes the comparison fair because all strategies receive the same input.
---
Case Types
The simulation includes several case types:
Minor injury
Regular check
High fever
Chest pain
Breathing issue
Each case type has:
a priority bonus used in the dynamic priority formula
a minimum and maximum treatment time
For example, `Breathing issue` receives a higher priority bonus than `Minor injury`, because it represents a more serious case.
---
Strategies Compared
1. FIFO Queue
FIFO means First In, First Out.
Patients are treated according to arrival order only.
This is implemented using Python's `deque`.
Main operations:
`append()` adds a patient to the end of the queue
`popleft()` removes the patient from the front of the queue
This strategy is simple, but it does not consider urgency.
---
2. Static Priority Queue
Patients are treated according to their urgency level.
A patient with urgency 10 will be treated before a patient with urgency 3.
This is implemented using Python's `heapq`.
Python's `heapq` is a min-heap, so the program inserts negative priority values. This allows the highest urgency patient to be selected first.
This strategy helps urgent patients, but it can cause starvation: less urgent patients may wait too long if urgent cases keep arriving.
---
3. Dynamic Priority Queue
Dynamic Priority Queue uses a priority score that changes over time.
The priority score is calculated as:
```text
score = 10 * urgency + 3 * case_type_bonus + 0.8 * waiting_time
```
Meaning:
`urgency` is the most important factor
`case_type_bonus` gives extra weight to more serious medical cases
`waiting_time` increases the priority of patients who have waited longer
This strategy tries to balance two goals:
treating urgent patients early
reducing starvation and long waiting times for less urgent patients
---
Why Dynamic Priority Is Needed
A static priority queue is useful because it protects urgent patients.
However, it may be unfair to lower-priority patients. If new urgent patients keep arriving, a less urgent patient can wait for a very long time.
The dynamic priority strategy solves part of this problem by increasing a patient's priority as their waiting time grows.
This means the system is not based only on the original urgency level. It also reacts to what happens during the simulation.
---
Output Files
When running the program, it creates an `output` folder with these files:
`patients.csv`  
The generated patients used as input.
`treatment_order.csv`  
The treatment order for each strategy.
`simulation_results.csv`  
Main statistical comparison between the strategies.
`waiting_distribution.csv`  
Distribution of waiting times by ranges.
`arrival_timeline.csv`  
Number of patients arriving in each time range.
`results_summary.txt`  
A readable text summary of all results.
`results_chart.html`  
Main result chart that can be opened in a browser.
`arrival_timeline.html`  
Visual chart of the patient arrival process.
`waiting_distribution.html`  
Visual chart of the waiting time distribution.
---
Metrics Compared
The simulation compares the strategies using:
average waiting time
average waiting time of urgent patients
maximum waiting time
number of urgent patients who waited more than 15 time units
distribution of waiting times
patient arrival timeline
The distribution is important because averages alone can hide important behavior. For example, two strategies can have similar average waiting time but very different numbers of patients who wait extremely long.
---
Example Result
Example result using the default settings:
```text
Strategy                     Avg wait     Urgent avg    Max wait    Urgent > 15
FIFO                            94.75          98.48      191.00             23
Static Priority Queue           98.94           7.60      251.00              5
Dynamic Priority Queue          98.69          17.64      213.00             10
```
---
Result Interpretation
FIFO is simple, but it performs poorly for urgent patients.
Static Priority Queue greatly improves urgent patient waiting time, but it can create long waits for less urgent patients.
Dynamic Priority Queue does not try to win every metric. Its goal is to balance urgency and fairness. It keeps urgent patients much better than FIFO, while reducing the maximum waiting time compared to the static priority strategy.
---
How to Run
Run the program:
```bash
python emergency_queue_simulation.py
```
Optional run with custom values:
```bash
python emergency_queue_simulation.py --patients 80 --seed 42 --output-dir output --open-chart
```
The `--open-chart` flag opens the main HTML chart automatically in the browser.
No external Python packages are required.
---
Why This Project Fits Data Structures
This project demonstrates:
regular queue behavior
priority queue behavior
heap usage
dynamic priority calculation
simulation of a real-world system
comparison between data structure choices
analysis of performance and fairness
The main idea is that a data structure is not only an implementation detail. It changes how the system behaves.
---
Author
Priel Tiran
