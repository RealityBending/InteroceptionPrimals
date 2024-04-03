import io
import os
import time

import autoreject
import matplotlib.pyplot as plt
import mne
import neurokit2 as nk
import numpy as np
import pandas as pd
import PIL
import pyllusion as ill
import scipy.stats
import urllib.request

mne.set_log_level(verbose="WARNING")

# Convenience functions ======================================================================
r = urllib.request.urlopen(
    "https://raw.githubusercontent.com/RealityBending/PrimalsInteroception/main/analysis/0_clean_physio.py"
).read()
eval(compile(r.decode(), "<string>", "single"))


def qc_physio(df, info, sub, plot_ecg=[], plot_ppg=[]):
    """Quality control (QC) of physiological signals."""

    # ECG ------------------------------------------------------------------------------------
    nk.ecg_plot(df, info)  # Save ECG plot
    fig = plt.gcf()
    img = ill.image_text(
        sub, color="black", size=100, x=-0.82, y=0.90, image=nk.fig2img(fig)
    )
    plt.close(fig)  # Do not show the plot in the console
    plot_ecg.append(img)

    # PPG ------------------------------------------------------------------------------------
    if plot_ppg is not None:
        df["PPG_Raw"] = nk.rescale(df["PPG_Raw"], to=df["PPG_Clean"])
        nk.ppg_plot(df, info)  # Save ECG plot
        fig = plt.gcf()
        img = ill.image_text(
            sub, color="black", size=100, x=-0.82, y=0.90, image=nk.fig2img(fig)
        )
        plot_ppg.append(img)
        plt.close(fig)
    return plot_ecg, plot_ppg


# Variables ==================================================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"
# path = "C:/Users/dmm56/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"

# Get participant list
meta = pd.read_csv(path + "participants.tsv", sep="\t")

# Initialize variables
df = pd.DataFrame()
qc = {"rs_ecg": [], "rs_ppg": [], "hct_ecg": [], "hct_ppg": []}


