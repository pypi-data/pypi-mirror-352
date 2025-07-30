import os
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# sys.path.append('./BIC_codes/')
from functions.dFC_funcs import *
from functions.post_analysis_funcs import *

print(" VISUALIZATION IN PROGRESS ... ")

################################# LOAD RESULTS #################################

output_root = "./../../../../RESULTs/methods_implementation/server/methods_implementation/final_figures/"
# output_root = './output/'
save_image = True

# the dictionary that collects all RESULTS
ALL_RESULTS = np.load(output_root + "ALL_RESULTS.npy", allow_pickle="True").item()

################################ common variables #################################

node_networks = ALL_RESULTS["node_networks"]

cluster_colors_dict = {
    "forestgreen": ["SlidingWindow", "Time-Freq"],
    "coral": ["Clustering", "ContinuousHMM", "DiscreteHMM"],
    "crimson": ["CAP", "Windowless"],
}

extra_colors = ["khaki", "orchid", "aquamarine"]

################################# dFC SAMPLES #################################

RESULTS = ALL_RESULTS["dFC_sample"]

plot_sample_dFC(
    D=RESULTS,
    x="samples",
    title="dFC_samples",
    cmap="seismic",
    normalize=False,
    disp_diag=False,
    save_image=save_image,
    output_root=output_root + "dFC_sample/",
    fix_lim=False,
    center_0=True,
    node_networks=node_networks,
    segmented=False,
)

plot_sample_dFC(
    D=RESULTS,
    x="samples_ranked",
    title="dFC_samples_ranked",
    cmap="plasma",
    normalize=False,
    disp_diag=False,
    save_image=save_image,
    output_root=output_root + "dFC_sample/",
    fix_lim=False,
    center_0=False,
    node_networks=node_networks,
    segmented=False,
)

################################# FCS visualization #################################

for measure in ALL_RESULTS["measure_lst"]:

    visualize_FCS(
        measure,
        normalize=True,
        fix_lim=False,
        save_image=save_image,
        output_root=output_root + "FCS/",
    )

################################# RSNs visualization #################################

measure = ALL_RESULTS["measure_lst"][0]

# find ROI count in each RSN
RSNs = np.unique(node_networks)
num_ROIs = {}
for RSN in RSNs:
    num_ROIs[RSN] = np.sum([1 for node in node_networks if node == RSN])

# write to a txt file
folder = f"{output_root}RSNs/"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/ROI_count_in_RSNs.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
for RSN in num_ROIs:
    text_file.write(RSN + " : " + str(num_ROIs[RSN]) + "\n")
text_file.close()

plot_rois(
    node_networks,
    measure.TS_info["nodes_locs"],
    save_image=save_image,
    output_root=f"{output_root}RSNs/",
)

################################# dFC values distributions #################################
dFC_dist_plot = True

if dFC_dist_plot:

    RESULTS = ALL_RESULTS["dFC_values_dist"]

    ############ VISUALIZE ############

    joint_dist_plot(
        data=RESULTS,
        title="dFC values distributions",
        save_image=save_image,
        output_root=output_root + "indiv_prop/",
    )

################################# dFC Similarity #################################

RESULTS = ALL_RESULTS["dFC_similarity_overall"]["spearman"]["session_Rest1_LR"][
    "overall_stat"
]

folder = output_root + "dFC_similarity"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/overall_stat.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
text_file.write("Average similarity of all pairs (E_E) = " + str(RESULTS["E_E"]) + "\n")
text_file.write(
    "Variance of average similarity across pairs (VAR_E) = "
    + str(RESULTS["VAR_E"])
    + " and std = "
    + str(np.sqrt(RESULTS["VAR_E"]))
    + "\n"
)
text_file.write(
    "Average variance of similarity across subjects (E_VAR) = "
    + str(RESULTS["E_VAR"])
    + "\n"
)
text_file.write(
    "ratio of variances (VAR_E / E_VAR) = "
    + str(RESULTS["VAR_E"] / RESULTS["E_VAR"])
    + "\n"
)
text_file.close()

################# whole subject #################
"""
    - corr((all dFC timepoints of one Subj using method_i), (all dFC timepoints of one Subj using method_j)) -> avg(corr) and var(corr)
    - spearman correlation, pearson correlation, Mutual Information (MI), Euclidean Distance
    - dendogram based on avg(corr)
"""

