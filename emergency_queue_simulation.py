"""
Dynamic Priority Queue Simulation for Emergency Room
Author: Priel Tiran 
Use: Chat GPT
This program simulates an emergency-room queue and compares three strategies:
1. FIFO Queue
2. Static Priority Queue
3. Dynamic Priority Queue

The program uses only built-in Python libraries.
No external packages are required.

Main output files:
- patients.csv
- treatment_order.csv
- simulation_results.csv
- waiting_distribution.csv
- arrival_timeline.csv
- results_summary.txt
- results_chart.html
- arrival_timeline.html
- waiting_distribution.html
"""

import argparse
import csv
import heapq
import os
import random
import webbrowser
from collections import deque
from dataclasses import dataclass, replace
from statistics import mean
from typing import Deque, Dict, List, Tuple


# ------------------------------------------------------------
# Medical case types used in the simulation
# ------------------------------------------------------------
# Each case type has:
# 1. type_bonus: used in the dynamic priority formula.
# 2. service_min / service_max: range of treatment time.
#
# Example:
# "Breathing issue" receives a high type_bonus because it is more critical
# than a minor injury or a regular check.
CASE_TYPES: Dict[str, Dict[str, float]] = {
    "Minor injury": {"type_bonus": 0.0, "service_min": 1, "service_max": 3},
    "Regular check": {"type_bonus": 0.5, "service_min": 2, "service_max": 4},
    "High fever": {"type_bonus": 1.0, "service_min": 2, "service_max": 5},
    "Chest pain": {"type_bonus": 2.0, "service_min": 3, "service_max": 6},
    "Breathing issue": {"type_bonus": 3.0, "service_min": 3, "service_max": 7},
}


@dataclass
class Patient:
    """Represents one patient in the simulation."""

    id: int
    arrival_time: int
    urgency: int
    case_type: str
    service_time: int
    start_time: int = -1
    finish_time: int = -1

    def waiting_time(self) -> int:
        """Waiting time is the time from arrival until treatment starts."""
        if self.start_time < 0:
            return 0
        return self.start_time - self.arrival_time


