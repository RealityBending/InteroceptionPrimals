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

# Convenience functions ======================================================================
mne.set_log_level(verbose="WARNING")


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buffer = io.BytesIO()
    fig.savefig(buffer)
    buffer.seek(0)
    img = PIL.Image.open(buffer)
    return img


def qc_physio(df, info, sub, plot_ecg=[], plot_ppg=[]):
    """Quality control (QC) of physiological signals."""

    # ECG ------------------------------------------------------------------------------------
    nk.ecg_plot(df, info)  # Save ECG plot
    fig = plt.gcf()
    img = ill.image_text(
        sub, color="black", size=100, x=-0.82, y=0.90, image=fig2img(fig)
    )
    plt.close(fig)  # Do not show the plot in the console
    plot_ecg.append(img)

    # PPG ------------------------------------------------------------------------------------
    df["PPG_Raw"] = nk.rescale(df["PPG_Raw"], to=df["PPG_Clean"])
    nk.ppg_plot(df, info)  # Save ECG plot
    fig = plt.gcf()
    img = ill.image_text(
        sub, color="black", size=100, x=-0.82, y=0.90, image=fig2img(fig)
    )
    plot_ppg.append(img)
    plt.close(fig)
    return plot_ecg, plot_ppg


def qc_eeg(raw, sub, plot_psd=[]):
    """Quality control (QC) of EEG."""
    ch_names = ["AF7", "AF8", "TP9", "TP10"]

    fig1, ax = plt.subplots(4, 1, figsize=(6, 5))
    fig1.suptitle(f"{sub}")

    df = raw.to_data_frame()
    df.index = df["time"] / 60
    df[ch_names].plot(ax=ax, subplots=True, linewidth=0.5)

    # PSD
    fig2, ax = plt.subplots(1, 1, figsize=(6, 5))
    psd = raw.compute_psd(picks="eeg", n_fft=256 * 20, fmax=80).to_data_frame()
    psd.plot(x="freq", y=ch_names, ax=ax, logy=True)

    img = ill.image_mosaic([fig2img(i) for i in [fig1, fig2]], nrows=1, ncols=2)

    # To image
    plot_psd.append(img)
    plt.close("all")
    return plot_psd


def qc_hep(epochs, reject_log, sub, plot_hep=[]):
    """Quality control (QC) of HEPs."""
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"{sub}")

    if reject_log is not None:
        reject_log.plot("horizontal", aspect="auto", ax=ax[0], show=False)

    hep = epochs.average(picks=["AF7", "AF8"], method=lambda x: np.nanmean(x, axis=0))
    hep.to_data_frame().plot(x="time", y=["AF7", "AF8"], ax=ax[1])

    # To image
    plot_hep.append(fig2img(fig))
    plt.close("all")
    return plot_hep


def qc_heo(power, itc, sub, plot_heo=[]):
    fig1 = power.plot_topo(
        baseline=None,
        mode="logratio",
        title=f"{sub}:  Time-frequency Power",
        vmin=0,
        # vmax=1e-7,
        fig_facecolor="white",
        fig_background=None,
        font_color="black",
        show=False,
    )

    fig2 = itc.plot_topo(
        title="Inter-Trial coherence",
        vmin=0,
        vmax=1.0,
        cmap="CMRmap",
        fig_facecolor="white",
        fig_background=None,
        font_color="black",
        show=False,
    )

    img = ill.image_mosaic([fig2img(i) for i in [fig1, fig2]], nrows=1, ncols=2)
    plot_heo.append(img)
    plt.close("all")
    return plot_heo