for metric in ALL_RESULTS["dFC_similarity_overall"]:

    RESULTS = ALL_RESULTS["dFC_similarity_overall"][metric]
    filters_lst = [filter for filter in RESULTS]
    keys_lst = [key for key in RESULTS[filters_lst[0]]]

    ############ VISUALIZE ############
    label_dict = {
        "session_Rest1_LR": "session Rest1 LR",
        "session_Rest1_RL": "session Rest1 RL",
        "session_Rest2_LR": "session Rest2 LR",
        "session_Rest2_RL": "session Rest2 RL",
    }
    for key in keys_lst:
        if key == "name_lst" or key == "sim_distribution" or key == "overall_stat":
            continue
        visualize_sim_mat(
            RESULTS,
            mat_key=key,
            title=metric + " " + key,
            name_lst_key="name_lst",
            label_dict=label_dict,
            cmap="viridis",
            save_image=save_image,
            output_root=output_root + "dFC_similarity/" + metric + "/",
        )

    #### similarity values distribution ####
    label_dict = {"sim": "similarity"}
    for filter in ["session_Rest1_LR"]:
        pairwise_cat_plots(
            RESULTS[filter]["sim_distribution"],
            y="sim",
            title=metric + " total similarity distributions " + filter,
            label_dict=label_dict,
            save_image=save_image,
            output_root=output_root + "dFC_similarity/" + metric + "/",
        )

    ############ Hierarchical Clustering ############
    for filter in ["session_Rest1_LR"]:
        dist_mat = corr2distance(RESULTS[filter]["avg_mat"], metric=metric)
        Z = distance2Z(dist_mat, method="ward")

        # find link colors to fix the color of each cluster
        link_cols = find_link_colors(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            cluster_colors_dict=cluster_colors_dict,
            extra_colors=extra_colors,
        )

        dist_mat_dendo(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            link_colors=link_cols,
            plot_threshold=True,
            title="Hierarchical Clustering of Methods " + filter + " using " + metric,
            save_image=save_image,
            output_root=output_root + "dFC_similarity/" + metric + "/",
        )

################# Hierarchical Clstr with Confidence Interval #################
"""
    - plot the most frequent hierclstr structures across subjects
"""
min_freq = 10
Z_lst = ALL_RESULTS["Hierclstr_CI"]
measures_lst = [measure.measure_name for measure in ALL_RESULTS["measure_lst"]]

# cluster Zs to find common structures
Z_clstrs = cluster_Z(Z_lst, num_leaf=len(measures_lst))

num_clstrs = len([key for key in Z_clstrs])
num_clstrs_included = 0
for key in Z_clstrs:
    Z_clstrs[key]["distance_lst"] = np.array(Z_clstrs[key]["distance_lst"])
    if Z_clstrs[key]["freq"] > min_freq:
        num_clstrs_included += 1
        n = Z_clstrs[key]["distance_lst"].shape[0]
        avg_distances = np.mean(Z_clstrs[key]["distance_lst"], axis=0)
        std_distances = np.std(Z_clstrs[key]["distance_lst"], axis=0)

        # reconstruct avg Z
        Z = list()
        for i, tree in enumerate(Z_clstrs[key]["Z"]):
            Z.append([tree[0], tree[1], avg_distances[i], tree[3]])
        Z = np.array(Z)

        # find link colors to fix the color of each cluster
        link_cols = find_link_colors(
            Z=Z,
            labels=measures_lst,
            cluster_colors_dict=cluster_colors_dict,
            extra_colors=extra_colors,
        )

        dist_mat_dendo(
            Z,
            labels=measures_lst,
            link_colors=link_cols,
            plot_threshold=True,
            distances_CI=std_distances,
            title="Hierclstr clstr " + str(key) + "_" + str(n) + "subjects",
            save_image=save_image,
            output_root=output_root + "hierclstr_CI/",
        )

# write to a txt file
folder = output_root + "hierclstr_CI"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/hierclstr.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
text_file.write("Number of structures found across subjects = " + str(num_clstrs) + "\n")
text_file.write("The min number of subjects to be included = " + str(min_freq) + "\n")
text_file.write("Number of structures included = " + str(num_clstrs_included) + "\n")
text_file.close()

################# session ANOVA #################