# ------------------------------------------------------------
# Patient generation
# ------------------------------------------------------------
def generate_patients(num_patients: int = 80, seed: int = 42) -> List[Patient]:
    """
    Generate random patients.

    The random generation is important because the project is a simulation,
    not just a fixed example.

    The seed makes the experiment repeatable: the same seed produces the same
    patients, which is useful for presentation and debugging.
    """
    random.seed(seed)
    patients: List[Patient] = []
    current_time = 0
    case_names = list(CASE_TYPES.keys())

    for patient_id in range(1, num_patients + 1):
        # Random gap between patient arrivals.
        current_time += random.randint(0, 3)

        # Medical urgency level between 1 and 10.
        urgency = random.randint(1, 10)

        # Random case type.
        case_type = random.choice(case_names)
        case_info = CASE_TYPES[case_type]

        # Treatment duration depends on the case type.
        service_time = random.randint(
            int(case_info["service_min"]), int(case_info["service_max"])
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
    Copy patients before running a strategy.

    Each strategy changes start_time and finish_time, so each strategy must get
    a clean copy of the same input patients.
    """
    return [replace(p) for p in patients]


# ------------------------------------------------------------
# Dynamic priority formula
# ------------------------------------------------------------
def dynamic_priority_score(patient: Patient, current_time: int) -> float:
    """
    Calculate the dynamic priority score.

    Formula:
    score = 10 * urgency + 3 * case_type_bonus + 0.8 * waiting_time

    Meaning:
    - urgency is the most important factor.
    - case_type_bonus gives extra priority to more serious cases.
    - waiting_time prevents starvation: patients who wait longer slowly become
      more important.
    """
    case_bonus = CASE_TYPES[patient.case_type]["type_bonus"]
    waiting_time = max(0, current_time - patient.arrival_time)
    return 10 * patient.urgency + 3 * case_bonus + 0.8 * waiting_time


# ------------------------------------------------------------
# Strategy 1: FIFO Queue
# ------------------------------------------------------------
def run_fifo_strategy(patients: List[Patient]) -> List[Patient]:
    """
    FIFO = First In First Out.

    Data structure: deque.
    - append(patient): add to the end of the queue.
    - popleft(): remove from the front of the queue.

    This strategy ignores urgency and treats patients only by arrival order.
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    waiting_queue: Deque[Patient] = deque()
    finished: List[Patient] = []

    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or waiting_queue:
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            waiting_queue.append(patients[next_patient_index])
            next_patient_index += 1

        if not waiting_queue:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        patient = waiting_queue.popleft()
        patient.start_time = current_time
        patient.finish_time = current_time + patient.service_time
        current_time = patient.finish_time
        finished.append(patient)

    return finished


# ------------------------------------------------------------
# Strategy 2: Static Priority Queue
# ------------------------------------------------------------
def run_static_priority_strategy(patients: List[Patient]) -> List[Patient]:
    """
    Static Priority Queue.

    Data structure: heapq.

    The patient with the highest urgency is treated first.
    The priority does not change while the patient is waiting.

    Python's heapq is a min-heap, so we insert negative urgency values.
    For example, urgency 10 becomes -10, which is selected before -3.
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    heap: List[Tuple[float, int, int, Patient]] = []
    finished: List[Patient] = []

    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or heap:
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            patient = patients[next_patient_index]
            heapq.heappush(heap, (-patient.urgency, patient.arrival_time, patient.id, patient))
            next_patient_index += 1

        if not heap:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        _, _, _, patient = heapq.heappop(heap)
        patient.start_time = current_time
        patient.finish_time = current_time + patient.service_time
        current_time = patient.finish_time
        finished.append(patient)

    return finished


# ------------------------------------------------------------
# Strategy 3: Dynamic Priority Queue
# ------------------------------------------------------------
def run_dynamic_priority_strategy(patients: List[Patient]) -> List[Patient]:
    """
    Dynamic Priority Queue.

    This strategy recalculates priority before each treatment decision.

    Why is it needed?
    Static priority is good for urgent patients, but it can cause starvation:
    less urgent patients may wait a very long time if new urgent cases keep
    arriving.

    Dynamic priority tries to balance urgency and fairness by using waiting
    time as part of the score.
    """
    patients = sorted(clone_patients(patients), key=lambda p: p.arrival_time)
    waiting_list: List[Patient] = []
    finished: List[Patient] = []

    current_time = 0
    next_patient_index = 0

    while next_patient_index < len(patients) or waiting_list:
        while (
            next_patient_index < len(patients)
            and patients[next_patient_index].arrival_time <= current_time
        ):
            waiting_list.append(patients[next_patient_index])
            next_patient_index += 1

        if not waiting_list:
            if next_patient_index < len(patients):
                current_time = patients[next_patient_index].arrival_time
            continue

        # Rebuild the heap because waiting time changes over time.
        heap: List[Tuple[float, int, int, Patient]] = []
        for patient in waiting_list:
            score = dynamic_priority_score(patient, current_time)
            heapq.heappush(heap, (-score, patient.arrival_time, patient.id, patient))

        _, _, _, selected_patient = heapq.heappop(heap)
        waiting_list = [p for p in waiting_list if p.id != selected_patient.id]

        selected_patient.start_time = current_time
        selected_patient.finish_time = current_time + selected_patient.service_time
        current_time = selected_patient.finish_time
        finished.append(selected_patient)

    return finished


# ------------------------------------------------------------
# Metrics and analysis
# ------------------------------------------------------------
def calculate_metrics(finished_patients: List[Patient]) -> Dict[str, float]:
    """Calculate summary statistics for one strategy."""
    waiting_times = [p.waiting_time() for p in finished_patients]
    urgent_patients = [p for p in finished_patients if p.urgency >= 8]
    urgent_waiting_times = [p.waiting_time() for p in urgent_patients]

    return {
        "avg_wait": mean(waiting_times) if waiting_times else 0,
        "urgent_avg_wait": mean(urgent_waiting_times) if urgent_waiting_times else 0,
        "max_wait": max(waiting_times) if waiting_times else 0,
        "urgent_over_15": sum(1 for p in urgent_patients if p.waiting_time() > 15),
    }


def waiting_distribution(finished_patients: List[Patient]) -> Dict[str, int]:
    """Count how many patients fall into each waiting-time range."""
    bins = {
        "0-20": 0,
        "21-50": 0,
        "51-100": 0,
        "101-150": 0,
        "151+": 0,
    }

    for patient in finished_patients:
        wait = patient.waiting_time()
        if wait <= 20:
            bins["0-20"] += 1
        elif wait <= 50:
            bins["21-50"] += 1
        elif wait <= 100:
            bins["51-100"] += 1
        elif wait <= 150:
            bins["101-150"] += 1
        else:
            bins["151+"] += 1

    return bins


def arrival_timeline(patients: List[Patient], bucket_size: int = 10) -> Dict[str, Dict[str, int]]:
    """
    Group patient arrivals into time buckets.

    Example bucket: "0-9", "10-19", etc.
    For each bucket, count total arrivals and urgent arrivals.
    """
    timeline: Dict[str, Dict[str, int]] = {}

    for patient in patients:
        bucket_start = (patient.arrival_time // bucket_size) * bucket_size
        bucket_end = bucket_start + bucket_size - 1
        bucket_name = f"{bucket_start}-{bucket_end}"

        if bucket_name not in timeline:
            timeline[bucket_name] = {"total": 0, "urgent": 0}

        timeline[bucket_name]["total"] += 1
        if patient.urgency >= 8:
            timeline[bucket_name]["urgent"] += 1

    return timeline


# ------------------------------------------------------------
# File saving helpers
# ------------------------------------------------------------
def ensure_output_dir(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


def out_path(output_dir: str, filename: str) -> str:
    return os.path.join(output_dir, filename)


def save_patients_csv(patients: List[Patient], output_dir: str) -> None:
    with open(out_path(output_dir, "patients.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "arrival_time", "urgency", "case_type", "service_time"])
        for p in patients:
            writer.writerow([p.id, p.arrival_time, p.urgency, p.case_type, p.service_time])


def save_treatment_order_csv(results_by_strategy: Dict[str, List[Patient]], output_dir: str) -> None:
    with open(out_path(output_dir, "treatment_order.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
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

        for strategy, finished_patients in results_by_strategy.items():
            for position, patient in enumerate(finished_patients, start=1):
                writer.writerow([
                    strategy,
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


def save_results_csv(metrics: Dict[str, Dict[str, float]], output_dir: str) -> None:
    with open(out_path(output_dir, "simulation_results.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["strategy", "avg_wait", "urgent_avg_wait", "max_wait", "urgent_over_15"])
        for strategy, values in metrics.items():
            writer.writerow([
                strategy,
                round(values["avg_wait"], 2),
                round(values["urgent_avg_wait"], 2),
                round(values["max_wait"], 2),
                values["urgent_over_15"],
            ])


def save_waiting_distribution_csv(distributions: Dict[str, Dict[str, int]], output_dir: str) -> None:
    bins = ["0-20", "21-50", "51-100", "101-150", "151+"]
    with open(out_path(output_dir, "waiting_distribution.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["range"] + list(distributions.keys()))
        for bin_name in bins:
            writer.writerow([bin_name] + [distributions[strategy][bin_name] for strategy in distributions])


def save_arrival_timeline_csv(timeline: Dict[str, Dict[str, int]], output_dir: str) -> None:
    with open(out_path(output_dir, "arrival_timeline.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["time_range", "total_arrivals", "urgent_arrivals"])
        for time_range, counts in timeline.items():
            writer.writerow([time_range, counts["total"], counts["urgent"]])


def html_bar(value: float, max_value: float, color: str, width: int = 520) -> str:
    bar_width = 0 if max_value == 0 else int((value / max_value) * width)
    return f'<div class="bar" style="width:{bar_width}px;background:{color};"></div>'


def save_results_chart_html(metrics: Dict[str, Dict[str, float]], output_dir: str) -> None:
    max_value = max(
        max(values["avg_wait"], values["urgent_avg_wait"]) for values in metrics.values()
    )

    rows = ""
    for strategy, values in metrics.items():
        rows += f"""
        <section class="card">
          <h2>{strategy}</h2>
          <p>Average waiting time: <b>{values['avg_wait']:.2f}</b></p>
          {html_bar(values['avg_wait'], max_value, '#4C78A8')}
          <p>Urgent average waiting time: <b>{values['urgent_avg_wait']:.2f}</b></p>
          {html_bar(values['urgent_avg_wait'], max_value, '#F58518')}
          <p>Maximum wait: <b>{values['max_wait']:.2f}</b> | Urgent patients above 15: <b>{values['urgent_over_15']}</b></p>
        </section>
        """

    html = build_html_page(
        title="Emergency Queue Simulation - Main Results",
        body=f"""
        <h1>Emergency Queue Simulation - Main Results</h1>
        <p>This chart compares FIFO, Static Priority Queue, and Dynamic Priority Queue.</p>
        <p>Blue bars show average waiting time for all patients. Orange bars show average waiting time for urgent patients.</p>
        {rows}
        """,
    )

    with open(out_path(output_dir, "results_chart.html"), "w", encoding="utf-8") as file:
        file.write(html)


def save_waiting_distribution_html(distributions: Dict[str, Dict[str, int]], output_dir: str) -> None:
    bins = ["0-20", "21-50", "51-100", "101-150", "151+"]
    max_value = max(max(d.values()) for d in distributions.values())
    colors = {
        "FIFO": "#4C78A8",
        "Static Priority Queue": "#F58518",
        "Dynamic Priority Queue": "#54A24B",
    }

    body = "<h1>Waiting Time Distribution</h1>"
    body += "<p>This chart shows how many patients fall into each waiting-time range.</p>"

    for bin_name in bins:
        body += f"<section class='card'><h2>Waiting time: {bin_name}</h2>"
        for strategy, distribution in distributions.items():
            value = distribution[bin_name]
            body += f"<p>{strategy}: <b>{value}</b></p>"
            body += html_bar(value, max_value, colors.get(strategy, "#888"))
        body += "</section>"

    html = build_html_page("Waiting Time Distribution", body)
    with open(out_path(output_dir, "waiting_distribution.html"), "w", encoding="utf-8") as file:
        file.write(html)


def save_arrival_timeline_html(timeline: Dict[str, Dict[str, int]], output_dir: str) -> None:
    max_value = max(counts["total"] for counts in timeline.values()) if timeline else 1
    body = "<h1>Patient Arrival Timeline</h1>"
    body += "<p>This chart shows how patients entered the simulation over time.</p>"

    for time_range, counts in timeline.items():
        total = counts["total"]
        urgent = counts["urgent"]
        body += f"""
        <section class="card">
          <h2>Time {time_range}</h2>
          <p>Total arrivals: <b>{total}</b></p>
          {html_bar(total, max_value, '#4C78A8')}
          <p>Urgent arrivals: <b>{urgent}</b></p>
          {html_bar(urgent, max_value, '#F58518')}
        </section>
        """

    html = build_html_page("Patient Arrival Timeline", body)
    with open(out_path(output_dir, "arrival_timeline.html"), "w", encoding="utf-8") as file:
        file.write(html)


def build_html_page(title: str, body: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
      background: #f7f7f7;
      color: #222;
    }}
    h1 {{ margin-bottom: 8px; }}
    h2 {{ margin-bottom: 10px; }}
    .card {{
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
      max-width: 760px;
    }}
    .bar {{
      height: 22px;
      border-radius: 4px;
      margin-bottom: 12px;
    }}
    p {{ line-height: 1.35; }}
  </style>
</head>
<body>
  {body}
</body>
</html>
"""


def save_text_summary(
    metrics: Dict[str, Dict[str, float]],
    distributions: Dict[str, Dict[str, int]],
    timeline: Dict[str, Dict[str, int]],
    output_dir: str,
) -> None:
    lines: List[str] = []
    lines.append("Emergency Queue Simulation Results")
    lines.append("=" * 42)
    lines.append("")

    lines.append("Main metrics:")
    for strategy, values in metrics.items():
        lines.append(f"\n{strategy}")
        lines.append(f"Average waiting time: {values['avg_wait']:.2f}")
        lines.append(f"Urgent average waiting time: {values['urgent_avg_wait']:.2f}")
        lines.append(f"Maximum waiting time: {values['max_wait']:.2f}")
        lines.append(f"Urgent patients waiting more than 15 time units: {values['urgent_over_15']}")

    lines.append("\nWaiting time distribution:")
    for strategy, dist in distributions.items():
        lines.append(f"\n{strategy}: {dist}")

    lines.append("\nArrival timeline:")
    for time_range, counts in timeline.items():
        lines.append(f"Time {time_range}: total={counts['total']}, urgent={counts['urgent']}")

    with open(out_path(output_dir, "results_summary.txt"), "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def print_results(metrics: Dict[str, Dict[str, float]], output_dir: str) -> None:
    print("\nEmergency Queue Simulation Results")
    print("=" * 88)
    print(
        f"{'Strategy':<25}"
        f"{'Avg wait':>12}"
        f"{'Urgent avg':>15}"
        f"{'Max wait':>12}"
        f"{'Urgent > 15':>15}"
    )
    print("-" * 88)

    for strategy, values in metrics.items():
        print(
            f"{strategy:<25}"
            f"{values['avg_wait']:>12.2f}"
            f"{values['urgent_avg_wait']:>15.2f}"
            f"{values['max_wait']:>12.2f}"
            f"{values['urgent_over_15']:>15}"
        )

    print("=" * 88)
    print("\nFiles were saved in:")
    print(os.path.abspath(output_dir))
    print("\nMain files created:")
    print("1. patients.csv")
    print("2. treatment_order.csv")
    print("3. simulation_results.csv")
    print("4. waiting_distribution.csv")
    print("5. arrival_timeline.csv")
    print("6. results_summary.txt")
    print("7. results_chart.html")
    print("8. arrival_timeline.html")
    print("9. waiting_distribution.html")


def run_simulation(num_patients: int, seed: int, output_dir: str, open_chart: bool = False) -> None:
    ensure_output_dir(output_dir)

    patients = generate_patients(num_patients=num_patients, seed=seed)

    results_by_strategy = {
        "FIFO": run_fifo_strategy(patients),
        "Static Priority Queue": run_static_priority_strategy(patients),
        "Dynamic Priority Queue": run_dynamic_priority_strategy(patients),
    }

    metrics = {
        strategy: calculate_metrics(finished)
        for strategy, finished in results_by_strategy.items()
    }

    distributions = {
        strategy: waiting_distribution(finished)
        for strategy, finished in results_by_strategy.items()
    }

    timeline = arrival_timeline(patients, bucket_size=10)

    save_patients_csv(patients, output_dir)
    save_treatment_order_csv(results_by_strategy, output_dir)
    save_results_csv(metrics, output_dir)
    save_waiting_distribution_csv(distributions, output_dir)
    save_arrival_timeline_csv(timeline, output_dir)
    save_results_chart_html(metrics, output_dir)
    save_arrival_timeline_html(timeline, output_dir)
    save_waiting_distribution_html(distributions, output_dir)
    save_text_summary(metrics, distributions, timeline, output_dir)

    print_results(metrics, output_dir)

    if open_chart:
        webbrowser.open(os.path.abspath(out_path(output_dir, "results_chart.html")))


def parse_args() -> argparse.Namespace:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_dir = os.path.join(script_dir, "output")

    parser = argparse.ArgumentParser(description="Emergency-room queue simulation")
    parser.add_argument("--patients", type=int, default=80, help="number of patients to generate")
    parser.add_argument("--seed", type=int, default=42, help="random seed for repeatable simulation")
    parser.add_argument("--output-dir", default=default_output_dir, help="folder for output files")
    parser.add_argument("--open-chart", action="store_true", help="open main HTML chart after running")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_simulation(
        num_patients=args.patients,
        seed=args.seed,
        output_dir=args.output_dir,
        open_chart=args.open_chart,
    )


if __name__ == "__main__":
    main()
