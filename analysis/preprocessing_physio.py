import os

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd

# Variables =======================================================
# Change the path to your local data folder.
# The data can be downloaded from OpenNeuro (TODO).
path = "C:/Users/domma/Box/Data/PrimalsInteroception/pilots/physio/"


# Convenience functions ============================================
def load_data(path, task="HBC"):
    files = os.listdir(path)
    df, info = nk.read_xdf(filename=path + [file for file in files if task in file][0])

    # # Test
    # df1 = df.iloc[0:3000]
    # df2 = info["data"][0].iloc[0:300]
    # plt.plot(df1.index, df1["TP9"])
    # plt.plot(df2.index, df2["TP9"])

    # df3 = info["data"][4].iloc[0:1000]
    # plt.plot(df1.index, df1["ECG"])
    # plt.plot(df3.index, df3["ECGBIT1"])

    df = df.reset_index()

    df = df.drop(
        columns=[
            "Right AUX",
            "X",
            "Y",
            "Z",
            "RED",
            "GYRO_X",
            "GYRO_Y",
            "GYRO_Z",
            "nSeq",
            "index",
        ]
    )

    df = df.rename(
        columns={
            "PPG": "PPG_Muse",
            "RESPBIT0": "RSP",
            "ECGBIT1": "ECG",
            "PULSEOXI2": "PPG",
            "LUX3": "PHOTO",
        }
    )

    return df, info


# Load Data =======================================================
participants = os.listdir(path)

for participant in participants:
    # participant = "sub-pilot2"
    path_sub = path + participant + "/ses-S001/beh/"

    df, info = load_data(path=path_sub, task="HBC")

    nk.signal_plot(df, subplots=True)