if "session_ANOVA" in ALL_RESULTS:

    RESULTS = ALL_RESULTS["session_ANOVA"]
    measure_lst = [measure.measure_name for measure in ALL_RESULTS["measure_lst"]]

    data = {
        "day p-values": {
            "p_values": np.nan * np.ones((len(measure_lst), len(measure_lst))),
            "measure_lst": measure_lst,
        },
        "direction p-values": {
            "p_values": np.nan * np.ones((len(measure_lst), len(measure_lst))),
            "measure_lst": measure_lst,
        },
    }

    for i, measure_i in enumerate(RESULTS):
        for j, measure_j in enumerate(RESULTS[measure_i]):
            result = RESULTS[measure_i][measure_j]

            index_i = measure_lst.index(unzip_name(measure_i))
            index_j = measure_lst.index(unzip_name(measure_j))

            data["day p-values"]["p_values"][index_i, index_j] = result["PR(>F)"][0]
            data["day p-values"]["p_values"][index_j, index_i] = result["PR(>F)"][0]
            data["direction p-values"]["p_values"][index_i, index_j] = result["PR(>F)"][1]
            data["direction p-values"]["p_values"][index_j, index_i] = result["PR(>F)"][1]

    ############ VISUALIZE ############

    visualize_sim_mat(
        data,
        mat_key="p_values",
        title="session_ANOVA_test",
        name_lst_key="measure_lst",
        annot=True,
        fmt=2,
        show_diag=False,
        show_sig=True,
        no_color=True,
        save_image=save_image,
        output_root=output_root + "dFC_similarity/",
    )

################# feature-based #################
"""
    - spatial
    - temporal
    - inter-time-correlation
    - inter-connection-correlation
    - dFC-avg
    - dFC-var
"""

for feature2extract in ALL_RESULTS["dFC_similarity_feature_based"]:

    RESULTS = ALL_RESULTS["dFC_similarity_feature_based"][feature2extract]
    filters_lst = [filter for filter in RESULTS]
    keys_lst = [key for key in RESULTS[filters_lst[0]]]

    ############ VISUALIZE ############
    label_dict = {
        "default_values": "session Rest1 LR",
        "session_Rest1_RL": "session Rest1 RL",
        "session_Rest2_LR": "session Rest2 LR",
        "session_Rest2_RL": "session Rest2 RL",
    }
    for key in keys_lst:
        if key == "name_lst":
            continue
        visualize_sim_mat(
            RESULTS,
            mat_key=key,
            title=feature2extract + " " + key,
            name_lst_key="name_lst",
            label_dict=label_dict,
            cmap="viridis",
            save_image=save_image,
            output_root=output_root + "feature_based/" + feature2extract + "/",
        )
    ############ Hierarchical Clustering ############
    for filter in ["default_values"]:
        dist_mat = corr2distance(RESULTS[filter]["avg_mat"], metric="spearman")
        Z = distance2Z(dist_mat, method="ward")

        # find link colors to fix the color of each cluster
        link_cols = find_link_colors(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            cluster_colors_dict=cluster_colors_dict,
            extra_colors=extra_colors,
        )

        dist_mat_dendo(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            link_colors=link_cols,
            plot_threshold=True,
            title="Hierarchical Clustering of Methods "
            + filter
            + " using "
            + feature2extract,
            save_image=save_image,
            output_root=output_root + "feature_based/" + feature2extract + "/",
        )

############ Spatial vs. Temporal Scatter plot ############

scatter_data = ALL_RESULTS["spatial_vs_temporal_similarity"]

############ visualization ############
label_dict = {"spatial": "spatial similarity", "temporal": "temporal similarity"}
scatter_plot(
    data=scatter_data,
    x="temporal",
    y="spatial",
    labels="labels",
    title="spatial similarity vs temporal similarity",
    label_dict=label_dict,
    c=0.3,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/spatialVsTemporal/",
)

################# graph-based #################
"""
    - spatial
    - temporal-avg
    - ECM, shortest_path, degree, clustering_coef
"""

###### spatial #####

for graph_property in ALL_RESULTS["dFC_similarity_graph"]["spatial"]:

    RESULTS = ALL_RESULTS["dFC_similarity_graph"]["spatial"][graph_property]
    filters_lst = [filter for filter in RESULTS]
    keys_lst = [key for key in RESULTS[filters_lst[0]]]

    ############ VISUALIZE ############
    label_dict = {
        "default_values": "session Rest1 LR",
        "session_Rest1_RL": "session Rest1 RL",
        "session_Rest2_LR": "session Rest2 LR",
        "session_Rest2_RL": "session Rest2 RL",
    }
    for key in keys_lst:
        if key == "name_lst":
            continue
        visualize_sim_mat(
            RESULTS,
            mat_key=key,
            title="spatial " + graph_property + " " + key,
            name_lst_key="name_lst",
            label_dict=label_dict,
            cmap="viridis",
            save_image=save_image,
            output_root=output_root + "graph_based/" + graph_property + "/",
        )
    ############ Hierarchical Clustering ############
    for filter in ["default_values"]:
        dist_mat = corr2distance(RESULTS[filter]["avg_mat"], metric="spearman")
        Z = distance2Z(dist_mat, method="ward")

        # find link colors to fix the color of each cluster
        link_cols = find_link_colors(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            cluster_colors_dict=cluster_colors_dict,
            extra_colors=extra_colors,
        )

        dist_mat_dendo(
            Z=Z,
            labels=RESULTS[filter]["name_lst"],
            link_colors=link_cols,
            plot_threshold=True,
            title="Hierarchical Clustering of Methods "
            + filter
            + " using "
            + "spatial "
            + graph_property,
            save_image=save_image,
            output_root=output_root + "graph_based/" + graph_property + "/",
        )

