from pathlib import Path

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "analysis"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "baseline_vs_script_aware.png"
)


# ---------------------------------------------------------
# Results from our experiments
# ---------------------------------------------------------

# Generic multilingual recognition model
GENERIC_CER = 0.914

# Script-aware recognition experiment
SCRIPT_AWARE_CER = 0.610


# ---------------------------------------------------------
# Create comparison chart
# ---------------------------------------------------------

def create_chart():

    print("=" * 70)
    print("GENERATING BASELINE VS SCRIPT-AWARE COMPARISON")
    print("=" * 70)

    labels = [
        "Generic OCR",
        "Script-Aware OCR"
    ]

    values = [
        GENERIC_CER,
        SCRIPT_AWARE_CER
    ]

    print("\nResults:")

    print(
        f"  Generic OCR       CER = {GENERIC_CER:.3f}"
    )

    print(
        f"  Script-Aware OCR  CER = {SCRIPT_AWARE_CER:.3f}"
    )

    # -----------------------------------------------------
    # Calculate improvement
    # -----------------------------------------------------

    improvement = (
        (GENERIC_CER - SCRIPT_AWARE_CER)
        / GENERIC_CER
    ) * 100

    print(
        f"\nRelative CER reduction: "
        f"{improvement:.2f}%"
    )

    # -----------------------------------------------------
    # Create output directory
    # -----------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        labels,
        values
    )

    plt.title(
        "Generic OCR vs Script-Aware OCR"
    )

    plt.xlabel(
        "Recognition Approach"
    )

    plt.ylabel(
        "Character Error Rate (CER)"
    )

    plt.ylim(
        0,
        1.05
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    # -----------------------------------------------------
    # Add values above bars
    # -----------------------------------------------------

    for bar, value in zip(
        bars,
        values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,

            value + 0.025,

            f"{value:.3f}",

            ha="center",
            va="bottom"
        )

    # -----------------------------------------------------
    # Add improvement annotation
    # -----------------------------------------------------

    plt.text(
        0.5,
        0.15,

        f"CER reduction: {improvement:.1f}%",

        ha="center",

        transform=plt.gca().transAxes
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nChart saved to:\n{OUTPUT_PATH}"
    )

    print("\n" + "=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    create_chart()