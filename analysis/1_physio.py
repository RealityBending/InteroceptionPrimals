import os

import matplotlib.pyplot as plt
import mne
import neurokit2 as nk
import numpy as np
import pandas as pd
import PIL
import pyllusion as ill
import requests
import scipy.stats
import gc


mne.set_log_level(verbose="WARNING")

# Convenience functions ======================================================================
# Download the load_physio() function
exec(
    requests.get(
        "https://raw.githubusercontent.com/RealityBending/InteroceptionPrimals/main/analysis/func_load_physio.py"
    ).text
)


def qc_physio(df, info, sub, plot_ecg=[], plot_ppg=[]):
    """Quality control (QC) of physiological signals."""

    # ECG ------------------------------------------------------------------------------------
    nk.ecg_plot(df, info)  # Save ECG plot
    fig = plt.gcf()

    # Remove legend and resize
    [ax.legend().set_visible(False) for ax in fig.axes]
    fig.set_size_inches(fig.get_size_inches() * 0.4)

    # Add text
    img = ill.image_text(
        sub, color="black", size=30, x=-0.82, y=0.90, image=nk.fig2img(fig)
    )
    plt.close(fig)  # Do not show the plot in the console
    plot_ecg.append(img)

    # PPG ------------------------------------------------------------------------------------
    if plot_ppg is not None:
        df["PPG_Raw"] = nk.rescale(df["PPG_Raw"], to=df["PPG_Clean"])
        nk.ppg_plot(df, info)  # Save ECG plot
        fig = plt.gcf()

        # Remove legend and resize
        [ax.legend().set_visible(False) for ax in fig.axes]
        fig.set_size_inches(fig.get_size_inches() * 0.4)

        # Add text
        img = ill.image_text(
            sub, color="black", size=30, x=-0.82, y=0.90, image=nk.fig2img(fig)
        )
        plot_ppg.append(img)
        plt.close(fig)
    return plot_ecg, plot_ppg


# Variables ==================================================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/InteroceptionPrimals/Reality Bending Lab - InteroceptionPrimals/"
# path = "C:/Users/dmm56/Box/Data/InteroceptionPrimals/Reality Bending Lab - InteroceptionPrimals/"
# path = "C:/Users/asf25/Box/InteroceptionPrimals/Reality Bending Lab - InteroceptionPrimals/"

# Get participant list
meta = pd.read_csv(path + "participants.tsv", sep="\t")

# Initialize variables
df = pd.DataFrame()
df = pd.read_csv("../data/rawdata_participants.csv")

qc = {"rs_ecg": [], "rs_ppg": [], "hct_ecg": [], "hct_ppg": []}