################################# TSNE visualization #################################

"""
    - visualize subjects dFC obtained by different methods in a 2D space
        considering their distances
"""

RESULTS = ALL_RESULTS["TSNE"]
sample_measure_lst = [sample[sample.find("_") + 1 :] for sample in RESULTS["sample_lst"]]

measures_lst = list(set(sample_measure_lst))
measures_lst.sort()
colors_lst = ["black", "green", "orange", "red", "dodgerblue", "grey", "violet"]
color_dict = {}
for i, measure in enumerate(measures_lst):
    color_dict[measure] = colors_lst[i]

# using overall corr
dist_mat = corr2distance(RESULTS["corr"], metric="spearman")

plot_TSNE(
    dist_mat,
    sample_measure_lst,
    color_dict,
    projection="2d",
    title="TSNE overall corr",
    save_image=save_image,
    output_root=output_root + "TSNE/",
)

for n_components in RESULTS["X_red_corr"]:
    dist_mat = corr2distance(RESULTS["X_red_corr"][n_components], metric="spearman")

    plot_TSNE(
        dist_mat,
        sample_measure_lst,
        color_dict,
        projection="2d",
        title="TSNE " + str(n_components),
        save_image=save_image,
        output_root=output_root + "TSNE/",
    )

################################# inter_subject similarity #################################

"""
    - returns correspondence of inter-subject relation between results of dFC
        measures in each session
    - dendogram based on inter-subject similarity
"""

for subj_lvl_feature in ALL_RESULTS["subj_clustring"]:

    RESULTS = ALL_RESULTS["subj_clustring"][subj_lvl_feature]

    ############ VISUALIZE ############
    label_dict = {
        "session_Rest1_LR": "session Rest1 LR",
        "session_Rest1_RL": "session Rest1 RL",
        "session_Rest2_LR": "session Rest2 LR",
        "session_Rest2_RL": "session Rest2 RL",
    }
    for key in RESULTS:
        annot = True
        # set diag values to 0
        for session in RESULTS[key]:
            np.fill_diagonal(RESULTS[key][session]["sim_mat"], 0)
        visualize_sim_mat(
            RESULTS[key],
            mat_key="sim_mat",
            title="inter-subject-corr similarity "
            + key
            + " based on "
            + subj_lvl_feature,
            name_lst_key="name_lst",
            label_dict=label_dict,
            cmap="viridis",
            annot=annot,
            save_image=save_image,
            output_root=output_root + "inter_subject/" + subj_lvl_feature + "/",
        )
    ############ Hierarchical Clustering ############
    for session in RESULTS["across_method"]:
        dist_mat = corr2distance(
            RESULTS["across_method"][session]["sim_mat"], metric="spearman"
        )
        Z = distance2Z(dist_mat, method="ward")

        # find link colors to fix the color of each cluster
        link_cols = find_link_colors(
            Z=Z,
            labels=RESULTS["across_method"][session]["name_lst"],
            cluster_colors_dict=cluster_colors_dict,
            extra_colors=extra_colors,
        )

        dist_mat_dendo(
            Z=Z,
            labels=RESULTS["across_method"][session]["name_lst"],
            link_colors=link_cols,
            plot_threshold=True,
            title="Hierarchical Clustering of Methods "
            + session
            + " using inter-subject similarity based on "
            + subj_lvl_feature,
            save_image=save_image,
            output_root=output_root + "inter_subject/" + subj_lvl_feature + "/",
        )

################################# dFC var #################################

"""
    - avg(variance/fluctuations of dFC in one Subj)
    - rank normed
"""

RESULTS = ALL_RESULTS["dFC_var"]

visualize_conn_mat_dict(
    RESULTS["avg_dFC_var"],
    node_networks=node_networks,
    title="avg dFC var",
    center_0=False,
    fix_lim=False,
    disp_diag=True,
    cmap="plasma",
    normalize=False,
    save_image=save_image,
    output_root=output_root + "dFC_var/",
)

