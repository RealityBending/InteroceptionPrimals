import io
import os

# import autoreject
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


def qc_physio(df, plot_ecg=[], plot_ppg=[]):
    """Quality control (QC) of physiological signals."""

    # ECG ------------------------------------------------------------------------------------
    nk.ecg_plot(df, sampling_rate=2000)  # Save ECG plot
    fig = plt.gcf()
    img = ill.image_text(
        sub, color="black", size=100, x=-0.82, y=0.90, image=fig2img(fig)
    )
    plt.close(fig)  # Do not show the plot in the console
    plot_ecg.append(img)

    # PPG ------------------------------------------------------------------------------------
    fig = nk.ppg_segment(df["PPG_Clean"], sampling_rate=2000, show="return")
    img = ill.image_text(
        sub, color="black", size=100, x=-0.82, y=0.90, image=fig2img(fig)
    )
    plot_ppg.append(img)
    plt.close(fig)  # Do not show the plot in the console
    return plot_ecg, plot_ppg


# def qc_eeg(raw, plot_psd=[]):
#     """Quality control (QC) of PSD."""
#     psd = raw.compute_psd(picks="eeg", fmax=80).to_data_frame()
#     psd.plot(x="freq", y=["AF7", "AF8", "TP9", "TP10"])
#     plt.yscale("log")
#     fig = plt.gcf()
#     img = ill.image_text(
#         sub, color="black", size=100, x=-0.82, y=0.90, image=fig2img(fig)
#     )
#     plt.close(fig)  # Do not show the plot in the console
#     plot_psd.append(img)
#     return plot_psd


# Variables ==================================================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"

# Get participant list
meta = pd.read_csv(path + "participants.tsv", sep="\t")


# Initialize variables
qc_hct_ecg = []
qc_hct_ppg = []
qc_rs_psd = []
qc_rs_hep = []
df = pd.DataFrame()

