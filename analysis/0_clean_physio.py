def load_physio(path, sub):
    """Function to preprocess the files of participants."""
    import os
    import mne
    import numpy as np
    import neurokit2 as nk

    # Path to EEG data
    path_eeg = path + sub + "/eeg/"
    path_beh = path + sub + "/beh/"

    # Resting State ==============================================================================
    file = [file for file in os.listdir(path_eeg) if "RS" in file]
    file = path_eeg + [f for f in file if ".vhdr" in f][0]

    rs = mne.io.read_raw_brainvision(file, preload=True)
    rs = rs.set_montage("standard_1020")

    # Detect onset of RS
    events = nk.events_find(
        rs.to_data_frame()["PHOTO"],
        threshold_keep="below",
        duration_min=int(rs.info["sfreq"] * 5),
    )
    assert len(events["onset"]) == 1  # Check that there is only one event

    # Fix for recording interruption
    if sub in ["sub-10", "sub-16", "sub-20"]:  # Cut till before the nan
        first_na = np.where(rs.to_data_frame()[["AF7"]].isna())[0][0]
        rs = nk.mne_crop(rs, smin=0, smax=first_na - 1)
    if sub in ["sub-15", "sub-19"]:  # Take second half
        last_na = np.where(rs.to_data_frame()[["AF7"]][0:800000].isna())[0][-1]
        rs = nk.mne_crop(rs, smin=last_na, smax=None)
    if sub in ["sub-24"]:  # Crop out nans at the beginning

        def consecutive_nans(ch="AF7"):
            nans = np.where(rs.to_data_frame()[ch].isna())[0]
            return np.max(np.split(nans, np.where(np.diff(nans) != 1)[0] + 1)[0])

        nans = np.max([consecutive_nans(ch) for ch in ["AF7", "ECG", "PPG_Muse"]])
        rs = nk.mne_crop(rs, smin=nans, smax=None)
    if sub in ["sub-38"]:  # Crop out nans at the beginning
        last_na = np.where(rs.to_data_frame()[["ECG"]][0:800000].isna())[0][-1] + 1
        rs = nk.mne_crop(rs, smin=last_na, smax=None)

    return rs