visualize_conn_mat_dict(
    RESULTS["avg_dFC_var"],
    node_networks=node_networks,
    segmented=True,
    title="segmented avg dFC var",
    center_0=False,
    fix_lim=False,
    disp_diag=True,
    cmap="plasma",
    normalize=False,
    save_image=save_image,
    output_root=output_root + "dFC_var/",
)

visualize_conn_mat_dict(
    RESULTS["var_dFC_var"],
    node_networks=node_networks,
    title="var of dFC var",
    center_0=False,
    fix_lim=False,
    disp_diag=True,
    cmap="plasma",
    normalize=False,
    save_image=save_image,
    output_root=output_root + "dFC_var/",
)

################################# dFC avg #################################

"""
    - avg(avg of dFC -static FC- in one Subj)
    - rank normed
"""

RESULTS = ALL_RESULTS["dFC_avg"]

visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    title="dFC avg",
    center_0=False,
    fix_lim=False,
    disp_diag=False,
    cmap="plasma",
    normalize=False,
    save_image=save_image,
    output_root=output_root + "dFC_avg/",
)

visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented dFC avg",
    center_0=False,
    fix_lim=False,
    disp_diag=False,
    cmap="plasma",
    normalize=False,
    save_image=save_image,
    output_root=output_root + "dFC_avg/",
)

################################# Across Func Conn total Correlation #################################

"""
    - spearman_corr((dFConnection(node_i, node_j) timecourse using method m), (dFConnection(node_i, node_j) timecourse using method n))
"""

RESULTS = ALL_RESULTS["across_func_conns"]

############ VISUALIZE ############

visualize_conn_mat_2D_dict(
    RESULTS,
    node_networks=node_networks,
    title="across func conn total spearman corr",
    fix_lim=False,
    disp_diag=False,
    cmap="seismic",
    normalize=False,
    center_0=True,
    save_image=save_image,
    output_root=output_root + "across_func_conn/",
)

visualize_conn_mat_2D_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented across func conn total spearman corr",
    fix_lim=False,
    disp_diag=False,
    cmap="seismic",
    normalize=False,
    center_0=True,
    save_image=save_image,
    output_root=output_root + "across_func_conn/",
)

visualize_conn_mat_2D_dict(
    RESULTS,
    node_networks=node_networks,
    title="across func conn total spearman corr normalized",
    fix_lim=False,
    disp_diag=False,
    cmap="seismic",
    normalize=True,
    center_0=True,
    save_image=save_image,
    output_root=output_root + "across_func_conn/",
)

visualize_conn_mat_2D_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented across func conn total spearman corr normalized",
    fix_lim=False,
    disp_diag=False,
    cmap="seismic",
    normalize=True,
    center_0=True,
    save_image=save_image,
    output_root=output_root + "across_func_conn/",
)

################################# High Variation Regions #################################
"""
    - high variation regions over methods and over time.
"""

RESULTS = ALL_RESULTS["var_across_func_conns"]
RATIO = ALL_RESULTS["var_across_func_conns_ratio"]
scatter_data = ALL_RESULTS["var_method_vs_time_across_func_conns_scatter"]

############ method var / time var ############

ratio = list()
ratio_std = list()
for i, sample in enumerate(scatter_data["var_method"]):
    ratio.append(scatter_data["var_method"][i] / scatter_data["var_time"][i])
    ratio_std.append(
        np.sqrt(scatter_data["var_method"][i]) / np.sqrt(scatter_data["var_time"][i])
    )
ratio = np.mean(np.array(ratio))
ratio_std = np.mean(np.array(ratio_std))
avg_var_time = np.mean(scatter_data["var_time"])
avg_var_method = np.mean(scatter_data["var_method"])

# write to a txt file
folder = output_root + "variation/timeVsMethod"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/var_ratio.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
text_file.write("Average of var method / var time ratio = " + str(ratio) + "\n")
text_file.write("Average of std method / std time ratio = " + str(ratio_std) + "\n")
text_file.write("Average var method = " + str(avg_var_method) + "\n")
text_file.write("Average var time = " + str(avg_var_time) + "\n")
text_file.write(
    "Ratio of avg var method / avg var time = "
    + str(avg_var_method / avg_var_time)
    + "\n"
)
text_file.close()

############ VISUALIZE ############

