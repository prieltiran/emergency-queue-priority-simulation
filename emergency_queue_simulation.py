"""
Dynamic Priority Queue Simulation for Emergency Room
Author: Priel Tiran

Project idea:
This program simulates an emergency-room queue.
Patients arrive over time, each patient has:
1. arrival time
2. urgency level
3. case type
4. estimated service time

The program compares three queue-management strategies:
1. FIFO Queue:
   First patient who arrives is treated first.
2. Static Priority Queue:
   Patients with higher urgency are treated first.
3. Dynamic Priority Queue:
   Priority is based on urgency, case type, and waiting time.

Important:
This version does NOT require matplotlib.
It uses only built-in Python libraries, so it should run in PyCharm without installing packages.
It creates:
1. patients.csv
2. treatment_order.csv
3. simulation_results.csv
4. results_chart.html
5. results_summary.txt
"""

import csv
import random
import heapq
from collections import deque
from dataclasses import dataclass, replace
from statistics import mean
from typing import Deque, Dict, List, Tuple


# ------------------------------------------------------------
# Case types
# ------------------------------------------------------------
# Each case type has:
# - type_bonus: extra priority for more serious cases.
# - service_min/service_max: estimated treatment time range.
#
# This makes the simulation more realistic:
# not every patient has the same case type or service time.
CASE_TYPES: Dict[str, Dict[str, float]] = {
    "Minor injury": {
        "type_bonus": 0.0,
        "service_min": 1,
        "service_max": 3,
    },
    "Regular check": {
        "type_bonus": 0.5,
        "service_min": 2,
        "service_max": 4,
    },
    "High fever": {
        "type_bonus": 1.0,
        "service_min": 2,
        "service_max": 5,
    },
    "Chest pain": {
        "type_bonus": 2.0,
        "service_min": 3,
        "service_max": 6,
    },
    "Breathing issue": {
        "type_bonus": 3.0,
        "service_min": 3,
        "service_max": 7,
    },
}


@dataclass
class Patient:
    """
    A simple data class that represents one patient.

    id:
        Patient number.
    arrival_time:
        The time when the patient enters the system.
    urgency:
        A number between 1 and 10. Higher means more urgent.
    case_type:
        The medical case type.
    service_time:
        How long it takes to treat this patient.
    start_time:
        The time when treatment starts.
    finish_time:
        The time when treatment ends.
    """

    id: int
    arrival_time: int
    urgency: int
    case_type: str
    service_time: int
    start_time: int = -1
    finish_time: int = -1

    def waiting_time(self) -> int:
        """
        Waiting time = start time - arrival time.
        If patient was not treated yet, return 0.
        """
        if self.start_time < 0:
            return 0
        return self.start_time - self.arrival_time


def generate_patients(num_patients: int = 50, seed: int = 42) -> List[Patient]:
    """
    Generate random patients.

    Why random?
    The professor asked for a dynamic simulation, not just a fixed list.
    So patients arrive over time with different urgency levels and case types.

    The random seed makes the experiment repeatable:
    every run with the same seed gives the same patients.
    """
    random.seed(seed)

    patients: List[Patient] = []
    current_time = 0

    case_names = list(CASE_TYPES.keys())

    for patient_id in range(1, num_patients + 1):
        # Random gap between arrivals.
        # Example: next patient arrives 0, 1, 2, or 3 time units later.
        current_time += random.randint(0, 3)

        # Urgency level between 1 and 10.
        urgency = random.randint(1, 10)

        # Random case type.
        case_type = random.choice(case_names)

        # Service time depends on the case type.
        case_info = CASE_TYPES[case_type]
        service_time = random.randint(
            int(case_info["service_min"]),
            int(case_info["service_max"]),
        )

        patients.append(
            Patient(
                id=patient_id,
                arrival_time=current_time,
                urgency=urgency,
                case_type=case_type,
                service_time=service_time,
            )
        )

    return patients


def clone_patients(patients: List[Patient]) -> List[Patient]:
    """
    Create a clean copy of the patients.

    We need this because each strategy changes start_time and finish_time.
    If we reuse the same objects, the results will affect each other.
    """
    return [replace(p) for p in patients]