# sub = "sub-02"
# Loop through participants ==================================================================
for sub in meta["participant_id"].values:
    # Print progress and comments
    print(sub)
    print("  - " + meta[meta["participant_id"] == sub]["Comments"].values[0])

    # Path to EEG data
    path_eeg = path + sub + "/eeg/"
    path_beh = path + sub + "/beh/"

    # Questionnaires -------------------------------------------------------------------------
    file = [file for file in os.listdir(path_beh) if "Questionnaires" in file]
    file = path_beh + [file for file in file if ".tsv" in file][0]
    dfsub = pd.read_csv(file, sep="\t")

    # # Heartbeat Evoked Potentials (HEP) ------------------------------------------------------
    # # Open RS file
    # file = [file for file in os.listdir(path_eeg) if "RS" in file]
    # file = path_eeg + [file for file in file if ".vhdr" in file][0]
    # rs = mne.io.read_raw_brainvision(file, preload=True)
    # rs = rs.set_montage("standard_1020")

    # # Preprocess
    # rs, _ = mne.set_eeg_reference(rs, ["TP9", "TP10"])
    # rs = rs.filter(1, 40, fir_design="firwin")

    # # NK pipeline
    # df = rs.to_data_frame()[["time", "AF7", "AF8", "PHOTO", "ECG"]]
    # df["EEG"] = df[["AF7", "AF8"]].mean(axis=1) / 1000000
    # events = nk.events_find(df["PHOTO"], threshold_keep="below", duration_min=50000)
    # df = df.iloc[events["onset"][0] : events["onset"][0] + events["duration"][0]]
    # rs_physio, _ = nk.ecg_process(df["ECG"].values, sampling_rate=rs.info["sfreq"])
    # epochs = nk.epochs_create(
    #     df,
    #     rs_physio["ECG_R_Peaks"].values.nonzero()[0],
    #     epochs_start=-0.5,
    #     epochs_end=1,
    # )
    # for i, epoch in epochs.items():
    #     plt.plot(epoch.index, epoch["EEG"], color="red", alpha=0.1)
    #     # plt.plot(epoch.index, epoch["AF8"], color="blue", alpha=0.1)
    #     plt.ylim(-2, 2)

    # # Crops to RS time
    # events = nk.events_find(
    #     rs.to_data_frame()["PHOTO"], threshold_keep="below", duration_min=50000
    # )
    # assert len(events["onset"]) == 1  # Check that there is only one event
    # rs = nk.mne_crop(
    #     rs, smin=events["onset"][0], smax=events["onset"][0] + events["duration"][0]
    # )
    # # rs = rs.crop(
    # #     tmin=rs.times[events["onset"][0]],
    # #     tmax=rs.times[events["onset"][0] + events["duration"][0]],
    # # )

    # # QC
    # qc_eeg(rs, plot_psd=signals_qc_rs_psd)
    # # rs.plot_sensors(show_names=True)
    # # rs.plot()

    # # Autoreject
    # chunks = mne.make_fixed_length_events(rs, duration=1.0)
    # epochs = mne.Epochs(rs, chunks, tmin=0, tmax=1.0, baseline=None, preload=True)
    # if sub in ["sub-04", "sub-06"]:  # These ppts error
    #     reject = {}
    # else:
    #     reject = autoreject.get_rejection_threshold(epochs, verbose=False)
    #     thresholds = autoreject.compute_thresholds(epochs, method="random_search")

    # # Find R-peaks
    # rs_physio, _ = nk.ecg_process(
    #     rs.to_data_frame()["ECG"].values, sampling_rate=rs.info["sfreq"]
    # )
    # events, event_id = nk.events_to_mne(rs_physio["ECG_R_Peaks"].values.nonzero()[0])
    # # events2, _, _ = mne.preprocessing.find_ecg_events(rs, event_id=0, ch_name="ECG")
    # epochs = mne.Epochs(
    #     rs,
    #     events,
    #     # event_id=event_id,
    #     picks="eeg",
    #     tmin=-0.3,
    #     tmax=0.7,
    #     verbose=False,
    #     preload=True,
    # )
    # epochs = epochs.drop_bad(reject=reject)
    # # epochs.plot_drop_log()
    # # fig = epochs.plot(events=events)

    # df_hep = epochs.to_data_frame()
    # df_hep["EEG"] = df_hep[["AF7", "AF8"]].mean(axis=1)
    # df_hep["participant_id"] = sub
    # signals_qc_rs_hep.append(df_hep[["participant_id", "epoch", "time", "EEG"]])

    # hep = epochs.average(picks=["AF7", "AF8"], method=lambda x: np.nanmean(x, axis=0))
    # signals_qc_rs_hep.append(hep)
    # # hep.to_data_frame()

    # # hep.plot(gfp=True)
    # # grand_average = mne.grand_average([hep])
    # # grand_average.plot()

    # Heartbeat Counting Task (HCT) ----------------------------------------------------------
    # Open HCT file
    file = [file for file in os.listdir(path_eeg) if "HCT" in file]
    file = path_eeg + [file for file in file if ".vhdr" in file][0]
    hct = mne.io.read_raw_brainvision(file, preload=True, verbose=False)
    hct = hct.to_data_frame()[["PHOTO", "ECG", "PPG_Muse"]]
    # Remove NA
    for m in ["bfill", "ffill"]:
        hct = hct.fillna(method=m)

    # Find events and crop just before (1 second +/-) first and after last
    events = nk.events_find(hct["PHOTO"], threshold_keep="below", duration_min=15000)
    start_end = [events["onset"][0], events["onset"][-1] + events["duration"][-1]]
    if sub in ["sub-13"]:
        start_end[0] = 2000
    hct = hct.iloc[start_end[0] - 2000 : start_end[1] + 2000]

    # Process signals
    hct, _ = nk.bio_process(
        ecg=hct["ECG"].values,
        ppg=hct["PPG_Muse"],
        sampling_rate=2000,
        keep=hct["PHOTO"],
    )
    qc_hct_ecg, qc_hct_ppg = qc_physio(hct, plot_ecg=qc_hct_ecg, plot_ppg=qc_hct_ppg)

    # Find events (again as data was cropped) and epoch
    events = nk.events_find(hct["PHOTO"], threshold_keep="below", duration_min=15000)
    epochs = nk.epochs_create(
        hct, events, sampling_rate=2000, epochs_start=0, epochs_end="from_events"
    )
    assert len(epochs) == 6  # Check that there are 6 epochs (the 6 intervals)

    # Load behavioral data
    file = [file for file in os.listdir(path_beh) if "HCT" in file]
    file = path_beh + [file for file in file if ".tsv" in file][0]
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
df = df.filter(regex="^(?!.*[0-9]$)(?!.*_R$).*")
df.to_csv("../data/data.csv", index=False)

# Save figures
qc_hct_ecg = ill.image_mosaic(qc_hct_ecg, ncols=2, nrows="auto")
qc_hct_ecg.save("figures/signals_qc_hct_ecg.png")
qc_hct_ppg = ill.image_mosaic(qc_hct_ppg, ncols=2, nrows="auto")
qc_hct_ppg.save("figures/signals_qc_hct_ppg.png")
# signals_qc_rs_psd = ill.image_mosaic(signals_qc_rs_psd, ncols=2, nrows="auto")
# signals_qc_rs_psd.save("figures/signals_qc_rs_psd.png")

# fig = plt.figure()
# for sub in signals_qc_rs_psd["participant_id"].unique():
#     dat = signals_qc_rs_psd[signals_qc_rs_psd["participant_id"] == sub]
#     fig = dat.plot(x="freq", y=["AF7", "AF8", "TP9", "TP10"])
# fig2img(fig)


# %matplotlib inline
# signals_qc_rs_hep = pd.concat(signals_qc_rs_hep, axis=0)
# for sub in signals_qc_rs_hep["participant_id"].unique():
#     dat = signals_qc_rs_hep[signals_qc_rs_hep["participant_id"] == sub]
#     for epoch in dat["epoch"].unique():
#         dat2 = dat[dat["epoch"] == epoch]
#         plt.plot(dat2["time"], dat2["EEG"], color="black", alpha=0.02)
# plt.show()
# plt.close()
# signals_qc_rs_hep[5].to_data_frame()
# signals_qc_rs_hep.pop(4)
# ga = mne.grand_average(signals_qc_rs_hep)
# mne.channels.combine_channels(ga, {"HEP":[0, 1]}, method="mean").plot()
# ga.plot()

print("Done!")