label_dict = {"var_method": "variation over method", "var_time": "variation over time"}
scatter_plot(
    data=scatter_data,
    x="var_time",
    y="var_method",
    title="var method vs time across func conns",
    label_dict=label_dict,
    hist=True,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

label_dict = {
    "var across method / time - 1": "var over method / time - 1",
}
visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=False,
    title="ratio of high variation regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=True,
    title="segmented ratio of high variation regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

label_dict = {
    "var_over_method": "variation over method",
    "var_over_time": "variation over time",
}

visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    title="variation across regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

# func conn segmented
visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented high variation regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

RESULTS = ALL_RESULTS["high_var_func_conns"]

label_dict = {
    "var_over_method": "variation over method",
    "var_over_time": "variation over time",
}
visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    title="high variation regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

################################# Variation Value Comparison #################################
"""
    - compare variation over methods with variation over time.
"""

RESULTS = ALL_RESULTS["var_comparison"]
scatter_data_across_func_conn = ALL_RESULTS[
    "var_method_vs_time_method_pairs_across_func_conns"
]
scatter_data = ALL_RESULTS["var_method_vs_time_method_pairs"]

############ VISUALIZE ############

visualize_sim_mat(
    RESULTS,
    mat_key="sim_mat",
    title="variation in different dimensions",
    name_lst_key="name_lst",
    cmap="viridis",
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

label_dict = {"var_method": "variation over methods", "var_time": "variation over time"}
pairwise_scatter_plots(
    data=scatter_data_across_func_conn,
    x="var_time",
    y="var_method",
    title="var method vs time across func conns across methods pairs",
    label_dict=label_dict,
    hist=True,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

label_dict = {"var_method": "variation over method", "var_time": "variation over time"}
scatter_plot(
    data=scatter_data,
    x="var_time",
    y="var_method",
    labels="labels",
    title="var method vs time",
    label_dict=label_dict,
    c=0.5,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/timeVsMethod/",
)

################################# Var method vs. Time Clstrwise #################################
"""
    - compute var over method and time within each group of methods
"""
scatter_data = ALL_RESULTS["var_method_vs_time_clstrwise"]["scatter_data"]
clstrs_dict = ALL_RESULTS["var_method_vs_time_clstrwise"]["clstrs_dict"]

# write to a txt file
folder = output_root + "variation"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/var_clstrwise_ratio.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")

for clstr in scatter_data:

    ratio = list()
    for i, sample in enumerate(scatter_data[clstr]["var_method"]):
        ratio.append(
            scatter_data[clstr]["var_method"][i] / scatter_data[clstr]["var_time"][i]
        )

    ratio = np.mean(np.array(ratio))
    avg_var_time = np.mean(scatter_data[clstr]["var_time"])
    avg_var_method = np.mean(scatter_data[clstr]["var_method"])

    text_file.write(clstr + "\n")
    text_file.write(" ".join(clstrs_dict[clstr]) + "\n")
    text_file.write("Average of var method / var time ratio = " + str(ratio) + "\n")
    text_file.write("Average var method = " + str(avg_var_method) + "\n")
    text_file.write("Average var time = " + str(avg_var_time) + "\n")
    text_file.write(
        "Ratio of avg var method / avg var time = "
        + str(avg_var_method / avg_var_time)
        + "\n"
    )

    label_dict = {
        "var_method": "variation over method",
        "var_time": "variation over time",
    }
    scatter_plot(
        data=scatter_data[clstr],
        x="var_time",
        y="var_method",
        title="var method vs time clusterwise across func conns " + clstr,
        label_dict=label_dict,
        hist=True,
        equal_axis_lim=True,
        show_x_equal_y=True,
        save_image=save_image,
        output_root=output_root + "variation/timeVsMethod/",
    )
text_file.close()

################################# Inter-subject Variation #################################
"""
    - compute var over method and subject across all func conns
"""

RESULTS = ALL_RESULTS["inter-subj_var_across_func_conns"]
RATIO = ALL_RESULTS["inter-subj_var_across_func_conns_ratio"]
scatter_data = ALL_RESULTS["var_method_vs_subj_across_func_conns_scatter"]

############ method var / subject var ############

ratio = list()
ratio_std = list()
for i, sample in enumerate(scatter_data["var_method"]):
    ratio.append(scatter_data["var_method"][i] / scatter_data["var_subj"][i])
    ratio_std.append(
        np.sqrt(scatter_data["var_method"][i]) / np.sqrt(scatter_data["var_subj"][i])
    )
ratio = np.mean(np.array(ratio))
ratio_std = np.mean(np.array(ratio_std))
avg_var_subj = np.mean(scatter_data["var_subj"])
avg_var_method = np.mean(scatter_data["var_method"])

# write to a txt file
folder = output_root + "variation/subjVsMethod"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/subj_var_ratio.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
text_file.write("Average of var method / var subj ratio = " + str(ratio) + "\n")
text_file.write("Average of std method / std subj ratio = " + str(ratio_std) + "\n")
text_file.write("Average var method = " + str(avg_var_method) + "\n")
text_file.write("Average var subj = " + str(avg_var_subj) + "\n")
text_file.write(
    "Ratio of avg var method / avg var subj = "
    + str(avg_var_method / avg_var_subj)
    + "\n"
)
text_file.close()

############ VISUALIZE ############

label_dict = {"var_method": "variation over method", "var_subj": "variation over subject"}
scatter_plot(
    data=scatter_data,
    x="var_subj",
    y="var_method",
    title="var method vs subj across func conns",
    label_dict=label_dict,
    hist=True,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/subjVsMethod/",
)

label_dict = {
    "var across method / subj - 1": "var over method / subj - 1",
}
visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=False,
    title="ratio of method subj var regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/subjVsMethod/",
)

visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=True,
    title="segmented ratio of method subj var regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/subjVsMethod/",
)

label_dict = {
    "var_over_method": "variation over method",
    "var_over_subj": "variation over subject",
}

visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    title="inter-subj variation across regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/subjVsMethod/",
)

