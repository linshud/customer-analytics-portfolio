"""Regenerate the cohort retention heatmap from the project's latest CSV.

Run from any directory with:
    py "C:\\...\\customer-analytics-main\\update_cohort_heatmap.py"

The script automatically locates the data and visualizations folders next to itself.
"""
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
CSV_FILE = PROJECT_DIR / "data" / "cohort_retention.csv"
OUTPUT_DIR = PROJECT_DIR / "visualizations"
IMAGE_FILE = OUTPUT_DIR / "cohort_retention_heatmap.png"
BACKUP_FILE = OUTPUT_DIR / "cohort_retention_heatmap_old_backup.png"
MONTH_COLS = [str(i) for i in range(13)]


def main():
    if not CSV_FILE.is_file():
        sys.exit(f"ERROR: Cannot find source CSV: {CSV_FILE}")

    # Read a wide-format table: CohortMonth,0,1,...,12
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig", dtype={"CohortMonth": str})
    df.columns = [str(col).strip() for col in df.columns]
    required = ["CohortMonth", *MONTH_COLS]
    missing = [c for c in required if c not in df.columns]
    if missing:
        sys.exit(
            f"ERROR: The cohort CSV is missing columns: {missing}.\n"
            f"Expected: {required}"
        )

    df = df.loc[:, required].copy()
    if df.empty:
        sys.exit("ERROR: The cohort CSV has no rows.")
    df["CohortMonth"] = df["CohortMonth"].str.strip()
    for col in MONTH_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # NaN denotes an unobservable future month, NOT zero retention.
    values = df[MONTH_COLS].to_numpy(dtype=float)
    if np.isfinite(values).sum() == 0:
        sys.exit("ERROR: No numeric retention values found.")
    if np.nanmax(values) <= 1 and np.nanmin(values) >= 0:
        # Support 0..1 fraction data; the current project uses 0..100.
        values *= 100

    # Keep the previous image for easy comparison; never overwrite backup.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if IMAGE_FILE.exists() and not BACKUP_FILE.exists():
        shutil.copy2(IMAGE_FILE, BACKUP_FILE)
        print(f"Old chart backed up to: {BACKUP_FILE}")

    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=160)
    masked = np.ma.masked_invalid(values)
    cmap = plt.get_cmap("YlOrRd_r").copy()
    cmap.set_bad("#f7f7f7")
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=100, aspect="auto", interpolation="none")

    ax.set_title("Monthly Cohort Retention Rates (%)", fontsize=17, weight="bold", pad=18)
    ax.set_xlabel("Months Since First Purchase", fontsize=12, labelpad=12)
    ax.set_ylabel("Cohort (First Purchase Month)", fontsize=12, labelpad=12)
    ax.set_xticks(range(len(MONTH_COLS)), labels=MONTH_COLS)
    ax.set_yticks(range(len(df)), labels=df["CohortMonth"].tolist())
    ax.tick_params(length=0, labelsize=10)
    ax.set_xticks(np.arange(-0.5, len(MONTH_COLS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(df), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.3)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if np.isfinite(value):
                label = "100" if np.isclose(value, 100) else f"{value:.2f}"
                ax.text(j, i, label, ha="center", va="center", fontsize=8.1,
                        color="#222222" if value >= 45 else "white")

    colorbar = fig.colorbar(im, ax=ax, shrink=0.84, pad=0.025)
    colorbar.set_label("Retention Rate (%)", fontsize=11)
    colorbar.outline.set_visible(False)

    fig.text(
        0.5, 0.015,
        "Blank cells = months outside the observed period. Data ends Dec 9, 2011; December observations are partial.",
        ha="center", va="center", fontsize=9, color="#555555"
    )
    fig.subplots_adjust(left=0.12, right=0.94, top=0.91, bottom=0.11)
    fig.savefig(IMAGE_FILE, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"SUCCESS: Updated heatmap: {IMAGE_FILE}")
    print(f"Cohorts: {len(df)}; observed values: {np.isfinite(values).sum()}")
    first_month = values[0, 1] if values.shape[1] > 1 else float("nan")
    print(f"{df['CohortMonth'].iloc[0]} Month-1 retention: {first_month:.2f}%")


if __name__ == "__main__":
    main()