def dynamic_priority_score(patient: Patient, current_time: int) -> float:
    """
    Calculate dynamic priority score.

    The score is based on:
    1. urgency
    2. case type bonus
    3. waiting time bonus

    This is the main idea of the project:
    a patient with medium urgency who waits too long should become more important.

    Formula:
    score = urgency + case_type_bonus + 0.15 * waiting_time
    """
    case_bonus = CASE_TYPES[patient.case_type]["type_bonus"]
    waiting_time = max(0, current_time - patient.arrival_time)

    score = 10 * patient.urgency + 3 * case_bonus + 0.3 * waiting_time

    return score

def run_fifo_strategy(patients: List[Patient]) -> List[Patient]:
    """
    Strategy 1: FIFO Queue.

    FIFO means First In First Out.
    The first patient who arrives is the first patient treated.

    Data structure:
    deque from collections.

    Main operations:
    append()  -> add patient to the end of the queue
    popleft() -> remove patient from the front of the queue
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    waiting_queue: Deque[Patient] = deque()

    finished: List[Patient] = []
    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or waiting_queue:
        # Add all patients that have arrived by current_time.
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            waiting_queue.append(patients[next_patient_index])
            next_patient_index += 1

        # If nobody is waiting, move time forward to the next arrival.
        if not waiting_queue:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        # Treat the first patient in the queue.
        patient = waiting_queue.popleft()
        patient.start_time = current_time
        patient.finish_time = current_time + patient.service_time

        current_time = patient.finish_time
        finished.append(patient)

    return finished


def run_static_priority_strategy(patients: List[Patient]) -> List[Patient]:
    """
    Strategy 2: Static Priority Queue.

    Patients with higher urgency are treated first.
    The priority does not change over time.

    Data structure:
    heapq.

    Python heapq is a min-heap.
    To make higher urgency come first, we insert negative urgency.
    Example:
    urgency 10 becomes -10, which is smaller than -5, so it comes first.

    Tuple format in heap:
    (-urgency, arrival_time, id, patient)

    arrival_time and id are used to break ties in a stable way.
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    heap: List[Tuple[float, int, int, Patient]] = []

    finished: List[Patient] = []
    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or heap:
        # Add all patients that have arrived by current_time.
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            patient = patients[next_patient_index]
            heapq.heappush(heap, (-patient.urgency, patient.arrival_time, patient.id, patient))
            next_patient_index += 1

        # If nobody is waiting, jump to next arrival.
        if not heap:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        # Treat patient with highest urgency.
        _, _, _, patient = heapq.heappop(heap)
        patient.start_time = current_time
        patient.finish_time = current_time + patient.service_time

        current_time = patient.finish_time
        finished.append(patient)

    return finished