# func conn segmented
visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented inter-subj variation across regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/subjVsMethod/",
)

################################# Overall Variability #################################
"""
    - compute var over method and overall across all func conns
"""

RESULTS = ALL_RESULTS["var_all_across_func_conns"]
RATIO = ALL_RESULTS["var_all_across_func_conns_ratio"]
scatter_data = ALL_RESULTS["var_method_vs_all_across_func_conns_scatter"]

############ method var / subject var ############

ratio = list()
ratio_std = list()
for i, sample in enumerate(scatter_data["var_method"]):
    ratio.append(scatter_data["var_method"][i] / scatter_data["var_all"][i])
    ratio_std.append(
        np.sqrt(scatter_data["var_method"][i]) / np.sqrt(scatter_data["var_all"][i])
    )
ratio = np.mean(np.array(ratio))
ratio_std = np.mean(np.array(ratio_std))
avg_var_all = np.mean(scatter_data["var_all"])
avg_var_method = np.mean(scatter_data["var_method"])

# write to a txt file
folder = output_root + "variation/allVsMethod"
if not os.path.exists(folder):
    os.makedirs(folder)
filename = Path(folder + "/all_var_ratio.txt")
filename.touch(exist_ok=True)
text_file = open(filename, "wt")
text_file.write("Average of var method / var all ratio = " + str(ratio) + "\n")
text_file.write("Average of std method / std all ratio = " + str(ratio_std) + "\n")
text_file.write("Average var method = " + str(avg_var_method) + "\n")
text_file.write("Average var subj = " + str(avg_var_all) + "\n")
text_file.write(
    "Ratio of avg var method / avg var subj = " + str(avg_var_method / avg_var_all) + "\n"
)
text_file.close()

############ VISUALIZE ############

label_dict = {"var_method": "variation over method", "var_all": "variation over all"}
scatter_plot(
    data=scatter_data,
    x="var_all",
    y="var_method",
    title="var method vs all across func conns",
    label_dict=label_dict,
    hist=True,
    equal_axis_lim=True,
    show_x_equal_y=True,
    save_image=save_image,
    output_root=output_root + "variation/allVsMethod/",
)

label_dict = {
    "var across method / all - 1": "var over method / all - 1",
}
visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=False,
    title="ratio of method all var regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/allVsMethod/",
)

visualize_conn_mat_dict(
    RATIO,
    node_networks=node_networks,
    segmented=True,
    title="segmented ratio of method all var regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=False,
    cmap="seismic",
    center_0=True,
    save_image=save_image,
    output_root=output_root + "variation/allVsMethod/",
)

label_dict = {
    "var_over_method": "variation over method",
    "var_over_all": "variation over all",
}

visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    title="all variation across regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/allVsMethod/",
)

# func conn segmented
visualize_conn_mat_dict(
    RESULTS,
    node_networks=node_networks,
    segmented=True,
    title="segmented all variation across regions",
    fix_lim=False,
    label_dict=label_dict,
    disp_diag=True,
    cmap="plasma",
    center_0=False,
    save_image=save_image,
    output_root=output_root + "variation/allVsMethod/",
)

