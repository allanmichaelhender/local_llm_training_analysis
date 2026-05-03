#!/usr/bin/env python3
"""Generate heart rate graph from FIT file data."""

import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fitparse import FitFile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def parse_hr_data(filepath):
    """Extract timestamp and HR from FIT file."""
    fitfile = FitFile(filepath)
    timestamps = []
    heart_rates = []

    for record in fitfile.get_messages("record"):
        ts = record.get_value("timestamp")
        hr = record.get_value("heart_rate")
        if ts and hr:
            timestamps.append(ts)
            heart_rates.append(hr)

    return timestamps, heart_rates


def get_session_info(filepath):
    """Get workout summary from session data."""
    fitfile = FitFile(filepath)
    for record in fitfile.get_messages("session"):
        return {
            "sport": record.get_value("sport") or "unknown",
            "avg_hr": record.get_value("avg_heart_rate"),
            "max_hr": record.get_value("max_heart_rate"),
            "calories": record.get_value("total_calories"),
            "duration_min": (record.get_value("total_elapsed_time") or 0) / 60,
        }
    return {}


def plot_hr(filepath, save_path=None):
    """Create HR vs time graph."""
    timestamps, heart_rates = parse_hr_data(filepath)
    info = get_session_info(filepath)

    if not timestamps:
        print(f"No HR data found in {filepath}")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot HR line
    ax.plot(timestamps, heart_rates, color="red", linewidth=1.5, label="Heart Rate")

    # Fill area under curve
    ax.fill_between(timestamps, heart_rates, alpha=0.3, color="red")

    # Add avg HR line if available
    if info.get("avg_hr"):
        ax.axhline(
            y=info["avg_hr"],
            color="orange",
            linestyle="--",
            linewidth=2,
            label=f"Avg HR: {info['avg_hr']} bpm",
        )

    # Add max HR line if available
    if info.get("max_hr"):
        ax.axhline(
            y=info["max_hr"],
            color="darkred",
            linestyle=":",
            linewidth=2,
            label=f"Max HR: {info['max_hr']} bpm",
        )

    # Formatting
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Heart Rate (bpm)", fontsize=12)

    # Build title
    sport = info.get("sport", "Workout").title()
    duration = info.get("duration_min", 0)
    title = f"{sport} - {duration:.0f} min"
    if info.get("calories"):
        title += f" - {info['calories']} kcal"
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Format x-axis as time
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    plt.xticks(rotation=45)

    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    # Set y-axis range with padding
    min_hr = min(heart_rates)
    max_hr = max(heart_rates)
    ax.set_ylim(min_hr - 10, max_hr + 10)

    plt.tight_layout()

    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Graph saved to: {save_path}")
    else:
        plt.show()

    plt.close()


def main():
    fit_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_files")
    fit_files = glob.glob(os.path.join(fit_dir, "*.fit"))

    if not fit_files:
        print("No .fit files found in fit_files/ directory")
        return

    # Create output directory for graphs
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphs")
    os.makedirs(output_dir, exist_ok=True)

    for filepath in fit_files:
        filename = os.path.basename(filepath).replace(".fit", ".png")
        save_path = os.path.join(output_dir, filename)
        plot_hr(filepath, save_path)


if __name__ == "__main__":
    main()
