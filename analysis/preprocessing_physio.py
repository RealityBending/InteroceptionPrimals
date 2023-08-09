import io
import os

import matplotlib.pyplot as plt
import mne
import neurokit2 as nk
import numpy as np
import pandas as pd
import PIL
import pyllusion as ill


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io

    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = PIL.Image.open(buf)
    return img


# Variables =======================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/PrimalsInteroception/Reality Bending Lab - PrimalsInteroception/"

# Get participant list
df_ppt = pd.read_csv(path + "participants.tsv", sep="\t")


# Initialize variables
signals_qc_hct_ecg = []

for sub in df_ppt["participant_id"].values:
    # Print progress and comments
    print(sub)
    print("  - " + df_ppt[df_ppt["participant_id"] == sub]["Comments"].values[0])

    # Path to EEG data
    path_eeg = path + sub + "/eeg/"

    # Heartbeat Counting Task (HCT) =======================================================
    # Open HCT file
    file = [file for file in os.listdir(path_eeg) if "HCT" in file]
    file = path_eeg + [file for file in file if ".vhdr" in file][0]
    hct = mne.io.read_raw_brainvision(file, preload=True, verbose=False)
    hct = hct.to_data_frame()[["PHOTO", "ECG", "PPG_Muse"]]
    hct = hct.dropna()  # Remove NA

    hct, _ = nk.bio_process(
        ecg=hct["ECG"].values,
        ppg=hct["PPG_Muse"],
        sampling_rate=2000,
        keep=hct["PHOTO"],
    )

    # Save ECG plot
    nk.ecg_plot(hct, sampling_rate=2000)
    fig = plt.gcf()
    img = ill.image_text(
        sub, color="white", size=100, x=-0.82, y=0.90, image=fig2img(fig)
    )
    plt.close(fig)
    signals_qc_hct_ecg.append(img)

signals_qc_hct_ecg = ill.image_mosaic(signals_qc_hct_ecg, ncols=2, nrows="auto")
signals_qc_hct_ecg.save("figures/signals_qc_hct_ecg.png")