################################# Randomization Tests #################################

metric = "spearman"

"""
find the similarity between the dFC obtained by each method
and a dFC which is a constant sequence of mean of all methods dFC
"""

########### Similarity with static FC ###########

RESULTS = ALL_RESULTS["randomization"]["sim_with_static_FC"]

############ VISUALIZE ############
label_dict = {"sim": "similarity", "dFC_method": "dFC assessment method"}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y="sim",
    kind="box",
    title="similarity with constant static FC",
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "randomization/",
)

########### Shuffled ###########

"""
find the similarity between the dFC obtained by each method
but with randomized temporal/spatial/all order
"""

RESULTS = ALL_RESULTS["randomization"]["shuffled"]["similarity_dict"]
modes_lst = ALL_RESULTS["randomization"]["shuffled"]["modes_lst"]

############ VISUALIZE ############
label_dict = {
    "all_shuffle_sim": "similarity",
    "spatial_shuffle_sim": "similarity",
    "temporal_shuffle_sim": "similarity",
}
for mode in modes_lst:
    key = mode + "_shuffle_sim"
    pairwise_cat_plots(
        RESULTS,
        y=key,
        z="actual_sim",
        title=mode + " shuffled similarity",
        label_dict=label_dict,
        save_image=save_image,
        output_root=output_root + "randomization/",
    )

########### Random state time course ###########

"""
find the similarity between dFC matrices created using
a random state time course but real FC patterns obtained
by each method; for SW and TF all FC patterns of each
subject are used
"""

RESULTS = ALL_RESULTS["randomization"]["random_state_TC"]

############ VISUALIZE ############
label_dict = {
    "sim": "similarity",
}
pairwise_cat_plots(
    RESULTS,
    y="sim",
    z="actual_sim",
    title="random state time course dFC",
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "randomization/",
)

################################# inter-state spatial similarity #################################

key_name = "inter-state_spatial_sim"
RESULTS = ALL_RESULTS[key_name]

############ VISUALIZE ############
label_dict = {
    "sim": "inter-state spatial similarity",
    "dFC_method": "dFC assessment method",
}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y="sim",
    kind="box",
    scale_dist=False,
    title=key_name,
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "indiv_prop/",
)

################################# SIMILARITY OF ADJACENT TIME POINTS #################################

key_name = "similarity of adjacent time points"
RESULTS = ALL_RESULTS["adjacent_time_points"]

############ VISUALIZE ############
label_dict = {"dFC_method": "dFC assessment method"}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y=key_name,
    kind="box",
    title=key_name,
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "indiv_prop/",
)

################################# TRANSITION FREQUENCY #################################
"""
 - plot normalized transition frequency
"""

key_name = "trans_freq"
RESULTS = ALL_RESULTS["transition_freq"]

############ VISUALIZE ############
label_dict = {"trans_freq": "transition frequency", "dFC_method": "dFC assessment method"}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y=key_name,
    kind="box",
    title=key_name,
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "indiv_prop/",
)

################################# DWELL TIME #################################
"""
 - plot normalized (not downsampled) dwell times
 - the dwell times are not averaged within each subj, they include all individual
 dwells
"""

key_name = "dwell_time"
RESULTS = ALL_RESULTS["dwell_time"]

############ VISUALIZE ############
label_dict = {"dwell_time": "dwell time", "dFC_method": "dFC assessment method"}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y=key_name,
    kind="box",
    scale_dist=True,
    title=key_name,
    label_dict=label_dict,
    y_lim=(0, 0.2),
    save_image=save_image,
    output_root=output_root + "indiv_prop/",
)

################################# TIME RECORD #################################

RESULTS = ALL_RESULTS["time_record"]
filter = "session_Rest1_LR"

############ VISUALIZE ############
label_dict = {
    "FCS_fit_time (s)": "FCS fitting time (s)",
    "dFC_assess_time (s)": "dFC assessing time (s)",
    "dFC_method": "dFC assessment method",
}
cat_plot(
    data=RESULTS,
    x="dFC_method",
    y="dFC_assess_time (s)",
    kind="bar",
    log=True,
    title="dFC assess time record of " + filter,
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "time/",
)

cat_plot(
    data=RESULTS,
    x="dFC_method",
    y="FCS_fit_time (s)",
    kind="bar",
    log=True,
    title="FCS fit time record of " + filter,
    label_dict=label_dict,
    save_image=save_image,
    output_root=output_root + "time/",
)

if not save_image:
    plt.show()
#################################################################################
