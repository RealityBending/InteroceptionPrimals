def load_physio(path, sub):
    """Function to preprocess the files of participants."""
    import os

    import mne
    import neurokit2 as nk
    import numpy as np

    # Convenience functions ======================================================================
    # Find consecutives nans in 3 groups of channels (of different sampling rates)
    def consecutive_nans(raw):
        start = [0, 0, 0]
        other = {"AF7": [], "ECG": [], "PPG_Muse": []}
        for i, ch in enumerate(["AF7", "ECG", "PPG_Muse"]):
            nans = np.where(raw.to_data_frame()[ch].isna())[0]
            if len(nans) != 0:
                consecutive = np.split(nans, np.where(np.diff(nans) != 1)[0] + 1)
                if consecutive[0][0] == 0:
                    start[i] = np.max(consecutive[0]) + 1
                    consecutive = consecutive[1::]
                other[ch] = consecutive
        return np.max(start), other

    # RS ==============================================================================
    def load_rs(path, sub):

        # Path to EEG data
        path_eeg = path + sub + "/eeg/"
        file = [file for file in os.listdir(path_eeg) if "RS" in file]
        file = path_eeg + [f for f in file if ".vhdr" in f][0]

        rs = mne.io.read_raw_brainvision(file, preload=True)
        rs = rs.set_montage("standard_1020")
        # rs.to_data_frame().plot(subplots=True)

        # Detect onset of RS
        events = nk.events_find(
            rs.to_data_frame()["PHOTO"],  # nk.signal_plot(rs["PHOTO"][0][0])
            threshold_keep="below",
            duration_min=int(rs.info["sfreq"] * 5),
        )

        # No Lux, crop out based on GYRO
        # nk.signal_plot(rs["GYRO"][0][0])
        # plt.vlines(
        #     [10000, 10000 + rs.info["sfreq"] * 60 * 8], ymin=0, ymax=10, color="red"
        # )
        if sub in ["sub-57", "sub-80", "sub-91"]:
            events = {"onset": [10000], "duration": [rs.info["sfreq"] * 60 * 8]}
        if sub in ["sub-93"]:
            events = {"onset": [4600], "duration": [rs.info["sfreq"] * 60 * 8]}
        assert len(events["onset"]) == 1  # Check that there is only one event

        rs = nk.mne_crop(
            rs, smin=events["onset"][0], smax=events["onset"][0] + events["duration"][0]
        )

        # Cut out nans at the beginning due to sync delay
        if sub in [
            "sub-24",
            "sub-38",
            "sub-65",
            "sub-68",
            "sub-76",
            "sub-105",
            "sub-108",
            "sub-109",
            "sub-110",
            "sub-111",
            "sub-112",
            "sub-113",
            "sub-114",
            "sub-116",
            "sub-117",
            "sub-118",
            "sub-119",
            "sub-120",
        ]:
            # rs.to_data_frame()
            first_valid, _ = consecutive_nans(rs)
            rs = nk.mne_crop(rs, smin=first_valid, smax=None)
        assert rs.to_data_frame()["ECG"].isna().sum() == 0

        assert (
            len(rs) / rs.info["sfreq"] / 60 > 6
        )  # Check duration is at least 6 minutes

        # Check MUSE signal interruptions
        _, others = consecutive_nans(rs)
        if sub in [
            "sub-10",
            "sub-15",
            "sub-16",
            "sub-19",
            "sub-20",
            "sub-31",
            "sub-42",
            "sub-50",
            "sub-70",
            "sub-76",
            "sub-82",
            "sub-95",
            "sub-117",
            "sub-119",
        ]:
            rs = rs.apply_function(
                nk.signal_fillmissing, picks="PPG_Muse", method="forward"
            )
        else:
            # rs.to_data_frame(["ECG", "AF7", "PPG_Muse", "PHOTO"]).plot(subplots=True)
            assert (
                len(others["PPG_Muse"]) == 0
            )  # Make sure no missing values for PPG-Muse
        return rs

    if sub in ["sub-86"]:  # No RS file
        rs = None
    else:
        rs = load_rs(path, sub)

    # HCT ==============================================================================
    # Open HCT file
    path_eeg = path + sub + "/eeg/"
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
    if sub in [
        "sub-16",
        "sub-52",
        "sub-54",
        "sub-80",
        "sub-102",
    ]:  # drop 1 extra even at the end
        events["onset"] = events["onset"][0:-1]
        events["duration"] = events["duration"][0:-1]

    # Get new start and end of the recording
    start_end = [events["onset"][0], events["onset"][-1] + events["duration"][-1]]
    if sub in ["sub-13", "sub-68", "sub-111", "sub-114"]:  # Because first onset < 2000
        # hct.to_data_frame()
        first_valid, _ = consecutive_nans(hct)
        start_end[0] = 2000 + first_valid
    assert start_end[0] > 2000
    hct = nk.mne_crop(hct, smin=start_end[0] - 2000, smax=start_end[1] + 2000)

    # Check that there are 6 epochs (the 6 intervals)
    assert len(events["onset"]) == 6

    # Check if MUSE signal interruptions
    _, others = consecutive_nans(hct)
    if sub in [
        "sub-03",
        "sub-04",
        "sub-11",
        "sub-12",
        "sub-13",
        "sub-70",
        "sub-89",
        "sub-95",
        "sub-103",
        "sub-107",
        "sub-108",
        "sub-117",
    ]:
        hct = hct.apply_function(
            nk.signal_fillmissing, picks="PPG_Muse", method="forward"
        )
    else:
        # Make sure no missing values for PPG-Muse
        try:
            assert len(others["PPG_Muse"]) == 0
        except:
            # hct.to_data_frame(["ECG", "AF7", "PPG_Muse", "PHOTO"]).plot(subplots=True)
            print(sub)
            assert len(others["PPG_Muse"]) == 0

    return rs, hct