def analyze_hep(raw, events):
    out = {}

    # From Zaccaro et al. (preprint): Epochs were not baseline-corrected (Petzschner et al., 2019).
    # This decision was made to exclude confounding residual CFA evoked by ECG waves that precede
    # the R-peak (P and Q-waves).

    epochs = mne.Epochs(
        raw,
        events,
        tmin=-0.3,
        tmax=0.7,
        detrend=None,
        decim=4,  # Downsample to 500 Hz
        verbose=False,
        preload=True,
    )

    # Autoreject
    try:
        ar = autoreject.AutoReject(verbose=False, picks="eeg")
        epochs, out["autoreject_log"] = ar.fit_transform(epochs, return_log=True)
    except IndexError:
        out["autoreject_log"] = None
    out["epochs"] = epochs

    # Compute HEP Features
    hep = epochs.average(
        picks=["AF7", "AF8", "ECG", "PPG_Muse"],
        method=lambda x: np.nanmean(x, axis=0),
    ).to_data_frame()
    hep.index = hep["time"]
    out["df"] = hep

    hep1 = hep[0.2:0.4][["AF7", "AF8"]]
    hep2 = hep[0.4:0.6][["AF7", "AF8"]]
    rez = pd.DataFrame(
        {
            "HEP_Amplitude_200_400_EEG": [hep1.mean(axis=1).mean()],
            "HEP_Amplitude_400_600_EEG": [hep2.mean(axis=1).mean()],
        }
    )

    for ch in hep1.columns:
        rez[f"HEP_Amplitude_200_400_{ch}"] = hep1[ch].mean()
        rez[f"HEP_Amplitude_400_600_{ch}"] = hep2[ch].mean()

    # Compute Time-frequency Power
    freqs = np.logspace(*np.log10([6, 30]), num=8)  # freqs of interest (log-spaced)
    n_cycles = freqs / 2.0  # different number of cycle per frequency
    power, itc = mne.time_frequency.tfr_morlet(
        epochs,
        freqs=freqs,
        n_cycles=n_cycles,
        use_fft=True,
        return_itc=True,
    )
    out["timefrequency"] = power
    out["itc"] = itc

    # Compute HEO Features
    # power.to_data_frame()

    return rez, out


# Variables ==================================================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"
# path = "C:/Users/dmm56/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"

# Get participant list
meta = pd.read_csv(path + "participants.tsv", sep="\t")

# Initialize variables
df = pd.DataFrame()
df_hep = pd.DataFrame()

