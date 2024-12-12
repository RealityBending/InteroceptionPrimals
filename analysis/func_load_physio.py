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

    if sub in ["sub-57"]:  # No Lux, crop out based on GYRO
        # nk.signal_plot(rs["GYRO"][0][0])
        # plt.vlines(
        #     [10000, 10000 + rs.info["sfreq"] * 60 * 8], ymin=0, ymax=10, color="red"
        # )
        events = {"onset": [10000], "duration": [rs.info["sfreq"] * 60 * 8]}

    assert len(events["onset"]) == 1  # Check that there is only one event

    rs = nk.mne_crop(
        rs, smin=events["onset"][0], smax=events["onset"][0] + events["duration"][0]
    )
    assert len(rs) > rs.info["sfreq"] * 60 * 6  # Check duration is at least 6 minutes

    # Fix for recording interruption
    if sub in ["sub-10", "sub-16", "sub-20"]:  # Cut till before the nan
        first_na = np.where(rs.to_data_frame()[["AF7"]].isna())[0][0]
        rs = nk.mne_crop(rs, smin=0, smax=first_na - 1)
    if sub in ["sub-15", "sub-19"]:  # Take second half
        last_na = np.where(rs.to_data_frame()[["AF7"]][0:800000].isna())[0][-1]
        rs = nk.mne_crop(rs, smin=last_na, smax=None)
    if sub in ["sub-24", "sub-50"]:  # Crop out nans at the beginning

        def consecutive_nans(ch="AF7"):
            nans = np.where(rs.to_data_frame()[ch].isna())[0]
            return np.max(np.split(nans, np.where(np.diff(nans) != 1)[0] + 1)[0])

        nans = np.max([consecutive_nans(ch) for ch in ["AF7", "ECG", "PPG_Muse"]])
        rs = nk.mne_crop(rs, smin=nans, smax=None)
    if sub in ["sub-38"]:  # Crop out nans at the beginning
        last_na = np.where(rs.to_data_frame()[["ECG"]][0:800000].isna())[0][-1] + 1
        rs = nk.mne_crop(rs, smin=last_na, smax=None)

    # HCT ==============================================================================
    # Open HCT file
    file = [file for file in os.listdir(path_eeg) if "HCT" in file]
    file = path_eeg + [f for f in file if ".vhdr" in f][0]
    hct = mne.io.read_raw_brainvision(file, preload=True, verbose=False)

    # Filter EEG
    hct = hct.set_montage("standard_1020")

    # Find events and crop just before (1 second +/-) first and after last
    events = nk.events_find(
        hct["PHOTO"][0][0], threshold_keep="below", duration_min=15000
    )
    # nk.signal_plot(hct["PHOTO"][0][0])

    # Fix manual cases
    if sub in ["sub-16", "sub-52", "sub-54"]:
        events["onset"] = events["onset"][0:-1]
        events["duration"] = events["duration"][0:-1]

    # Get new start and end of the recording
    start_end = [events["onset"][0], events["onset"][-1] + events["duration"][-1]]
    if sub in ["sub-13"]:  # Because first onset < 2000
        first_valid = hct["PPG_Muse"][0][0]
        first_valid = np.where(~np.isnan(first_valid))[0][0]
        start_end[0] = 2000 + first_valid
    hct = nk.mne_crop(hct, smin=start_end[0] - 2000, smax=start_end[1] + 2000)

    assert len(events["onset"]) == 6  # Check that there are 6 epochs (the 6 intervals)

    # Interpolate signal interruptions
    if sub in ["sub-13"]:
        hct = hct.apply_function(
            nk.signal_fillmissing, picks="PPG_Muse", method="backward"
        )

    return rs, hct
