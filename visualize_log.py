import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
LOG_FILE = "station_log.csv"

ROOM_COLORS = {
    "R1": "#1f77b4",        # blue
    "R2": "#ff7f0e",        # orange
    "Control": "#2ca02c",   # green
}

DEFAULT_COLOR = "#7f7f7f"


# ---------------- LOAD DATA ----------------
def load_log(path=LOG_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run simulation first.")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("CSV is empty.")

    # make relative time
    if "time" in df.columns:
        t0 = df["time"].iloc[0]
        df["t_rel"] = df["time"] - t0
    else:
        df["t_rel"] = range(len(df))

    return df


def room_color(room_id):
    return ROOM_COLORS.get(room_id, DEFAULT_COLOR)


# ---------------- PLOTS ----------------
def plot_temperature_lines(df):
    plt.figure(figsize=(9, 5))

    for room, g in df.groupby("room_id"):
        plt.plot(
            g["t_rel"],
            g["temperature"],
            label=room,
            color=room_color(room),
            linewidth=2,
            alpha=0.9,
        )

    plt.title("🌡 Room Temperature Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()


def plot_energy_lines(df):
    plt.figure(figsize=(9, 5))

    for room, g in df.groupby("room_id"):
        plt.plot(
            g["t_rel"],
            g["energy_usage_kw"],
            label=room,
            color=room_color(room),
            linewidth=2,
            linestyle="--",
            alpha=0.85,
        )

    plt.title("⚡ Energy Usage Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy (kW)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()


def bar_avg_energy(df):
    avg_energy = df.groupby("room_id")["energy_usage_kw"].mean()

    plt.figure(figsize=(7, 5))
    bars = plt.bar(
        avg_energy.index,
        avg_energy.values,
        color=[room_color(r) for r in avg_energy.index],
        alpha=0.85,
    )

    plt.title("📊 Average Energy Usage per Room")
    plt.ylabel("Avg Energy (kW)")
    plt.xlabel("Room")

    for bar in bars:
        y = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, y, f"{y:.2f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()


def bar_avg_temperature(df):
    avg_temp = df.groupby("room_id")["temperature"].mean()

    plt.figure(figsize=(7, 5))
    bars = plt.bar(
        avg_temp.index,
        avg_temp.values,
        color=[room_color(r) for r in avg_temp.index],
        alpha=0.85,
    )

    plt.title("📊 Average Temperature per Room")
    plt.ylabel("Avg Temperature (°C)")
    plt.xlabel("Room")

    for bar in bars:
        y = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, y, f"{y:.1f}",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()


def scatter_solar_vs_energy(df):
    if "solar_flux" not in df.columns:
        print("No solar_flux column found, skipping scatter.")
        return

    plt.figure(figsize=(8, 5))

    for room, g in df.groupby("room_id"):
        plt.scatter(
            g["solar_flux"],
            g["energy_usage_kw"],
            label=room,
            color=room_color(room),
            alpha=0.6,
            s=30,
        )

    plt.title("🔵 Solar Flux vs Energy Usage")
    plt.xlabel("Solar Flux")
    plt.ylabel("Energy Usage (kW)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()


# ---------------- SUMMARY ----------------
def print_summary(df):
    summary = df.groupby("room_id").agg(
        avg_temp=("temperature", "mean"),
        max_temp=("temperature", "max"),
        avg_energy=("energy_usage_kw", "mean"),
        max_energy=("energy_usage_kw", "max"),
    )

    print("\n===== 🔍 ROOM SUMMARY =====")
    print(summary.round(2))
    print("==========================\n")


# ---------------- MAIN ----------------
def main():
    df = load_log()

    print_summary(df)

    plot_temperature_lines(df)
    plot_energy_lines(df)
    bar_avg_energy(df)
    bar_avg_temperature(df)
    scatter_solar_vs_energy(df)

    plt.show()


if __name__ == "__main__":
    main()