# sub = "sub-19"
# Loop through participants ==================================================================
for sub in meta["participant_id"].values:
    # Print progress and comments
    print(sub)
    print("  * " + meta[meta["participant_id"] == sub]["Comments"].values[0])

    # Path to EEG data
    path_eeg = path + sub + "/eeg/"
    path_beh = path + sub + "/beh/"

    # Questionnaires -------------------------------------------------------------------------
    file = [file for file in os.listdir(path_beh) if "Questionnaires" in file]
    file = path_beh + [f for f in file if ".tsv" in f][0]
    dfsub = pd.read_csv(file, sep="\t")

    # Load data
    rs, hct = load_physio(path, sub)  # Function loaded from script at URL

    # Resting State ==========================================================================

    # Preprocessing --------------------------------------------------------------------------
    print("  - RS - Preprocessing")

    bio, info = nk.bio_process(
        ecg=rs["ECG"][0][0],
        ppg=rs["PPG_Muse"][0][0],
        sampling_rate=rs.info["sfreq"],
    )

    # QC
    qc["rs_ecg"], qc["rs_ppg"] = qc_physio(
        bio, info, sub, plot_ecg=qc["rs_ecg"], plot_ppg=qc["rs_ppg"]
    )

    # Hear Rate Variability (HRV) -------------------------------------------------------------
    hrv = nk.hrv(bio["ECG_R_Peaks"].values.nonzero()[0], sampling_rate=rs.info["sfreq"])
    idx = ["MeanNN", "SDNN", "RMSSD", "SampEn", "HF", "HFD", "LFHF", "IALS", "Ca", "AI"]
    hrv = hrv[["HRV_" + s for s in idx]]
    dfsub = pd.concat([dfsub, hrv], axis=1)

    # Heartbeat Counting Task (HCT) ===========================================================

    # Preprocessing --------------------------------------------------------------------------
    print("  - HCT - Preprocessing")

    # Find events (again as data was cropped) and epoch
    events = nk.events_find(
        hct["PHOTO"][0][0], threshold_keep="below", duration_min=15000
    )
    assert len(events["onset"]) == 6  # Check that there are 6 epochs (the 6 intervals)

    # Process signals
    hct_physio = hct.to_data_frame()[["PHOTO", "ECG", "PPG_Muse"]]
    hct_physio, info = nk.bio_process(
        ecg=hct_physio["ECG"].values,
        ppg=hct_physio["PPG_Muse"].values,
        sampling_rate=2000,
        keep=hct_physio["PHOTO"],
    )

    # QC
    qc["hct_ecg"], qc["hct_ppg"] = qc_physio(
        hct_physio, info, sub, plot_ecg=qc["hct_ecg"], plot_ppg=qc["hct_ppg"]
    )

    # Analysis --------------------------------------------------------------------------
    # Make epochs
    epochs = nk.epochs_create(
        hct_physio, events, sampling_rate=2000, epochs_start=0, epochs_end="from_events"
    )

    # Load behavioral data
    file = [file for file in os.listdir(path_beh) if "HCT" in file]
    file = path_beh + [f for f in file if ".tsv" in f][0]
    hct_beh = pd.read_csv(file, sep="\t")

    # Count R peaks in each epoch
    hct_beh["N_R_peaks"] = [epoch["ECG_R_Peaks"].sum() for i, epoch in epochs.items()]
    hct_beh["N_PPG_peaks"] = [epoch["PPG_Peaks"].sum() for i, epoch in epochs.items()]

    # Manual fix (based on comments)
    peaks = hct_beh["N_R_peaks"].values
    if sub == "sub-09":  # No ECG
        peaks = hct_beh["N_PPG_peaks"].values

    # Compute accuracy
    hct_beh["HCT_Accuracy"] = 1 - (abs(peaks - hct_beh["Answer"])) / (
        (peaks + hct_beh["Answer"]) / 2
    )

    # Manual fixes (based on comments)
    if sub == "sub-07":
        hct_beh.loc[2, ["Confidence", "HCT_Accuracy"]] = np.nan
    if sub == "sub-11":
        hct_beh.loc[0:2, ["Confidence", "HCT_Accuracy"]] = np.nan

    # Compute interoception scores (Garfinkel et al., 2015) -----------------------------------
    dfsub["HCT_Accuracy"] = np.mean(hct_beh["HCT_Accuracy"])
    dfsub["HCT_Sensibility"] = np.nanmean(hct_beh["Confidence"])
    dfsub["HCT_Awareness"] = scipy.stats.spearmanr(
        hct_beh["Confidence"].dropna(), hct_beh["HCT_Accuracy"].dropna()
    ).statistic

    # Hear Rate Variability (HRV) -------------------------------------------------------------

    hrv = pd.concat(
        [
            nk.hrv_time(
                e["ECG_R_Peaks"].values.nonzero()[0], sampling_rate=rs.info["sfreq"]
            )
            for e in epochs.values()
        ]
    )
    hrv = hrv[["HRV_" + s for s in ["MeanNN", "SDNN", "RMSSD"]]].mean(axis=0)
    hrv.index = [s + "_HCT" for s in hrv.index]
    dfsub = pd.concat([dfsub, pd.DataFrame(hrv).T], axis=1)

    # Append participant to rest --------------------------------------------------------------
    df = pd.concat([df, dfsub], axis=0)


# Clean up and Save data
df = pd.merge(meta, df)
df.to_csv("../data/data_participants.csv", index=False)

# Save figures
ill.image_mosaic(qc["rs_ecg"], ncols=4, nrows="auto").save("signals/rs_ecg.png")
ill.image_mosaic(qc["rs_ppg"], ncols=4, nrows="auto").save("signals/rs_ppg.png")
ill.image_mosaic(qc["hct_ecg"], ncols=4, nrows="auto").save("signals/hct_ecg.png")
ill.image_mosaic(qc["hct_ppg"], ncols=4, nrows="auto").save("signals/hct_ppg.png")


print("Done!")