qc_rs_psd = []
qc_rs_ecg = []
qc_rs_ppg = []
qc_rs_hep = []
qc_rs_heo = []
qc_hct_psd = []
qc_hct_ecg = []
qc_hct_ppg = []
qc_hct_hep = []
qc_hct_heo = []


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

    # Resting State ==========================================================================

    # Preprocessing --------------------------------------------------------------------------
    print("  - RS - Preprocessing")

    # Open RS assessment
    file = [file for file in os.listdir(path_beh) if "RS" in file]
    file = path_beh + [f for f in file if ".tsv" in f][0]
    rs_beh = pd.read_csv(file, sep="\t").drop(["participant_id"], axis=1)
    dfsub = pd.concat([dfsub, rs_beh.add_prefix("RS_")], axis=1)

    # Open RS file
    file = [file for file in os.listdir(path_eeg) if "RS" in file]
    file = path_eeg + [f for f in file if ".vhdr" in f][0]
    rs = mne.io.read_raw_brainvision(file, preload=True)

    # Detect onset of RS
    events = nk.events_find(
        rs.to_data_frame()["PHOTO"],
        threshold_keep="below",
        duration_min=int(rs.info["sfreq"] * 5),
    )
    assert len(events["onset"]) == 1  # Check that there is only one event

    # Filter EEG
    rs = rs.set_montage("standard_1020")
    rs, _ = mne.set_eeg_reference(rs, ["TP9", "TP10"])
    rs = rs.notch_filter(np.arange(50, 251, 50), picks="eeg")
    rs = rs.filter(1, 30, picks="eeg")
    rs = nk.mne_crop(
        rs, smin=events["onset"][0], smax=events["onset"][0] + events["duration"][0]
    )

    # Fix for recording interruption
    if sub in ["sub-10", "sub-16", "sub-20"]:  # Cut till before the nan
        first_na = np.where(rs.to_data_frame()[["AF7"]].isna())[0][0]
        rs = nk.mne_crop(rs, smin=0, smax=first_na - 1)
    if sub in ["sub-15", "sub-19"]:  # Take second half
        last_na = np.where(rs.to_data_frame()[["AF7"]][0:800000].isna())[0][-1]
        rs = nk.mne_crop(rs, smin=last_na, smax=None)

    # QC
    qc_rs_psd = qc_eeg(rs, sub, plot_psd=qc_rs_psd)

    # Heartbeat Evoked Potentials (HEP) -------------------------------------------------------
    print("  - RS - HEP")

    # Preprocess physio
    ecg, info = nk.bio_process(
        ecg=rs["ECG"][0][0],
        ppg=rs["PPG_Muse"][0][0],
        sampling_rate=rs.info["sfreq"],
    )

    # Find R-peaks
    events, _ = nk.events_to_mne(ecg["ECG_R_Peaks"].values.nonzero()[0])

    rs_hep, out = analyze_hep(rs, events)

    # QC
    qc_rs_ecg, qc_rs_ppg = qc_physio(
        ecg, info, sub, plot_ecg=qc_rs_ecg, plot_ppg=qc_rs_ppg
    )
    qc_rs_hep = qc_hep(out["epochs"], out["autoreject_log"], sub, plot_hep=qc_rs_hep)
    qc_rs_heo = qc_heo(out["timefrequency"], out["itc"], sub, plot_heo=qc_rs_heo)

    # Add Features
    if sub not in ["sub-06", "sub-09"]:
        dfsub = pd.concat([dfsub, rs_hep.add_prefix("RS_")], axis=1)
        out["df"]["participant_id"] = sub
        out["df"]["Condition"] = "RestingState"
        df_hep = pd.concat([df_hep, out["df"]], axis=0)

    # Heartbeat Counting Task (HCT) ----------------------------------------------------------
    print("  - HCT - Preprocessing")
    # Open HCT file
    file = [file for file in os.listdir(path_eeg) if "HCT" in file]
    file = path_eeg + [f for f in file if ".vhdr" in f][0]
    hct = mne.io.read_raw_brainvision(file, preload=True, verbose=False)

    # Filter EEG
    hct = hct.set_montage("standard_1020")
    hct, _ = mne.set_eeg_reference(hct, ["TP9", "TP10"])
    hct = hct.notch_filter(np.arange(50, 251, 50), picks="eeg")
    hct = hct.filter(1, 40, picks="eeg")

    # Find events and crop just before (1 second +/-) first and after last
    events = nk.events_find(
        hct["PHOTO"][0][0], threshold_keep="below", duration_min=15000
    )
    if sub in ["sub-16"]:
        events["onset"] = events["onset"][0:-1]
        events["duration"] = events["duration"][0:-1]
    start_end = [events["onset"][0], events["onset"][-1] + events["duration"][-1]]
    if sub in ["sub-13"]:
        start_end[0] = 2178
    hct = nk.mne_crop(hct, smin=start_end[0] - 2000, smax=start_end[1] + 2000)

    qc_hct_psd = qc_eeg(hct, sub, plot_psd=qc_hct_psd)

    # Find events (again as data was cropped) and epoch
    events = nk.events_find(
        hct["PHOTO"][0][0], threshold_keep="below", duration_min=15000
    )
    assert len(events["onset"]) == 6  # Check that there are 6 epochs (the 6 intervals)

    # HCT - HEP ------------------------------------------------------------------------------
    print("  - HCT - HEP")

    # Preprocess physio
    ecg, _ = nk.bio_process(
        ecg=hct["ECG"][0][0], ppg=hct["PPG_Muse"][0][0], sampling_rate=hct.info["sfreq"]
    )

    # Find R-peaks
    beats = ecg["ECG_R_Peaks"].values.nonzero()[0]
    intervals = [[i, i + j] for i, j in zip(events["onset"], events["duration"])]
    for i, b in enumerate(beats):
        # If it's not in any interval, remove it
        if not any([b >= j[0] and b <= j[1] for j in intervals]):
            beats[i] = 0
    beats = beats[beats != 0]

    hct_hep, out = analyze_hep(hct, nk.events_to_mne(beats)[0])

    # QC
    qc_hct_hep = qc_hep(out["epochs"], out["autoreject_log"], sub, plot_hep=qc_hct_hep)
    qc_hct_heo = qc_heo(out["timefrequency"], out["itc"], sub, plot_heo=qc_hct_heo)

    # Add features
    if sub not in ["sub-03"]:
        dfsub = pd.concat([dfsub, hct_hep.add_prefix("HCT_")], axis=1)
        out["df"]["participant_id"] = sub
        out["df"]["Condition"] = "HCT"
        df_hep = pd.concat([df_hep, out["df"]], axis=0)

    # HCT - Task -----------------------------------------------------------------------------
    print("  - HCT - Task")

    # Process signals
    hct_physio = hct.to_data_frame()[["PHOTO", "ECG", "PPG_Muse"]]
    hct_physio, info = nk.bio_process(
        ecg=hct_physio["ECG"].values,
        ppg=hct_physio["PPG_Muse"].values,
        sampling_rate=2000,
        keep=hct_physio["PHOTO"],
    )
    qc_hct_ecg, qc_hct_ppg = qc_physio(
        hct_physio, info, sub, plot_ecg=qc_hct_ecg, plot_ppg=qc_hct_ppg
    )

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
    if sub == "sub-09":
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

    # Compute interoception scores (Garfinkel et al., 2015)
    dfsub["HCT_Accuracy"] = np.mean(hct_beh["HCT_Accuracy"])
    dfsub["HCT_Sensibility"] = np.nanmean(hct_beh["Confidence"])
    dfsub["HCT_Awareness"] = scipy.stats.spearmanr(
        hct_beh["Confidence"].dropna(), hct_beh["HCT_Accuracy"].dropna()
    ).statistic

    df = pd.concat([df, dfsub], axis=0)


