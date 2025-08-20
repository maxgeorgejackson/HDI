import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

st.set_page_config(page_title="Mass Spec Peak Analyzer", layout="wide")
st.title("Mass Spec Peak Analyzer")

# ------------------- Drag-and-Drop CSVs -------------------
uploaded_files = st.file_uploader(
    "Drag and drop all CSV files here",
    type="csv",
    accept_multiple_files=True
)

output_csv = st.text_input("Output CSV file name", value="merged_output.csv")
output_pdf = st.text_input("Output PDF file name", value="peak_intensities.pdf")
mz_tolerance = st.number_input("m/z tolerance for merging peaks", value=0.02, step=0.01)
top_percent = st.number_input("Top % threshold for significance", value=1.0, step=0.1)
number_of_scans_col = "Number of Scans"

run_analysis = st.button("Run Analysis")

# ------------------- Functions -------------------
def parse_filename(filename):
    base = filename.name if hasattr(filename, 'name') else filename
    base = base.replace(".csv", "")
    cell_line_match = re.search(r"(Mel202|92\.1|921|MP41|MP46)", base)
    if not cell_line_match:
        raise ValueError(f"Cell line not found in filename: {base}")
    cell_line = cell_line_match.group(1)
    if cell_line == "921":
        cell_line = "92.1"
    repeat_match = re.search(r"([A-Za-z]+)(\d+)", base)
    if not repeat_match:
        raise ValueError(f"Repeat ID not found in filename: {base}")
    bio_repeat, sys_repeat = repeat_match.groups()
    return cell_line, bio_repeat, sys_repeat

def cluster_peaks(peaks, tolerance):
    sorted_peaks = sorted(peaks)
    clusters = []
    current_cluster = [sorted_peaks[0]]
    for p in sorted_peaks[1:]:
        if abs(p - np.mean(current_cluster)) <= tolerance:
            current_cluster.append(p)
        else:
            clusters.append(current_cluster)
            current_cluster = [p]
    clusters.append(current_cluster)
    mapping = {}
    for c in clusters:
        mean_val = np.mean(c)
        for p in c:
            mapping[p] = mean_val
    return mapping

def round_sf(x, sig=4):
    if pd.isnull(x):
        return x
    return float(f"{x:.{sig}g}")

# ------------------- Main Analysis -------------------
if run_analysis:
    if not uploaded_files:
        st.error("Please drag and drop at least one CSV file.")
    else:
        st.info(f"Processing {len(uploaded_files)} files...")
        all_data = []
        all_peaks = set()
        for f in uploaded_files:
            try:
                cell_line, bio_repeat, sys_repeat = parse_filename(f)
                df = pd.read_csv(f)
                if number_of_scans_col not in df.columns:
                    st.warning(f"Column '{number_of_scans_col}' not found in {f.name}. Skipping.")
                    continue
                peak_cols = [c for c in df.columns[4:] if c != number_of_scans_col]
                df[peak_cols] = df[peak_cols].apply(pd.to_numeric, errors='coerce')
                df[number_of_scans_col] = pd.to_numeric(df[number_of_scans_col], errors='coerce')
                df[peak_cols] = df[peak_cols].div(df[number_of_scans_col], axis=0)
                days = df.iloc[:,0].astype(str).str.extract(r"(\d+)$")[0].astype(int)
                for peak_col in peak_cols:
                    peak_val = float(peak_col.split("_")[0])
                    intensities = df[peak_col].values
                    for day, intensity in zip(days, intensities):
                        all_data.append({
                            "peak": peak_val,
                            "day": day,
                            "cell_line": cell_line,
                            "bio_repeat": bio_repeat,
                            "sys_repeat": sys_repeat,
                            "intensity": intensity
                        })
                    all_peaks.add(peak_val)
            except Exception as e:
                st.warning(f"Skipping file {f.name} due to error: {e}")

        # Merge peaks
        peak_mapping = cluster_peaks(all_peaks, mz_tolerance)
        for d in all_data:
            d["peak"] = peak_mapping[d["peak"]]

        merged_df = pd.DataFrame(all_data)
        pivot_df = merged_df.pivot_table(
            index="peak",
            columns=["cell_line","day"],
            values="intensity",
            aggfunc="mean"
        )
        pivot_df.index = np.round(pivot_df.index,4)
        pivot_df = pivot_df.applymap(lambda x: round_sf(x,4))
        pivot_df.to_csv(output_csv)
        st.success(f"Saved merged CSV: {output_csv}")

        # Plot
        sns.set(style="whitegrid")
        plot_df = pivot_df.reset_index()
        plt.figure(figsize=(16,7))
        cell_lines = [c for c in plot_df.columns.levels[0] if c != "peak"]
        palette = sns.color_palette("tab10", n_colors=len(cell_lines))
        all_values = plot_df[cell_lines].values.flatten()
        all_values = all_values[~pd.isnull(all_values)]
        global_threshold = np.percentile(all_values, 100-top_percent)
        all_peaks_top = []
        for cell_line in cell_lines:
            sub_df = plot_df[cell_line]
            mask = sub_df.gt(global_threshold).any(axis=1)
            peaks_above = plot_df.loc[mask, "peak"].values
            all_peaks_top.extend(peaks_above)
        all_peaks_top = np.unique(all_peaks_top)

        for idx, cell_line in enumerate(cell_lines):
            for i, day in enumerate(plot_df[cell_line].columns):
                y_vals = plot_df[(cell_line, day)].values
                plt.scatter(
                    plot_df["peak"],
                    y_vals,
                    s=50,
                    color=palette[idx],   # use single color, no np.where
                    edgecolor='k',
                    label=f"{cell_line} Day {day}"
                )


        used_y_positions = []
        for peak_val in all_peaks_top:
            y_max = plot_df.loc[plot_df["peak"] == peak_val][cell_lines].max().max()
            offset = 0.05 * plt.ylim()[1]
            direction = 1
            while any(abs((y_max + direction*offset) - y) < 0.02*plt.ylim()[1] for y in used_y_positions):
                offset += 0.03*plt.ylim()[1]
                direction *= -1
            used_y_positions.append(y_max + direction*offset)
            plt.annotate(
                f"{peak_val:.4f}",
                xy=(peak_val, y_max),
                xytext=(peak_val, y_max+direction*offset),
                arrowprops=dict(arrowstyle="->", color='blue'),
                ha='center', va='bottom', color='blue', fontsize=9
            )

        plt.axhline(global_threshold, color="red", linestyle=":", linewidth=1.5,
                    label=f"Top {top_percent}% threshold ({global_threshold:.2f})")
        plt.title("Peak Intensities Across All Cell Lines and Days", fontsize=16)
        plt.xlabel("m/z (peak)", fontsize=14)
        plt.ylabel("Normalized Intensity", fontsize=14)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.savefig(output_pdf, dpi=600)
        plt.close()
        st.success(f"Saved peak PDF: {output_pdf}")

        top_peaks_df = pivot_df.loc[pivot_df[cell_lines].gt(global_threshold).any(axis=1)]
        top_peaks_file = "top_peaks.txt"
        top_peaks_df.to_csv(top_peaks_file, sep="\t", index=True)
        st.success(f"Saved top peaks: {top_peaks_file}")