def run_dynamic_priority_strategy(patients: List[Patient]) -> List[Patient]:
    """
    Strategy 3: Dynamic Priority Queue.

    This is the most advanced strategy in the project.

    Priority is recalculated before each treatment decision.
    It depends on:
    - urgency
    - case type
    - waiting time

    Why rebuild the heap?
    In Python heapq, priorities are not automatically updated.
    Since waiting time changes as time moves forward, we rebuild the heap
    before selecting the next patient.

    This is fine for a simulation and makes the dynamic behavior clear.
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    waiting_list: List[Patient] = []

    finished: List[Patient] = []
    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or waiting_list:
        # Add all patients that have arrived by current_time.
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            waiting_list.append(patients[next_patient_index])
            next_patient_index += 1

        # If nobody is waiting, jump to next arrival.
        if not waiting_list:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        # Build a heap with updated dynamic priorities.
        heap: List[Tuple[float, int, int, Patient]] = []

        for patient in waiting_list:
            score = dynamic_priority_score(patient, current_time)

            # Negative score because heapq is a min-heap.
            # Higher score should be selected first.
            heapq.heappush(heap, (-score, patient.arrival_time, patient.id, patient))

        # Select the patient with the highest dynamic score.
        _, _, _, selected_patient = heapq.heappop(heap)

        # Remove selected patient from waiting list.
        waiting_list = [p for p in waiting_list if p.id != selected_patient.id]

        selected_patient.start_time = current_time
        selected_patient.finish_time = current_time + selected_patient.service_time

        current_time = selected_patient.finish_time
        finished.append(selected_patient)

    return finished


def calculate_metrics(finished_patients: List[Patient]) -> Dict[str, float]:
    """
    Calculate statistical measurements for one strategy.

    These statistics are used to compare the strategies:
    - average waiting time
    - average waiting time for urgent patients
    - maximum waiting time
    - number of urgent patients waiting more than 15 time units
    """
    waiting_times = [p.waiting_time() for p in finished_patients]

    # Urgent patient is defined here as urgency >= 8.
    urgent_patients = [p for p in finished_patients if p.urgency >= 8]
    urgent_waiting_times = [p.waiting_time() for p in urgent_patients]

    urgent_waiting_more_than_15 = sum(
        1 for p in urgent_patients if p.waiting_time() > 15
    )

    return {
        "avg_wait": mean(waiting_times) if waiting_times else 0,
        "urgent_avg_wait": mean(urgent_waiting_times) if urgent_waiting_times else 0,
        "max_wait": max(waiting_times) if waiting_times else 0,
        "urgent_over_15": urgent_waiting_more_than_15,
    }


def save_patients_csv(patients: List[Patient], filename: str = "patients.csv") -> None:
    """
    Save the generated patients to a CSV file.
    This helps show the input data of the simulation.
    """
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "id",
            "arrival_time",
            "urgency",
            "case_type",
            "service_time",
        ])

        for p in patients:
            writer.writerow([
                p.id,
                p.arrival_time,
                p.urgency,
                p.case_type,
                p.service_time,
            ])


def save_treatment_order_csv(
    strategy_name: str,
    finished_patients: List[Patient],
    filename: str = "treatment_order.csv",
    write_header: bool = False,
) -> None:
    """
    Save the treatment order for one strategy.

    The same CSV file will contain all strategies.
    This makes it easy to compare treatment order.
    """
    mode = "w" if write_header else "a"

    with open(filename, mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if write_header:
            writer.writerow([
                "strategy",
                "treatment_position",
                "patient_id",
                "arrival_time",
                "start_time",
                "finish_time",
                "waiting_time",
                "urgency",
                "case_type",
                "service_time",
            ])

        for position, patient in enumerate(finished_patients, start=1):
            writer.writerow([
                strategy_name,
                position,
                patient.id,
                patient.arrival_time,
                patient.start_time,
                patient.finish_time,
                patient.waiting_time(),
                patient.urgency,
                patient.case_type,
                patient.service_time,
            ])


def save_results_csv(
    results: Dict[str, Dict[str, float]],
    filename: str = "simulation_results.csv",
) -> None:
    """
    Save the final statistical comparison to CSV.
    """
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "strategy",
            "avg_wait",
            "urgent_avg_wait",
            "max_wait",
            "urgent_over_15",
        ])

        for strategy, metrics in results.items():
            writer.writerow([
                strategy,
                round(metrics["avg_wait"], 2),
                round(metrics["urgent_avg_wait"], 2),
                round(metrics["max_wait"], 2),
                metrics["urgent_over_15"],
            ])


def save_html_chart(
    results: Dict[str, Dict[str, float]],
    filename: str = "results_chart.html",
) -> None:
    """
    Save a simple chart as an HTML file.

    Why HTML instead of matplotlib?
    Because HTML works without installing external Python packages.
    The file can be opened in any browser.

    The chart shows:
    - average waiting time
    - urgent average waiting time
    """
    strategies = list(results.keys())
    max_value = max(
        max(metrics["avg_wait"], metrics["urgent_avg_wait"])
        for metrics in results.values()
    )

    def bar_width(value: float) -> int:
        if max_value == 0:
            return 0
        return int((value / max_value) * 500)

    rows = ""

    for strategy in strategies:
        avg_wait = results[strategy]["avg_wait"]
        urgent_wait = results[strategy]["urgent_avg_wait"]

        rows += f"""
        <div class="strategy">
            <h2>{strategy}</h2>

            <div class="label">Average waiting time: {avg_wait:.2f}</div>
            <div class="bar avg" style="width: {bar_width(avg_wait)}px;"></div>

            <div class="label">Urgent patients average waiting time: {urgent_wait:.2f}</div>
            <div class="bar urgent" style="width: {bar_width(urgent_wait)}px;"></div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Emergency Queue Simulation Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f7f7f7;
                color: #222;
            }}
            h1 {{
                margin-bottom: 10px;
            }}
            .strategy {{
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 18px;
                margin-bottom: 18px;
                max-width: 750px;
            }}
            .label {{
                margin-top: 10px;
                margin-bottom: 4px;
                font-size: 15px;
            }}
            .bar {{
                height: 24px;
                border-radius: 4px;
            }}
            .avg {{
                background: #4C78A8;
            }}
            .urgent {{
                background: #F58518;
            }}
            .note {{
                margin-top: 30px;
                font-size: 14px;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <h1>Emergency Queue Simulation Results</h1>
        <p>
            Comparison between FIFO, Static Priority Queue, and Dynamic Priority Queue.
        </p>

        {rows}

        <div class="note">
            Blue bars: average waiting time for all patients.<br>
            Orange bars: average waiting time for urgent patients.
        </div>
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)


def save_text_summary(
    results: Dict[str, Dict[str, float]],
    filename: str = "results_summary.txt",
) -> None:
    """
    Save a simple text summary.
    This is useful if you want to copy results into your presentation.
    """
    lines = []
    lines.append("Emergency Queue Simulation Results")
    lines.append("=" * 40)
    lines.append("")

    for strategy, metrics in results.items():
        lines.append(strategy)
        lines.append("-" * len(strategy))
        lines.append(f"Average waiting time: {metrics['avg_wait']:.2f}")
        lines.append(f"Urgent average waiting time: {metrics['urgent_avg_wait']:.2f}")
        lines.append(f"Maximum waiting time: {metrics['max_wait']:.2f}")
        lines.append(f"Urgent patients waiting more than 15 time units: {metrics['urgent_over_15']}")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def print_results(results: Dict[str, Dict[str, float]]) -> None:
    """
    Print results in a readable table in the terminal.
    """
    print("\nEmergency Queue Simulation Results")
    print("=" * 85)
    print(
        f"{'Strategy':<25}"
        f"{'Avg wait':>12}"
        f"{'Urgent avg':>15}"
        f"{'Max wait':>12}"
        f"{'Urgent > 15':>15}"
    )
    print("-" * 85)

    for strategy, metrics in results.items():
        print(
            f"{strategy:<25}"
            f"{metrics['avg_wait']:>12.2f}"
            f"{metrics['urgent_avg_wait']:>15.2f}"
            f"{metrics['max_wait']:>12.2f}"
            f"{metrics['urgent_over_15']:>15}"
        )

    print("=" * 85)
    print("\nFiles created:")
    print("1. patients.csv")
    print("2. treatment_order.csv")
    print("3. simulation_results.csv")
    print("4. results_chart.html")
    print("5. results_summary.txt")
    print("\nOpen results_chart.html in your browser to see the chart.")


def main() -> None:
    """
    Main function:
    1. Generate patients.
    2. Run the three strategies.
    3. Calculate metrics.
    4. Save output files.
    5. Print results.
    """
    # You can change these two values if you want different simulations.
    num_patients = 80
    seed = 42

    patients = generate_patients(num_patients=num_patients, seed=seed)

    # Run the three queue strategies.
    fifo_finished = run_fifo_strategy(patients)
    static_priority_finished = run_static_priority_strategy(patients)
    dynamic_priority_finished = run_dynamic_priority_strategy(patients)

    # Calculate statistical metrics.
    results = {
        "FIFO": calculate_metrics(fifo_finished),
        "Static Priority Queue": calculate_metrics(static_priority_finished),
        "Dynamic Priority Queue": calculate_metrics(dynamic_priority_finished),
    }

    # Save input data.
    save_patients_csv(patients)

    # Save treatment order of all strategies.
    save_treatment_order_csv("FIFO", fifo_finished, write_header=True)
    save_treatment_order_csv("Static Priority Queue", static_priority_finished)
    save_treatment_order_csv("Dynamic Priority Queue", dynamic_priority_finished)

    # Save final results.
    save_results_csv(results)
    save_html_chart(results)
    save_text_summary(results)

    # Print results to terminal.
    print_results(results)


if __name__ == "__main__":
    main()