# Loop through participants ==================================================================
for i, sub in enumerate(meta["participant_id"].values):

    # Print progress and comments
    print(sub)
    print("  * " + meta[meta["participant_id"] == sub]["Comments"].values[0])

    if "participant_id" in df.columns and sub in df["participant_id"].values:
        print("  - Already processed")
        continue

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
    if sub not in ["sub-86"]:  # No RS file
        # Preprocessing --------------------------------------------------------------------------
        print("  - RS - Preprocessing")

        srate = rs.info["sfreq"]
        rs, info = nk.bio_process(
            ecg=rs["ECG"][0][0],
            ppg=rs["PPG_Muse"][0][0],
            sampling_rate=srate,
        )

        # QC
        qc["rs_ecg"], qc["rs_ppg"] = qc_physio(
            rs, info, sub, plot_ecg=qc["rs_ecg"], plot_ppg=qc["rs_ppg"]
        )

        # Hear Rate Variability (HRV) -------------------------------------------------------------
        hrv = nk.hrv(rs["ECG_R_Peaks"].values.nonzero()[0], sampling_rate=srate)
        idx = [
            "MeanNN",
            "SDNN",
            "RMSSD",
            "SampEn",
            "HF",
            "HFD",
            "LFHF",
            "IALS",
            "Ca",
            "AI",
        ]
        hrv = hrv[["HRV_" + s for s in idx]]
        dfsub = pd.concat([dfsub, hrv], axis=1)

    # Heartbeat Counting Task (HCT) ===========================================================
    if sub not in ["sub-146"]:  # No photosensor
        # Preprocessing --------------------------------------------------------------------------
        print("  - HCT - Preprocessing")

        srate = hct.info["sfreq"]
        # Load behavioral data
        file = [file for file in os.listdir(path_beh) if "HCT" in file]
        file = path_beh + [f for f in file if ".tsv" in f][0]
        hct_beh = pd.read_csv(file, sep="\t")

        # Find events (again as data was cropped) and epoch
        events = nk.events_find(
            hct["PHOTO"][0][0], threshold_keep="below", duration_min=15000
        )

        # Make sure there are 6 events
        assert len(events["onset"]) == 6

        # Make sure the are of expected duration
        if sub not in ["sub-68", "sub-114"]:
            durations = events["duration"] / srate
            assert np.max(np.abs(durations - hct_beh["Duration"].values)) < 0.50

        # - sub68 has one slitghtly shorter event (we can keep it)
        # if sub not in ["sub-68"]:

        # Process signals
        hct, info = nk.bio_process(
            ecg=hct["ECG"][0][0],
            ppg=hct["PPG_Muse"][0][0],
            sampling_rate=srate,
            keep=pd.DataFrame({"PHOTO": hct["PHOTO"][0][0]}),
        )

        # QC
        qc["hct_ecg"], qc["hct_ppg"] = qc_physio(
            hct, info, sub, plot_ecg=qc["hct_ecg"], plot_ppg=qc["hct_ppg"]
        )

        # Analysis --------------------------------------------------------------------------
        # Make epochs
        epochs = nk.epochs_create(
            hct,
            events,
            sampling_rate=srate,
            epochs_start=0,
            epochs_end="from_events",
        )

        # Count R peaks in each epoch
        hct_beh["N_R_peaks"] = [
            epoch["ECG_R_Peaks"].sum() for i, epoch in epochs.items()
        ]
        hct_beh["N_PPG_peaks"] = [
            epoch["PPG_Peaks"].sum() for i, epoch in epochs.items()
        ]

        # Manual fix (based on comments)
        peaks = hct_beh["N_R_peaks"].values
        if sub == "sub-09":  # No ECG
            peaks = hct_beh["N_PPG_peaks"].values

        # Compute accuracy
        if sub in ["sub-72"]:
            hct_beh["HCT_Accuracy"] = np.nan
        else:
            hct_beh["HCT_Accuracy"] = 1 - ((np.abs(hct_beh["Answer"] - peaks)) / peaks)

        # Manual fixes (based on comments)
        if sub == "sub-07":
            hct_beh.loc[2, ["Confidence", "HCT_Accuracy"]] = np.nan
        if sub == "sub-11":
            hct_beh.loc[0:2, ["Confidence", "HCT_Accuracy"]] = np.nan

        # Replace zeros with nans
        if 0 in hct_beh["Answer"].values:
            # print("    - Zero in Answer")
            hct_beh["Answer"] = hct_beh["Answer"].replace(0, np.nan)

        # Deal with short epochs
        if sub in ["sub-114"]:
            hct_beh.loc[0, ["HCT_Accuracy"]] = np.nan

        valid = hct_beh["Answer"].notna()

        # Compute interoception scores (Garfinkel et al., 2015) -----------------------------------
        if sub not in ["sub-72"]:
            dfsub["HCT_Accuracy"] = np.nanmean(hct_beh["HCT_Accuracy"])
            dfsub["HCT_Sensibility"] = np.nanmean(hct_beh["Confidence"])
            dfsub["HCT_Awareness"] = scipy.stats.spearmanr(
                hct_beh["Confidence"][valid], hct_beh["HCT_Accuracy"][valid]
            ).statistic

        # Hear Rate Variability (HRV) -------------------------------------------------------------
        print("  - HCT - HRV")

        hrv = pd.concat(
            [
                nk.hrv_time(
                    e["ECG_R_Peaks"].values.nonzero()[0],
                    sampling_rate=srate,
                )
                for e in epochs.values()
            ]
        )
        hrv = hrv[["HRV_" + s for s in ["MeanNN", "SDNN", "RMSSD"]]].mean(axis=0)
        hrv.index = [s + "_HCT" for s in hrv.index]
        dfsub = pd.concat([dfsub, pd.DataFrame(hrv).T], axis=1)

        # Append participant to rest --------------------------------------------------------------
        df = pd.concat([df, dfsub], axis=0)

        del rs, hct, epochs
        plt.close()
        gc.collect()

    # Save data ==============================================================================
    if i in [29, 59, 89, 119, len(meta["participant_id"].values) - 1]:
        print("**SAVING DATA**")
        pd.merge(meta, df, on="participant_id", suffixes=("", "_DUP")).filter(
            regex="^(?!.*_DUP)"
        ).to_csv("../data/rawdata_participants.csv", index=False)

        # Save figures
        if len(qc["rs_ecg"]) > 10:
            ill.image_mosaic(qc["rs_ecg"], ncols=6, nrows="auto").save(
                f"signals/rs_ecg_{i+1}.png"
            )
            ill.image_mosaic(qc["rs_ppg"], ncols=6, nrows="auto").save(
                f"signals/rs_ppg_{i+1}.png"
            )
            ill.image_mosaic(qc["hct_ecg"], ncols=6, nrows="auto").save(
                f"signals/hct_ecg_{i+1}.png"
            )
            ill.image_mosaic(qc["hct_ppg"], ncols=6, nrows="auto").save(
                f"signals/hct_ppg_{i+1}.png"
            )

            # Reset
            qc = {"rs_ecg": [], "rs_ppg": [], "hct_ecg": [], "hct_ppg": []}


print("Done!")
