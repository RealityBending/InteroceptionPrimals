import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
import tslearn.clustering
import tslearn.neighbors
import tslearn.preprocessing

df = pd.read_csv("../data/data_hep.csv")

data = {}
for c in ["RestingState", "HCT"]:
    for ch in ["AF7", "AF8"]:
        data[c + "_" + ch] = df[(df["Condition"] == c)].pivot(
            index="time", columns="participant_id", values=ch
        )
        data[c + "_" + ch] = nk.standardize(data[c + "_" + ch])

X1 = tslearn.utils.to_time_series_dataset(data["RestingState_AF7"].T)
X2 = tslearn.utils.to_time_series_dataset(data["RestingState_AF8"].T)
# X1 = tslearn.preprocessing.TimeSeriesScalerMeanVariance().fit_transform(X1)


# How many clusters? ========================================
def silhouette(X, n_clusters=2):
    m = tslearn.clustering.KShape(n_clusters=n_clusters).fit(X)
    return tslearn.clustering.silhouette_score(X, m.labels_, metric="euclidean")


plt.plot(range(2, 7), [silhouette(X1, n_clusters=i) for i in range(2, 7)], label="AF7")
plt.plot(range(2, 7), [silhouette(X1, n_clusters=i) for i in range(2, 7)], label="AF8")
plt.legend()

# Clustering ================================================
# Manual clusters (based on observation)
manual_clusters = [1, 5, 10, 13, 15, 17, 18, 20]
numbers = [int(s.split("-")[1]) for s in data["RestingState_AF7"].columns]
manual_clusters = np.array([0 if n in manual_clusters else 1 for n in numbers])

# Clustering
models = {}
for metric in ["euclidean", "dtw", "softdtw", "kshape"]:
    if metric == "kshape":
        ks = tslearn.clustering.KShape(n_clusters=2)
        models[metric] = ks.fit(X2)
    else:
        km = tslearn.clustering.TimeSeriesKMeans(n_clusters=2, metric=metric)
        models[metric] = km.fit(X2)


# Visualize
def plot_clusters(data, clusters, ax=None):
    if isinstance(clusters, np.ndarray):
        model = None
    else:
        model = clusters
        clusters = model.labels_
    colors = {0: "red", 1: "black"}
    for ppt, cluster in enumerate(clusters):
        ax.plot(
            data.index,
            data.values[:, ppt],
            color=colors[cluster],
            alpha=1 / 6,
            linewidth=0.5,
        )
    for c in range(2):
        ax.plot(
            data.index,
            data.iloc[:, clusters == c].mean(axis=1),
            color=colors[c],
            label=c,
            linewidth=1,
        )
        if model is not None:
            ax.plot(
                data.index,
                model.cluster_centers_[c].ravel(),
                color=colors[c],
                linewidth=2,
                linestyle="dashed",
            )


fig, ax = plt.subplots(ncols=2, nrows=5, figsize=(10, 12))
for i, ch in enumerate(["AF7", "AF8"]):
    plot_clusters(data["RestingState_" + ch], manual_clusters, ax=ax[0, i])
    ax[0, i].set_title(f"Manual clustering ({ch})")
    for j, metric in enumerate(["euclidean", "dtw", "softdtw", "kshape"]):
        plot_clusters(data["RestingState_" + ch], models[metric], ax=ax[j + 1, i])
        ax[j + 1, i].set_title(f"{metric} clustering ({ch})")
plt.legend()

# Save clusters
clusters = models["euclidean"].labels_
df["Cluster"] = [
    "N100" if s in data["RestingState_AF7"].columns[clusters == 0] else "P200"
    for s in df["participant_id"]
]
df.to_csv("../data/data_hep.csv", index=False)