# Clean up and Save data
df = pd.merge(meta, df)
# Keep only columns that do not end with number or _R
# df = df.filter(regex="^(?!.*[0-9]$)(?!.*_R$).*")
df.to_csv("../data/data.csv", index=False)
df_hep.to_csv("../data/data_hep.csv", index=False)

# Save figures
qc_rs_psd = ill.image_mosaic(qc_rs_psd, ncols=2, nrows="auto")
qc_rs_psd.save("figures/signals_qc_rs_psd.png")
qc_rs_ecg = ill.image_mosaic(qc_rs_ecg, ncols=2, nrows="auto")
qc_rs_ecg.save("figures/signals_qc_rs_ecg.png")
qc_rs_ppg = ill.image_mosaic(qc_rs_ppg, ncols=2, nrows="auto")
qc_rs_ppg.save("figures/signals_qc_rs_ppg.png")
qc_rs_hep = ill.image_mosaic(qc_rs_hep, ncols=2, nrows="auto")
qc_rs_hep.save("figures/signals_qc_rs_hep.png")
qc_rs_heo = ill.image_mosaic(qc_rs_heo, ncols=2, nrows="auto")
qc_rs_heo.save("figures/signals_qc_rs_heo.png")
qc_hct_ecg = ill.image_mosaic(qc_hct_ecg, ncols=2, nrows="auto")
qc_hct_ecg.save("figures/signals_qc_hct_ecg.png")
qc_hct_ppg = ill.image_mosaic(qc_hct_ppg, ncols=2, nrows="auto")
qc_hct_ppg.save("figures/signals_qc_hct_ppg.png")
qc_hct_psd = ill.image_mosaic(qc_hct_psd, ncols=2, nrows="auto")
qc_hct_psd.save("figures/signals_qc_hct_psd.png")
qc_hct_hep = ill.image_mosaic(qc_hct_hep, ncols=2, nrows="auto")
qc_hct_hep.save("figures/signals_qc_hct_hep.png")
qc_hct_heo = ill.image_mosaic(qc_hct_heo, ncols=2, nrows="auto")
qc_hct_heo.save("figures/signals_qc_hct_heo.png")

print("Done!")
