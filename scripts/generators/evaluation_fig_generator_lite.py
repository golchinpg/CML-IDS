import matplotlib.pyplot as plt
import matplotlib.cm as cm

import pandas as pd
import numpy as np
import math


class EvaluationFigureGeneratorLite():
    """Plot evaluation figures.

    Attributes:
        final_file_path_list: list of .csv files
            List of paths of evaluation files saved in .csv format.
        index_file_path_list: two dimentional list of .csv files
            Lists of paths of evalution files for each day of each evaluation time.
        fig_save_base_path_list:
            List of base paths to save figures.
    """

    _METRIC_COLOR_WEIGHT = 0.8
    _BASELINE_COLOR_WEIGHT = 0.4
    _ALPHA_VAL = 0.3

    _COLOR_DICT = {
        "tuesday_color": "tab:blue",
        "wednesday_color": "tab:orange",
        "thursday_color": "tab:red",
        "friday_color": "tab:green",

        "tuesday_baseline_color": cm.Blues(_BASELINE_COLOR_WEIGHT),
        "wednesday_baseline_color": cm.Oranges(_BASELINE_COLOR_WEIGHT),
        "thursday_baseline_color": cm.Reds(_BASELINE_COLOR_WEIGHT),
        "friday_baseline_color": cm.Greens(_BASELINE_COLOR_WEIGHT),

        "f1_color": "tab:blue",
        "pre_color": "tab:orange",
        "re_color": "tab:green",

        "f1_baseline_color": cm.Blues(_BASELINE_COLOR_WEIGHT),
        "pre_baseline_color": cm.Oranges(_BASELINE_COLOR_WEIGHT),
        "re_baseline_color": cm.Greens(_BASELINE_COLOR_WEIGHT),

        "fn_color": "tab:blue",
        "fp_color": "tab:orange",
        "tn_color": "tab:green",
        "tp_color": "tab:red",

        "time_p4_color": "tab:blue",
        "time_controller_color": "tab:orange",

        "baseline_color": "grey",
        "sum_color": "tab:purple"
    }

    _GINI_THRESHOLD_LIST = [0.1, 0.2, 0.3, 0.4]

    def __init__(self, final_file_path_list, index_file_path_list, fig_save_base_path, day_list) -> None:
        self.fig_save_base_path = fig_save_base_path
        self.dataset_day_list = day_list
        self.df_final_list = []
        self.df_index_list = []
        self.fig_dpi = 300
        factor = 0.67
        self.figsize_single = (8*factor, 5.5*factor)
        self.fontsize_label = 13

        self.fontsize_title_subplot = 30
        self.fontsize_label_subplot = 25
        self.fontsize_legend_subplot = 25
        self.fontsize_ticks_subplot = 20
        self.fontsize_text_subplot = 19
        # initialize the colors
        self._load_file(final_file_path_list, index_file_path_list)

    def _load_file(self, final_file_path_list, index_file_path_list):
        """Load the dataset of evaluation results of each day
        """
        for i, day in enumerate(self.dataset_day_list):
            df_final_tmp = pd.read_csv(final_file_path_list[i])
            df_index_tmp = pd.read_csv(index_file_path_list[i])
            self.df_final_list.append(df_final_tmp)
            self.df_index_list.append(df_index_tmp)

    def show_file(self):
        print(self.df)

    def show_column(self, column_name):
        print(self.df[column_name])

    def plot_gini_to_macro_avg_sum(self):
        """Plot macro-average values for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.

        Args:
        """

        metrics = ["macro_avg_pre_sum",
                   "macro_avg_pre_sum_wo_controller",
                   "macro_avg_re_sum",
                   "macro_avg_re_sum_wo_controller",
                   "macro_avg_f1_sum",
                   "macro_avg_f1_sum_wo_controller"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini["macro_avg_pre_sum"].tolist()
                re_tmp = df_index_gini["macro_avg_re_sum"].tolist()
                f1_tmp = df_index_gini["macro_avg_f1_sum"].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))

            # convert to numpy array
            pre_avg_arr = np.array(pre_avg_list)
            re_avg_arr = np.array(re_avg_list)
            f1_avg_arr = np.array(f1_avg_list)
            pre_std_arr = np.array(pre_std_list)
            re_std_arr = np.array(re_std_list)
            f1_std_arr = np.array(f1_std_list)

            # print(f"{day} pre avg: {pre_avg_arr}")
            # print(f"{day} rre avg: {re_avg_arr}")
            # print(f"{day} f1 avg: {f1_avg_arr}")
            # print(f"{day} pre std: {pre_std_arr}")
            # print(f"{day} re std: {re_std_arr}")
            # print(f"{day} f1 std: {f1_std_arr}")

            # get the baseline value list
            gini_threshold_count = len(self._GINI_THRESHOLD_LIST)
            pre_baseline_list = [df_index["macro_avg_pre_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count
            re_baseline_list = [df_index["macro_avg_re_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count
            f1_baseline_list = [df_index["macro_avg_f1_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count

            ############################## plot ##############################
            fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
            fig.tight_layout()
            plt.subplots_adjust(wspace=0.2)

            # plot the macro average
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_avg_arr, linestyle='-',
                        marker='o', color=self._COLOR_DICT["f1_color"], label="F1 Score")
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_avg_arr, linestyle='-',
                        marker='o', color=self._COLOR_DICT["pre_color"], label="Precision")
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_avg_arr, linestyle='-',
                        marker='o', color=self._COLOR_DICT["re_color"], label="Recall")

            # plot the deviation
            axs[0].fill_between(self._GINI_THRESHOLD_LIST, f1_avg_arr - f1_std_arr, f1_avg_arr +
                                f1_std_arr, color=self._COLOR_DICT["f1_color"], alpha=self._ALPHA_VAL)
            axs[1].fill_between(self._GINI_THRESHOLD_LIST, pre_avg_arr - pre_std_arr, pre_avg_arr +
                                pre_std_arr, color=self._COLOR_DICT["pre_color"], alpha=self._ALPHA_VAL)
            axs[2].fill_between(self._GINI_THRESHOLD_LIST, re_avg_arr - re_std_arr, re_avg_arr +
                                re_std_arr, color=self._COLOR_DICT["re_color"], alpha=self._ALPHA_VAL)

            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_baseline_list, linestyle='-',
                        color=self._COLOR_DICT["f1_baseline_color"], label="Baseline F1 Score")
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_baseline_list, linestyle='-',
                        color=self._COLOR_DICT["pre_baseline_color"], label="Baseline Precision")
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_baseline_list, linestyle='-',
                        color=self._COLOR_DICT["re_baseline_color"], label="Baseline Recall")

            # set the ylim to the range
            ylim_min = 0
            ylim_max = 1.1
            axs[0].set_ylim([ylim_min, ylim_max])
            axs[1].set_ylim([ylim_min, ylim_max])
            axs[2].set_ylim([ylim_min, ylim_max])

            axs[0].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
            axs[1].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
            axs[2].set(xlabel="Gini Threshold", ylabel="Macro Average Value")

            axs[0].legend()
            axs[1].legend()
            axs[2].legend()

            plt.show()

            # save figure
            fig_name = f"{day}_gini_threshold_to_macro_avg_line.png"
            fig_path = self.fig_save_base_path + \
                f"/{day}/figs_lite/" + fig_name
            # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_macro_avg_day_sum(self, ylim_arr):
        """Plot macro-average values for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.  One subfigure contains the results of all of the days.

        Args:
            ylim_arr: array like data with 2 values
                The range of y axis
        """

        metrics = ["macro_avg_pre_sum",
                   "macro_avg_pre_sum_wo_controller",
                   "macro_avg_re_sum",
                   "macro_avg_re_sum_wo_controller",
                   "macro_avg_f1_sum",
                   "macro_avg_f1_sum_wo_controller"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}

        # baseline of pre, re and f1 for each day
        pre_baseline_day_dict = {}
        re_baseline_day_dict = {}
        f1_baseline_day_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini["macro_avg_pre_sum"].tolist()
                re_tmp = df_index_gini["macro_avg_re_sum"].tolist()
                f1_tmp = df_index_gini["macro_avg_f1_sum"].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))

            # get the baseline value list
            gini_threshold_count = len(self._GINI_THRESHOLD_LIST)
            pre_baseline_list = [df_index["macro_avg_pre_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count
            re_baseline_list = [df_index["macro_avg_re_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count
            f1_baseline_list = [df_index["macro_avg_f1_sum_wo_controller"].mean(
                axis=0)] * gini_threshold_count

            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_day_dict[day] = pre_baseline_list
            re_baseline_day_dict[day] = re_baseline_list
            f1_baseline_day_dict[day] = f1_baseline_list

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            15, 5), sharey=True, sharex=True)
        fig.tight_layout()

        marker_list = ['o', '^', 's']
        for i, day in enumerate(self.dataset_day_list):
            label_pre_tmp = day.capitalize() + " Precision"
            label_re_tmp = day.capitalize() + " Recall"
            label_f1_tmp = day.capitalize() + " F1 Score"
            label_pre_baseline_tmp = day.capitalize() + " Precision Baseline"
            label_re_baseline_tmp = day.capitalize() + " Recall Baseline"
            label_f1_baseline_tmp = day.capitalize() + " F1 Score Baseline"
            color_tmp = self._COLOR_DICT[day + "_color"]
            color_baseline_tmp = self._COLOR_DICT[day + "_baseline_color"]
            # plot f1 score
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_f1_tmp)
            axs[0].fill_between(self._GINI_THRESHOLD_LIST, f1_avg_day_dict[day] - f1_std_day_dict[day],
                                f1_avg_day_dict[day] + f1_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_f1_baseline_tmp)

            # plot precision
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_pre_tmp)
            axs[1].fill_between(self._GINI_THRESHOLD_LIST, pre_avg_day_dict[day] - pre_std_day_dict[day],
                                pre_avg_day_dict[day] + pre_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_pre_baseline_tmp)

            # plot recall
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_re_tmp)
            axs[2].fill_between(self._GINI_THRESHOLD_LIST, re_avg_day_dict[day] - re_std_day_dict[day],
                                re_avg_day_dict[day] + re_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_re_baseline_tmp)

        axs[0].set_ylim(ylim_arr)
        axs[0].set_xticks(self._GINI_THRESHOLD_LIST)
        axs[0].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
        axs[1].set(xlabel="Gini Threshold")
        axs[2].set(xlabel="Gini Threshold")

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_line.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_macro_avg_day_sum_bar(self, ylim_arr):
        """Plot macro-average values for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller. Bar plot

        Args:
            ylim_arr: array like data with 2 values
                The range of y axis
        """

        metrics = ["macro_avg_pre_sum",
                   "macro_avg_pre_sum_wo_controller",
                   "macro_avg_re_sum",
                   "macro_avg_re_sum_wo_controller",
                   "macro_avg_f1_sum",
                   "macro_avg_f1_sum_wo_controller"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}
        pre_baseline_avg_day_dict = {}
        re_baseline_avg_day_dict = {}
        f1_baseline_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}
        pre_baseline_std_day_dict = {}
        re_baseline_std_day_dict = {}
        f1_baseline_std_day_dict = {}

        # baseline of pre, re and f1 for each day

        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini["macro_avg_pre_sum"].tolist()
                re_tmp = df_index_gini["macro_avg_re_sum"].tolist()
                f1_tmp = df_index_gini["macro_avg_f1_sum"].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))

            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_avg_day_dict[day] = np.mean(
                df_index["macro_avg_pre_sum_wo_controller"].tolist())
            re_baseline_avg_day_dict[day] = np.mean(
                df_index["macro_avg_re_sum_wo_controller"].tolist())
            f1_baseline_avg_day_dict[day] = np.mean(
                df_index["macro_avg_f1_sum_wo_controller"].tolist())
            pre_baseline_std_day_dict[day] = np.std(
                df_index["macro_avg_pre_sum_wo_controller"].tolist())
            re_baseline_std_day_dict[day] = np.std(
                df_index["macro_avg_re_sum_wo_controller"].tolist())
            f1_baseline_std_day_dict[day] = np.std(
                df_index["macro_avg_f1_sum_wo_controller"].tolist())

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            15, 5), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.15

        # Set position of bars on x-axis
        r1 = np.arange(3)
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]

        r_list = [r1, r2, r3, r4, r5]

        for i, day in enumerate(self.dataset_day_list):
            # plot one subfigure for one day
            for j in range(len(self._GINI_THRESHOLD_LIST) + 1):
                # exact the values for each gini threshold or baseline
                avg_values_to_gini_list = []
                std_values_to_gini_list = []
                if j < 4:
                    # avg
                    avg_values_to_gini_list.append(f1_avg_day_dict[day][j])
                    avg_values_to_gini_list.append(pre_avg_day_dict[day][j])
                    avg_values_to_gini_list.append(re_avg_day_dict[day][j])
                    # std
                    std_values_to_gini_list.append(f1_std_day_dict[day][j])
                    std_values_to_gini_list.append(pre_std_day_dict[day][j])
                    std_values_to_gini_list.append(re_std_day_dict[day][j])

                    label_name = f"Model Confidence Threshold = 0.{j + 1}"
                else:
                    # append baseline value
                    # avg
                    avg_values_to_gini_list.append(
                        f1_baseline_avg_day_dict[day])
                    avg_values_to_gini_list.append(
                        pre_baseline_avg_day_dict[day])
                    avg_values_to_gini_list.append(
                        re_baseline_avg_day_dict[day])
                    # std
                    std_values_to_gini_list.append(
                        f1_baseline_std_day_dict[day])
                    std_values_to_gini_list.append(
                        pre_baseline_std_day_dict[day])
                    std_values_to_gini_list.append(
                        re_baseline_std_day_dict[day])

                    label_name = "Baseline"

                # x axis postiones in one tick. for gini thresholdes and baseline
                axs[i].bar(r_list[j], avg_values_to_gini_list,
                           width=barWidth, label=label_name)
                axs[i].errorbar(r_list[j], avg_values_to_gini_list,
                                yerr=std_values_to_gini_list, fmt='none', ecolor='black', capsize=3)

                # add number on top of bar for gini 0.3 and baseline
                if j in [2, 4]:
                    for m, val in enumerate(avg_values_to_gini_list):
                        axs[i].text(r_list[j][m] - barWidth/2, avg_values_to_gini_list[m] +
                                    0.005, format(avg_values_to_gini_list[m], ".3f"))

            axs[i].set_xlabel("Macro Average Metric")
            axs[i].set_ylim(ylim_arr)
            axs[i].legend(loc="lower left")

        axs[0].set_xticks(r3, ["F1 Score", "Precision", "Recall"])
        axs[0].set_ylabel("Macro Average Value")

        # set titles for each subplot
        axs[0].set_title("(A) Brute Force")
        axs[1].set_title("(B) DoS/DDoS")
        axs[2].set_title("(C) Botnet")

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_macro_avg_ensemble_bar(self, ylim_arr):
        """Plot macro-average values for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller. Bar plot. Ensemble result including all days datasest

        Args:
            ylim_arr: array like data with 2 values
                The range of y axis
        """

        metrics = ["fn_sum",
                   "fp_sum",
                   "tn_sum",
                   "tp_sum",
                   "fn_sum_wo_controller",
                   "fp_sum_wo_controller",
                   "tn_sum_wo_controller",
                   "tp_sum_wo_controller"]
        # columns should be extracted from indexed file of each dataset
        columns = ["evaluation_index", "gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # save the avg and std of all flow entries for each gini threshold
        pre_avg_list = []
        re_avg_list = []
        f1_avg_list = []

        pre_std_list = []
        re_std_list = []
        f1_std_list = []

        # concatenate datasets for all days
        df_concat = pd.concat(self.df_index_list)
        # refine the concatenated dataset
        df_refined = df_concat[columns]

        # lists for baseline pre, re and f1 for each gini threshold
        pre_baseline_list = []
        re_baseline_list = []
        f1_baseline_list = []
        # compute the precision, recall and f1 for each gini threshold
        for gini_threshold_val in self._GINI_THRESHOLD_LIST:
            df_gini = df_refined[df_refined["gini_threshold"]
                                 == gini_threshold_val]
            # lists for pre, re and f1 for each gini threshold
            pre_list = []
            re_list = []
            f1_list = []

            for i in range(3):
                # get the sum value of a specific gini threshold and evaluation index
                df_sum = df_gini[df_gini["evaluation_index"]
                                 == (i+1)][metrics].sum(axis=0)

                attack_pre_tmp = df_sum["tp_sum"] / \
                    (df_sum["tp_sum"] + df_sum["fp_sum"])
                attack_re_tmp = df_sum["tp_sum"] / \
                    (df_sum["tp_sum"] + df_sum["fn_sum"])
                attack_f1_tmp = (2 * attack_pre_tmp * attack_re_tmp) / \
                    (attack_pre_tmp + attack_re_tmp)

                attack_pre_baseline_tmp = df_sum["tp_sum_wo_controller"] / (
                    df_sum["tp_sum_wo_controller"] + df_sum["fp_sum_wo_controller"])
                attack_re_baseline_tmp = df_sum["tp_sum_wo_controller"] / (
                    df_sum["tp_sum_wo_controller"] + df_sum["fn_sum_wo_controller"])
                attack_f1_baseline_tmp = (
                    2 * attack_pre_baseline_tmp * attack_re_baseline_tmp) / (attack_pre_baseline_tmp + attack_re_baseline_tmp)

                benign_fn_df_sum = df_sum["fp_sum"]
                benign_fp_df_sum = df_sum["fn_sum"]
                benign_tn_df_sum = df_sum["tp_sum"]
                benign_tp_df_sum = df_sum["tn_sum"]

                benign_fn_df_sum_wo_controller = df_sum["fp_sum_wo_controller"]
                benign_fp_df_sum_wo_controller = df_sum["fn_sum_wo_controller"]
                benign_tn_df_sum_wo_controller = df_sum["tp_sum_wo_controller"]
                benign_tp_df_sum_wo_controller = df_sum["tn_sum_wo_controller"]

                benign_pre_tmp = benign_tp_df_sum / \
                    (benign_tp_df_sum + benign_fp_df_sum)
                benign_re_tmp = benign_tp_df_sum / \
                    (benign_tp_df_sum + benign_fn_df_sum)
                benign_f1_tmp = (2 * benign_pre_tmp * benign_re_tmp) / \
                    (benign_pre_tmp + benign_re_tmp)

                benign_pre_baseline_tmp = benign_tp_df_sum_wo_controller / (
                    benign_tp_df_sum_wo_controller + benign_fp_df_sum_wo_controller)
                benign_re_baseline_tmp = benign_tp_df_sum_wo_controller / (
                    benign_tp_df_sum_wo_controller + benign_fn_df_sum_wo_controller)
                benign_f1_baseline_tmp = (
                    2 * benign_pre_baseline_tmp * benign_re_baseline_tmp) / (benign_pre_baseline_tmp + benign_re_baseline_tmp)

                pre_list.append((attack_pre_tmp + benign_pre_tmp) / 2)
                re_list.append((attack_re_tmp + benign_re_tmp) / 2)
                f1_list.append((attack_f1_tmp + benign_f1_tmp) / 2)
                pre_baseline_list.append(
                    (attack_pre_baseline_tmp + benign_pre_baseline_tmp) / 2)
                re_baseline_list.append(
                    (attack_re_baseline_tmp + benign_re_baseline_tmp) / 2)
                f1_baseline_list.append(
                    (attack_f1_baseline_tmp + benign_f1_baseline_tmp) / 2)

            # compute the avg and std
            pre_avg_list.append(np.mean(pre_list))
            re_avg_list.append(np.mean(re_list))
            f1_avg_list.append(np.mean(f1_list))

            pre_std_list.append(np.std(pre_list))
            re_std_list.append(np.std(re_list))
            f1_std_list.append(np.std(f1_list))

        pre_baseline_avg_val = np.mean(pre_baseline_list)
        re_baseline_avg_val = np.mean(re_baseline_list)
        f1_baseline_avg_val = np.mean(f1_baseline_list)

        pre_baseline_std_val = np.std(pre_baseline_list)
        re_baseline_std_val = np.std(re_baseline_list)
        f1_baseline_std_val = np.std(f1_baseline_list)

        ############################## plot ##############################
        fig = plt.figure(figsize=self.figsize_single)
        # Set width of bar
        barWidth = 0.15

        # Set position of bars on x-axis
        r1 = np.arange(3)
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]
        r_list = [r1, r2, r3, r4, r5]

        for i in range(len(self._GINI_THRESHOLD_LIST) + 1):
            # exact the values for each gini threshold or baseline
            avg_values_to_gini_list = []
            std_values_to_gini_list = []
            if i < 4:
                # avg
                avg_values_to_gini_list.append(f1_avg_list[i])
                avg_values_to_gini_list.append(pre_avg_list[i])
                avg_values_to_gini_list.append(re_avg_list[i])
                # std
                std_values_to_gini_list.append(f1_std_list[i])
                std_values_to_gini_list.append(pre_std_list[i])
                std_values_to_gini_list.append(re_std_list[i])

                label_name = "$MC_{thr}$ = " + f"0.{i + 1}"
            else:
                # append baseline value
                # avg
                avg_values_to_gini_list.append(f1_baseline_avg_val)
                avg_values_to_gini_list.append(pre_baseline_avg_val)
                avg_values_to_gini_list.append(re_baseline_avg_val)
                # std
                std_values_to_gini_list.append(f1_baseline_std_val)
                std_values_to_gini_list.append(pre_baseline_std_val)
                std_values_to_gini_list.append(re_baseline_std_val)

                label_name = "Baseline"
            # plot for each gini threshold or baseline
            plt.bar(r_list[i], avg_values_to_gini_list,
                    width=barWidth, label=label_name)
            plt.errorbar(r_list[i], avg_values_to_gini_list,
                         yerr=std_values_to_gini_list, fmt='none', ecolor='black', capsize=3)
            # add number on top of bar for gini 0.3 and baseline
            if i in [2, 4]:
                for j, val in enumerate(avg_values_to_gini_list):
                    plt.text(r_list[i][j], val + 0.03,
                             format(val, ".3f"), ha='center', va='center')

        plt.xlabel("Macro Average Metric", fontsize=self.fontsize_label)
        plt.xticks(r3, ["F1 Score", "Precision", "Recall"])
        plt.ylabel("Macro Average Value", fontsize=self.fontsize_label)
        plt.ylim(ylim_arr)
        plt.legend(loc="lower left")

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_ensemble_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_metric_sum(self, flow_type):
        """Plot values of benign and attack for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.

        Args:
            flow_type: benign, attack
                The type of flows
        """
        # set the metric to plot
        # precision
        if flow_type == "benign":
            metrics = ["benign_pre_sum",
                       "benign_re_sum",
                       "benign_f1_sum",
                       "benign_pre_sum_wo_controller",
                       "benign_re_sum_wo_controller",
                       "benign_f1_sum_wo_controller"]
        elif flow_type == "attack":
            metrics = ["attack_pre_sum",
                       "attack_re_sum",
                       "attack_f1_sum",
                       "attack_pre_sum_wo_controller",
                       "attack_re_sum_wo_controller",
                       "attack_f1_sum_wo_controller"]
        else:
            raise ValueError("The given flow type is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metrics

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini[metrics[0]].tolist()
                re_tmp = df_index_gini[metrics[1]].tolist()
                f1_tmp = df_index_gini[metrics[2]].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))

            # convert to numpy array
            pre_avg_arr = np.array(pre_avg_list)
            re_avg_arr = np.array(re_avg_list)
            f1_avg_arr = np.array(f1_avg_list)
            pre_std_arr = np.array(pre_std_list)
            re_std_arr = np.array(re_std_list)
            f1_std_arr = np.array(f1_std_list)

            # print(f"{day} pre avg: {pre_avg_arr}")
            # print(f"{day} rre avg: {re_avg_arr}")
            # print(f"{day} f1 avg: {f1_avg_arr}")
            # print(f"{day} pre std: {pre_std_arr}")
            # print(f"{day} re std: {re_std_arr}")
            # print(f"{day} f1 std: {f1_std_arr}")

            # get the baseline value list
            gini_threshold_count = len(self._GINI_THRESHOLD_LIST)
            pre_baseline_list = [df_index[metrics[3]].mean(
                axis=0)] * gini_threshold_count
            re_baseline_list = [df_index[metrics[4]].mean(
                axis=0)] * gini_threshold_count
            f1_baseline_list = [df_index[metrics[5]].mean(
                axis=0)] * gini_threshold_count

            ############################## plot ##############################
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))
            fig.tight_layout()
            plt.subplots_adjust(wspace=0.2)

            # plot the macro average
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_avg_arr, linestyle='-', marker='o',
                        color=self._COLOR_DICT["f1_color"], label=f"Macro-Average F1 Score of {flow_type.capitalize()}")
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_avg_arr, linestyle='-', marker='o',
                        color=self._COLOR_DICT["pre_color"], label=f"Macro-Average Precision of {flow_type.capitalize()}")
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_avg_arr, linestyle='-', marker='o',
                        color=self._COLOR_DICT["re_color"], label=f"Macro-Average Recall of {flow_type.capitalize()}")

            # plot the deviation
            axs[0].fill_between(self._GINI_THRESHOLD_LIST, f1_avg_arr - f1_std_arr, f1_avg_arr +
                                f1_std_arr, color=self._COLOR_DICT["f1_color"], alpha=self._ALPHA_VAL)
            axs[1].fill_between(self._GINI_THRESHOLD_LIST, pre_avg_arr - pre_std_arr, pre_avg_arr +
                                pre_std_arr, color=self._COLOR_DICT["pre_color"], alpha=self._ALPHA_VAL)
            axs[2].fill_between(self._GINI_THRESHOLD_LIST, re_avg_arr - re_std_arr, re_avg_arr +
                                re_std_arr, color=self._COLOR_DICT["re_color"], alpha=self._ALPHA_VAL)

            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_baseline_list, linestyle='-', color=self._COLOR_DICT["f1_baseline_color"],
                        label=f"Baseline Macro-Average F1 Score of {flow_type.capitalize()}")
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_baseline_list, linestyle='-', color=self._COLOR_DICT["pre_baseline_color"],
                        label=f"Baseline Macro-Average Precision of {flow_type.capitalize()}")
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_baseline_list, linestyle='-',
                        color=self._COLOR_DICT["re_baseline_color"], label=f"Baseline Macro-Average Recall of {flow_type.capitalize()}")

            # set the ylim to the range
            ylim_min = 0.5
            ylim_max = 1
            axs[0].set_ylim([ylim_min, ylim_max])
            axs[1].set_ylim([ylim_min, ylim_max])
            axs[2].set_ylim([ylim_min, ylim_max])

            axs[0].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
            axs[1].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
            axs[2].set(xlabel="Gini Threshold", ylabel="Macro Average Value")

            axs[0].legend()
            axs[1].legend()
            axs[2].legend()

            plt.show()

            # save figure
            fig_name = f"{day}_gini_threshold_to_" + \
                flow_type + "macro_avg_line.png"
            fig_path = self.fig_save_base_path + \
                f"/{day}/figs_lite/" + fig_name
            # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_metric_day_sum(self, flow_type, ylim_arr):
        """Plot values of benign and attack for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.

        Args:
            flow_type: benign, attack
                The type of flows
            ylim_arr: array like data with 2 values
                The range of y axis
        """
        # set the metric to plot
        # precision
        if flow_type == "benign":
            metrics = ["benign_pre_sum",
                       "benign_re_sum",
                       "benign_f1_sum",
                       "benign_pre_sum_wo_controller",
                       "benign_re_sum_wo_controller",
                       "benign_f1_sum_wo_controller"]
        elif flow_type == "attack":
            metrics = ["attack_pre_sum",
                       "attack_re_sum",
                       "attack_f1_sum",
                       "attack_pre_sum_wo_controller",
                       "attack_re_sum_wo_controller",
                       "attack_f1_sum_wo_controller"]
        else:
            raise ValueError("The given flow type is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}

        # baseline of pre, re and f1 for each day
        pre_baseline_day_dict = {}
        re_baseline_day_dict = {}
        f1_baseline_day_dict = {}

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini[metrics[0]].tolist()
                re_tmp = df_index_gini[metrics[1]].tolist()
                f1_tmp = df_index_gini[metrics[2]].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))

            # get the baseline value list
            gini_threshold_count = len(self._GINI_THRESHOLD_LIST)
            pre_baseline_list = [df_index[metrics[3]].mean(
                axis=0)] * gini_threshold_count
            re_baseline_list = [df_index[metrics[4]].mean(
                axis=0)] * gini_threshold_count
            f1_baseline_list = [df_index[metrics[5]].mean(
                axis=0)] * gini_threshold_count

            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_day_dict[day] = pre_baseline_list
            re_baseline_day_dict[day] = re_baseline_list
            f1_baseline_day_dict[day] = f1_baseline_list

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            15, 5), sharey=True, sharex=True)
        fig.tight_layout()
        # plt.subplots_adjust(wspace=0.2)

        marker_list = ['o', '^', 's']
        for i, day in enumerate(self.dataset_day_list):
            label_pre_tmp = day.capitalize() + ' ' + flow_type.capitalize() + " Precision"
            label_re_tmp = day.capitalize() + ' ' + flow_type.capitalize() + " Recall"
            label_f1_tmp = day.capitalize() + ' ' + flow_type.capitalize() + " F1 Score"
            label_pre_baseline_tmp = day.capitalize() + ' ' + flow_type.capitalize() + \
                " Precision Baseline"
            label_re_baseline_tmp = day.capitalize() + ' ' + flow_type.capitalize() + \
                " Recall Baseline"
            label_f1_baseline_tmp = day.capitalize() + ' ' + flow_type.capitalize() + \
                " F1 Score Baseline"
            color_tmp = self._COLOR_DICT[day + "_color"]
            color_baseline_tmp = self._COLOR_DICT[day + "_baseline_color"]
            # plot f1 score
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_f1_tmp)
            axs[0].fill_between(self._GINI_THRESHOLD_LIST, f1_avg_day_dict[day] - f1_std_day_dict[day],
                                f1_avg_day_dict[day] + f1_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[0].plot(self._GINI_THRESHOLD_LIST, f1_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_f1_baseline_tmp)

            # plot precision
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_pre_tmp)
            axs[1].fill_between(self._GINI_THRESHOLD_LIST, pre_avg_day_dict[day] - pre_std_day_dict[day],
                                pre_avg_day_dict[day] + pre_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[1].plot(self._GINI_THRESHOLD_LIST, pre_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_pre_baseline_tmp)

            # plot recall
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_avg_day_dict[day], linestyle='-',
                        marker=marker_list[i], color=color_tmp, label=label_re_tmp)
            axs[2].fill_between(self._GINI_THRESHOLD_LIST, re_avg_day_dict[day] - re_std_day_dict[day],
                                re_avg_day_dict[day] + re_std_day_dict[day], color=color_tmp, alpha=self._ALPHA_VAL)
            axs[2].plot(self._GINI_THRESHOLD_LIST, re_baseline_day_dict[day],
                        linestyle='-', color=color_baseline_tmp, label=label_re_baseline_tmp)

        axs[0].set_ylim(ylim_arr)
        axs[0].set_xticks(self._GINI_THRESHOLD_LIST)
        axs[0].set(xlabel="Gini Threshold", ylabel="Macro Average Value")
        axs[1].set(xlabel="Gini Threshold")
        axs[2].set(xlabel="Gini Threshold")

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        # plt.show()

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_{flow_type}_line.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_macro_avg_metric_day_bar(self, metric, ylim_arr):
        """Plot macro average metrics for each day

        Flows are classified in P4 switch and controller. Bar plot

        Args:
            metric: pre, re, f1
                The evaluation metric
            ylim_arr: array like data with 2 values
                The range of y axis
        """
        # set the metric to plot
        metrics = ["macro_avg_pre_sum",
                   "macro_avg_re_sum",
                   "macro_avg_f1_sum",
                   "macro_avg_pre_sum_wo_controller",
                   "macro_avg_re_sum_wo_controller",
                   "macro_avg_f1_sum_wo_controller"]

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}
        pre_baseline_avg_day_dict = {}
        re_baseline_avg_day_dict = {}
        f1_baseline_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}
        pre_baseline_std_day_dict = {}
        re_baseline_std_day_dict = {}
        f1_baseline_std_day_dict = {}

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini[metrics[0]].tolist()
                re_tmp = df_index_gini[metrics[1]].tolist()
                f1_tmp = df_index_gini[metrics[2]].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))
            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[3]].tolist())
            re_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[4]].tolist())
            f1_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[5]].tolist())
            pre_baseline_std_day_dict[day] = np.std(
                df_index[metrics[3]].tolist())
            re_baseline_std_day_dict[day] = np.std(
                df_index[metrics[4]].tolist())
            f1_baseline_std_day_dict[day] = np.std(
                df_index[metrics[5]].tolist())

        ############################## plot ##############################
        fig = plt.figure(figsize=self.figsize_single)
        # Set width of bar
        barWidth = 0.15

        # Set position of bars on x-axis
        r1 = np.arange(3)
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]
        r_list = [r1, r2, r3, r4, r5]

        for i in range(len(self._GINI_THRESHOLD_LIST) + 1):
            # exact the values for each gini threshold or baseline
            avg_values_to_gini_list = []
            std_values_to_gini_list = []
            for day in self.dataset_day_list:
                if i < 4:
                    # append pre, re or f1
                    if metric == "pre":
                        avg_values_to_gini_list.append(
                            pre_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            pre_std_day_dict[day][i])
                    elif metric == "re":
                        avg_values_to_gini_list.append(
                            re_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            re_std_day_dict[day][i])
                    elif metric == "f1":
                        avg_values_to_gini_list.append(
                            f1_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            f1_std_day_dict[day][i])
                    else:
                        raise ValueError(
                            "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")
                    label_name = "$MC_{thr}$ = " + f"0.{i + 1}"
                else:
                    # append baseline value
                    if metric == "pre":
                        avg_values_to_gini_list.append(
                            pre_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            pre_baseline_std_day_dict[day])
                    elif metric == "re":
                        avg_values_to_gini_list.append(
                            re_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            re_baseline_std_day_dict[day])
                    elif metric == "f1":
                        avg_values_to_gini_list.append(
                            f1_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            f1_baseline_std_day_dict[day])
                    else:
                        raise ValueError(
                            "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")
                    label_name = "Baseline"

            print(avg_values_to_gini_list)
            # plot for each gini threshold or baseline
            plt.bar(r_list[i], avg_values_to_gini_list,
                    width=barWidth, label=label_name)
            plt.errorbar(r_list[i], avg_values_to_gini_list,
                         yerr=std_values_to_gini_list, fmt='none', ecolor='black', capsize=3)
            # add number on top of bar for gini 0.3 and baseline
            if i in [2, 4]:
                for j, val in enumerate(avg_values_to_gini_list):
                    plt.text(r_list[i][j]+barWidth/2, val + 0.02,
                             format(val, ".3f"), ha='center', va='center')

        # get the y label name
        if metric == "pre":
            y_label_name = f"Macro-Average Precision"
        elif metric == "re":
            y_label_name = f"Macro-Average Recall"
        elif metric == "f1":
            y_label_name = f"Macro-Average F1 Score"
        else:
            raise ValueError(
                "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")

        plt.xlabel("Attack Type", fontsize=self.fontsize_label)
        plt.xticks(r3, ["Brute Force", "DoS/DDoS", "Botnet"])
        plt.ylabel(y_label_name, fontsize=self.fontsize_label)
        plt.ylim(ylim_arr)
        plt.legend(loc="lower left")

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_{metric}_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_metric_day_sum_bar(self, flow_type, ylim_arr):
        """Plot values of benign and attack for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller. Bar plot

        Args:
            flow_type: benign, attack
                The type of flows
            ylim_arr: array like data with 2 values
                The range of y axis
        """
        # set the metric to plot
        # precision
        if flow_type == "benign":
            metrics = ["benign_pre_sum",
                       "benign_re_sum",
                       "benign_f1_sum",
                       "benign_pre_sum_wo_controller",
                       "benign_re_sum_wo_controller",
                       "benign_f1_sum_wo_controller"]
            y_label_plot = "Benign Metric Value"
        elif flow_type == "attack":
            metrics = ["attack_pre_sum",
                       "attack_re_sum",
                       "attack_f1_sum",
                       "attack_pre_sum_wo_controller",
                       "attack_re_sum_wo_controller",
                       "attack_f1_sum_wo_controller"]
            y_label_plot = "Attack Metric Value"
        else:
            raise ValueError("The given flow type is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}
        pre_baseline_avg_day_dict = {}
        re_baseline_avg_day_dict = {}
        f1_baseline_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}
        pre_baseline_std_day_dict = {}
        re_baseline_std_day_dict = {}
        f1_baseline_std_day_dict = {}

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini[metrics[0]].tolist()
                re_tmp = df_index_gini[metrics[1]].tolist()
                f1_tmp = df_index_gini[metrics[2]].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))
            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[3]].tolist())
            re_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[4]].tolist())
            f1_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[5]].tolist())
            pre_baseline_std_day_dict[day] = np.std(
                df_index[metrics[3]].tolist())
            re_baseline_std_day_dict[day] = np.std(
                df_index[metrics[4]].tolist())
            f1_baseline_std_day_dict[day] = np.std(
                df_index[metrics[5]].tolist())

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            15, 5), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.15

        # Set position of bars on x-axis
        r1 = np.arange(3)
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]

        r_list = [r1, r2, r3, r4, r5]

        for i, day in enumerate(self.dataset_day_list):
            # plot one subfigure for one day
            for j in range(len(self._GINI_THRESHOLD_LIST) + 1):
                # exact the values for each gini threshold or baseline
                avg_values_to_gini_list = []
                std_values_to_gini_list = []
                if j < 4:
                    # avg
                    avg_values_to_gini_list.append(f1_avg_day_dict[day][j])
                    avg_values_to_gini_list.append(pre_avg_day_dict[day][j])
                    avg_values_to_gini_list.append(re_avg_day_dict[day][j])
                    # std
                    std_values_to_gini_list.append(f1_std_day_dict[day][j])
                    std_values_to_gini_list.append(pre_std_day_dict[day][j])
                    std_values_to_gini_list.append(re_std_day_dict[day][j])

                    label_name = f"Model Confidence Threshold = 0.{j + 1}"
                else:
                    # append baseline value
                    # avg
                    avg_values_to_gini_list.append(
                        f1_baseline_avg_day_dict[day])
                    avg_values_to_gini_list.append(
                        pre_baseline_avg_day_dict[day])
                    avg_values_to_gini_list.append(
                        re_baseline_avg_day_dict[day])
                    # std
                    std_values_to_gini_list.append(
                        f1_baseline_std_day_dict[day])
                    std_values_to_gini_list.append(
                        pre_baseline_std_day_dict[day])
                    std_values_to_gini_list.append(
                        re_baseline_std_day_dict[day])

                    label_name = "Baseline"

                # x axis postiones in one tick. for gini thresholdes and baseline
                axs[i].bar(r_list[j], avg_values_to_gini_list,
                           width=barWidth, label=label_name)
                axs[i].errorbar(r_list[j], avg_values_to_gini_list,
                                yerr=std_values_to_gini_list, fmt='none', ecolor='black', capsize=3)

                # add number on top of bar for gini 0.3 and baseline
                if j in [2, 4]:
                    for m, val in enumerate(avg_values_to_gini_list):
                        axs[i].text(r_list[j][m] - barWidth/2, avg_values_to_gini_list[m] +
                                    0.005, format(avg_values_to_gini_list[m], ".3f"))

            axs[i].set_xlabel("Metric")
            axs[i].set_ylim(ylim_arr)
            axs[i].legend(loc="lower left")

        axs[0].set_xticks(r3, ["F1 Score", "Precision", "Recall"])
        axs[0].set_ylabel(y_label_plot)

        # set titles for each subplot
        axs[0].set_title("(A) Brute Force")
        axs[1].set_title("(B) DoS/DDoS")
        axs[2].set_title("(C) Botnet")

        # save figure
        fig_name = f"gini_threshold_to_macro_avg_{flow_type}_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_metric_type_bar(self, flow_type, metric, ylim_arr):
        """Plot values of benign and attack for a specific metric in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller. Bar plot

        Args:
            flow_type: benign, attack
                The type of flows
            metric: pre, re, f1
                The evaluation metric
            ylim_arr: array like data with 2 values
                The range of y axis
        """
        # set the metric to plot
        # precision
        if flow_type == "benign":
            metrics = ["benign_pre_sum",
                       "benign_re_sum",
                       "benign_f1_sum",
                       "benign_pre_sum_wo_controller",
                       "benign_re_sum_wo_controller",
                       "benign_f1_sum_wo_controller"]
        elif flow_type == "attack":
            metrics = ["attack_pre_sum",
                       "attack_re_sum",
                       "attack_f1_sum",
                       "attack_pre_sum_wo_controller",
                       "attack_re_sum_wo_controller",
                       "attack_f1_sum_wo_controller"]
        else:
            raise ValueError("The given flow type is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average pre, re and f1 for each day
        pre_avg_day_dict = {}
        re_avg_day_dict = {}
        f1_avg_day_dict = {}
        pre_baseline_avg_day_dict = {}
        re_baseline_avg_day_dict = {}
        f1_baseline_avg_day_dict = {}

        # standard deviation of pre, re and f1 for each day
        pre_std_day_dict = {}
        re_std_day_dict = {}
        f1_std_day_dict = {}
        pre_baseline_std_day_dict = {}
        re_baseline_std_day_dict = {}
        f1_baseline_std_day_dict = {}

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]

            # save the avg and std for each gini threshold
            pre_avg_list = []
            re_avg_list = []
            f1_avg_list = []
            pre_std_list = []
            re_std_list = []
            f1_std_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                pre_tmp = df_index_gini[metrics[0]].tolist()
                re_tmp = df_index_gini[metrics[1]].tolist()
                f1_tmp = df_index_gini[metrics[2]].tolist()
                pre_avg_list.append(np.mean(pre_tmp))
                re_avg_list.append(np.mean(re_tmp))
                f1_avg_list.append(np.mean(f1_tmp))
                pre_std_list.append(np.std(pre_tmp))
                re_std_list.append(np.std(re_tmp))
                f1_std_list.append(np.std(f1_tmp))
            # save average pre, re and f1 into the dictionary for this day
            pre_avg_day_dict[day] = np.array(pre_avg_list)
            re_avg_day_dict[day] = np.array(re_avg_list)
            f1_avg_day_dict[day] = np.array(f1_avg_list)
            # save standard deviation of pre, re and f1 into the dictionary for this day
            pre_std_day_dict[day] = np.array(pre_std_list)
            re_std_day_dict[day] = np.array(re_std_list)
            f1_std_day_dict[day] = np.array(f1_std_list)
            # save baseline data for this day
            pre_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[3]].tolist())
            re_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[4]].tolist())
            f1_baseline_avg_day_dict[day] = np.mean(
                df_index[metrics[5]].tolist())
            pre_baseline_std_day_dict[day] = np.std(
                df_index[metrics[3]].tolist())
            re_baseline_std_day_dict[day] = np.std(
                df_index[metrics[4]].tolist())
            f1_baseline_std_day_dict[day] = np.std(
                df_index[metrics[5]].tolist())

        ############################## plot ##############################
        # Set width of bar
        barWidth = 0.15

        # Set position of bars on x-axis
        r1 = np.arange(3)
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]
        r_list = [r1, r2, r3, r4, r5]

        for i in range(len(self._GINI_THRESHOLD_LIST) + 1):
            # exact the values for each gini threshold or baseline
            avg_values_to_gini_list = []
            std_values_to_gini_list = []
            for day in self.dataset_day_list:
                if i < 4:
                    # append pre, re or f1
                    if metric == "pre":
                        avg_values_to_gini_list.append(
                            pre_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            pre_std_day_dict[day][i])
                    elif metric == "re":
                        avg_values_to_gini_list.append(
                            re_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            re_std_day_dict[day][i])
                    elif metric == "f1":
                        avg_values_to_gini_list.append(
                            f1_avg_day_dict[day][i])
                        std_values_to_gini_list.append(
                            f1_std_day_dict[day][i])
                    else:
                        raise ValueError(
                            "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")
                    label_name = f"Model Confidence Threshold = 0.{i + 1}"
                else:
                    # append baseline value
                    if metric == "pre":
                        avg_values_to_gini_list.append(
                            pre_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            pre_baseline_std_day_dict[day])
                    elif metric == "re":
                        avg_values_to_gini_list.append(
                            re_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            re_baseline_std_day_dict[day])
                    elif metric == "f1":
                        avg_values_to_gini_list.append(
                            f1_baseline_avg_day_dict[day])
                        std_values_to_gini_list.append(
                            f1_baseline_std_day_dict[day])
                    else:
                        raise ValueError(
                            "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")
                    label_name = "Baseline"

            print(avg_values_to_gini_list)
            # plot for each gini threshold or baseline
            plt.bar(r_list[i], avg_values_to_gini_list,
                    width=barWidth, label=label_name)
            plt.errorbar(r_list[i], avg_values_to_gini_list,
                         yerr=std_values_to_gini_list, fmt='none', ecolor='black', capsize=3)
            # add number on top of bar for gini 0.3 and baseline
            if i in [2, 4]:
                for j, val in enumerate(avg_values_to_gini_list):
                    plt.text(r_list[i][j] - barWidth/2, val + 0.01,
                             format(val, ".3f"))

        # get the y label name
        if metric == "pre":
            y_label_name = f"Precision of {flow_type.capitalize()}"
        elif metric == "re":
            y_label_name = f"Recall of {flow_type.capitalize()}"
        elif metric == "f1":
            y_label_name = f"F1 Score of {flow_type.capitalize()}"
        else:
            raise ValueError(
                "The given metric is illegal. Please give it within 'pre', 're' and 'f1'")

        plt.xlabel("Attack Type")
        plt.xticks(r3, ["Brute Force", "DoS/DDoS", "Botnet"])
        plt.ylabel(y_label_name)
        plt.ylim(ylim_arr)
        plt.legend(loc="lower left")

        # save figure
        fig_name = f"gini_threshold_to_{flow_type}_{metric}_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_total_flow_to_controller(self, wspace_val, bbox_arr, two_y_axis=False):
        """Plot the number of flows sent to controller compared to the total extracted flows for different gini threshold values.

        """
        metrics = ["flows_to_controller_sum",
                   "flow_benign_real_sum", "flow_attack_real_sum"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average total flow sent to controller, total extracted flows and the ratio of to_controller and total flow for each day
        flows_to_controller_sum_avg_day_dict = {}
        flows_total_avg_day_dict = {}
        ratio_to_controller_over_total_avg_day_dict = {}

        # standard deviation of total flow sent to controller, total extracted flows and the ratio of to_controller and total flow for each day
        flows_to_controller_sum_std_day_dict = {}
        flows_total_std_day_dict = {}
        ratio_to_controller_over_total_std_day_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]
            # save the avg and std for each gini threshold
            flows_to_controller_sum_avg_list = []
            flows_total_avg_list = []
            ratio_to_controller_over_total_avg_list = []

            flows_to_controller_sum_std_list = []
            flows_total_std_list = []
            ratio_to_controller_over_total_std_list = []

            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                flows_to_controller_sum_tmp = df_index_gini[metrics[0]].tolist(
                )
                flows_total_tmp = np.array(df_index_gini[metrics[1]].tolist(
                )) + np.array(df_index_gini[metrics[2]].tolist())
                ratio_to_controller_over_total_tmp = np.array(
                    flows_to_controller_sum_tmp) / np.array(flows_total_tmp)

                flows_to_controller_sum_avg_list.append(
                    np.mean(flows_to_controller_sum_tmp))
                flows_total_avg_list.append(np.mean(flows_total_tmp))
                ratio_to_controller_over_total_avg_list.append(
                    np.mean(ratio_to_controller_over_total_tmp))

                flows_to_controller_sum_std_list.append(
                    np.std(flows_to_controller_sum_tmp))
                flows_total_std_list.append(np.std(flows_total_tmp))
                ratio_to_controller_over_total_std_list.append(
                    np.std(ratio_to_controller_over_total_tmp))

            # save average to dictionary
            flows_to_controller_sum_avg_day_dict[day] = np.array(
                flows_to_controller_sum_avg_list)
            flows_total_avg_day_dict[day] = np.array(flows_total_avg_list)
            ratio_to_controller_over_total_avg_day_dict[day] = np.array(
                ratio_to_controller_over_total_avg_list)

            # save standard deviation to dictionary
            flows_to_controller_sum_std_day_dict[day] = np.array(
                flows_to_controller_sum_std_list)
            flows_total_std_day_dict[day] = np.array(flows_total_std_list)
            ratio_to_controller_over_total_std_day_dict[day] = np.array(
                ratio_to_controller_over_total_std_list)

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            12, 4.5), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.5

        # Set position of bars on x-axis
        r1 = np.arange(len(self._GINI_THRESHOLD_LIST))

        # plot bar for number of flows sent to controller
        for i, day in enumerate(self.dataset_day_list):
            axs[i].bar(r1, flows_to_controller_sum_avg_day_dict[day],
                       width=barWidth, label="Number of Sub-flows")
            axs[i].set_xticks(r1, self._GINI_THRESHOLD_LIST,
                              fontsize=self.fontsize_ticks_subplot)

            # plot with two y axises
            if two_y_axis:
                # axs for the y label on the right hand side
                axs_twin = []
                for i, ax in enumerate(axs):
                    axs_twin.append(ax.twinx())

                # plot line for the percentage of flows sent to controller
                for i, day in enumerate(self.dataset_day_list):
                    axs_twin[i].plot(r1, ratio_to_controller_over_total_avg_day_dict[day],
                                     marker='o', color="black", label="Percentage of Sub-flows")
                    axs_twin[i].set_ylim(0, 1.09)
                    axs_twin[i].tick_params(labelright=False)
                    axs_twin[i].legend(loc="upper right")

                    # add number of each point in the line
                    for j, x_pos in enumerate(r1):
                        axs_twin[i].text(x_pos, ratio_to_controller_over_total_avg_day_dict[day][j] + 0.01,
                                         format(ratio_to_controller_over_total_avg_day_dict[day][j] * 100, ".1f") + '%')
                axs_twin[2].set_ylabel(
                    "Percentage of Flows Sent to CP-IDS", fontsize=self.fontsize_label_subplot)
                axs_twin[2].tick_params(labelright=True)
                # axs_twin[2].set_yticks([0.1, 0.2, 0.3, 0.4, 0.5], ["10%", "20%", "30%", "40%", "50%"])
                axs[i].legend(loc="upper left",
                              fontsize=self.fontsize_legend_subplot)

             # plot with 1 y axis
            else:
                axs[i].plot(r1, flows_to_controller_sum_avg_day_dict[day],
                            marker='o', color="black", label="Percentage of Sub-flows")

                # add number of each point in the line
                for j, x_pos in enumerate(r1):
                    if j in [0, 3]:
                        axs[i].text(x_pos-0.3, flows_to_controller_sum_avg_day_dict[day][j] + 3000,
                                    format(ratio_to_controller_over_total_avg_day_dict[day][j] * 100, ".1f") + '%', fontsize=self.fontsize_text_subplot)
                    else:
                        axs[i].text(x_pos-0.04, flows_to_controller_sum_avg_day_dict[day][j] + 3000,
                                    format(ratio_to_controller_over_total_avg_day_dict[day][j] * 100, ".1f") + '%', fontsize=self.fontsize_text_subplot)

        axs[1].set_xlabel("Model Confidence Threshold",
                          fontsize=self.fontsize_label_subplot)
        axs[0].legend(loc="best", bbox_to_anchor=bbox_arr,
                      fontsize=self.fontsize_legend_subplot, ncol=2, fancybox=True)
        axs[0].set_ylabel("Sub-flows Sent to CP-IDS",
                          fontsize=self.fontsize_label_subplot)
        axs[0].set_ylim([0, 130000])
        axs[0].yaxis.set_tick_params(labelsize=self.fontsize_ticks_subplot)
        if two_y_axis:
            axs[0].set_ylim([0, 135000])

        # set titles for each subplot
        axs[0].set_title("(A) Brute Force",
                         fontsize=self.fontsize_title_subplot)
        axs[1].set_title("(B) DoS/DDoS", fontsize=self.fontsize_title_subplot)
        axs[2].set_title("(C) Botnet", fontsize=self.fontsize_title_subplot)

        # change the space between plots
        plt.subplots_adjust(left=None, bottom=None, right=None,
                            top=None, wspace=wspace_val, hspace=None)

        # save figure
        fig_name = f"gini_threshold_to_flows_to_controller_bar_line.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_confusion_matrix_to_controller(self, with_std=False, with_number=False):
        """Plot the numbers of fn, fp, tn, tp and total flows classified in switch and sent to controller for different gini threshold value.

        One subfigure contains the results of all of the days.

        Args:
            with_std: True, False
                Add the standard deviation for the bar of total flows
            with_number: True, False
                Add the absolute number for the bar of total flows
        """
        metrics = ["fn_to_controller",
                   "fp_to_controller",
                   "tn_to_controller",
                   "tp_to_controller",
                   "flows_to_controller_sum"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average fn, fp, tn, tp, total flow sent to controller and the ratio of to_controller and total flow for each day
        fn_to_controller_avg_day_dict = {}
        fp_to_controller_avg_day_dict = {}
        tn_to_controller_avg_day_dict = {}
        tp_to_controller_avg_day_dict = {}
        flows_to_controller_sum_avg_day_dict = {}

        # standard deviation of fn, fp, tn, tp, total flow sent to controller and the ratio of to_controller and total flow for each day
        fn_to_controller_std_day_dict = {}
        fp_to_controller_std_day_dict = {}
        tn_to_controller_std_day_dict = {}
        tp_to_controller_std_day_dict = {}
        flows_to_controller_sum_std_day_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]
            # save the avg and std for each gini threshold
            fn_to_controller_avg_list = []
            fp_to_controller_avg_list = []
            tn_to_controller_avg_list = []
            tp_to_controller_avg_list = []
            flows_to_controller_sum_avg_list = []

            fn_to_controller_std_list = []
            fp_to_controller_std_list = []
            tn_to_controller_std_list = []
            tp_to_controller_std_list = []
            flows_to_controller_sum_std_list = []

            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                fn_to_controller_tmp = df_index_gini[metrics[0]].tolist()
                fp_to_controller_tmp = df_index_gini[metrics[1]].tolist()
                tn_to_controller_tmp = df_index_gini[metrics[2]].tolist()
                tp_to_controller_tmp = df_index_gini[metrics[3]].tolist()
                flows_to_controller_sum_tmp = df_index_gini[metrics[4]].tolist(
                )

                fn_to_controller_avg_list.append(np.mean(fn_to_controller_tmp))
                fp_to_controller_avg_list.append(np.mean(fp_to_controller_tmp))
                tn_to_controller_avg_list.append(np.mean(tn_to_controller_tmp))
                tp_to_controller_avg_list.append(np.mean(tp_to_controller_tmp))
                flows_to_controller_sum_avg_list.append(
                    np.mean(flows_to_controller_sum_tmp))

                fn_to_controller_std_list.append(np.std(fn_to_controller_tmp))
                fp_to_controller_std_list.append(np.std(fp_to_controller_tmp))
                tn_to_controller_std_list.append(np.std(tn_to_controller_tmp))
                tp_to_controller_std_list.append(np.std(tp_to_controller_tmp))
                flows_to_controller_sum_std_list.append(
                    np.std(flows_to_controller_sum_tmp))

            # save average to dictionary
            fn_to_controller_avg_day_dict[day] = np.array(
                fn_to_controller_avg_list)
            fp_to_controller_avg_day_dict[day] = np.array(
                fp_to_controller_avg_list)
            tn_to_controller_avg_day_dict[day] = np.array(
                tn_to_controller_avg_list)
            tp_to_controller_avg_day_dict[day] = np.array(
                tp_to_controller_avg_list)
            flows_to_controller_sum_avg_day_dict[day] = np.array(
                flows_to_controller_sum_avg_list)

            # save standard deviation to dictionary
            fn_to_controller_std_day_dict[day] = np.array(
                fn_to_controller_std_list)
            fp_to_controller_std_day_dict[day] = np.array(
                fp_to_controller_std_list)
            tn_to_controller_std_day_dict[day] = np.array(
                tn_to_controller_std_list)
            tp_to_controller_std_day_dict[day] = np.array(
                tp_to_controller_std_list)
            flows_to_controller_sum_std_day_dict[day] = np.array(
                flows_to_controller_sum_std_list)

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            12, 4), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.2

        # Set position of bars on x-axis
        r1 = np.arange(len(self._GINI_THRESHOLD_LIST))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]
        r5 = [x + barWidth for x in r4]

        # the maximum value of each bar
        ylim_max = 0

        for i, day in enumerate(self.dataset_day_list):
            flows_to_controller_sum_avg_day_tmp = flows_to_controller_sum_avg_day_dict[day]
            if (max(flows_to_controller_sum_avg_day_tmp) > ylim_max):
                ylim_max = max(flows_to_controller_sum_avg_day_tmp)

            # plot bars
            axs[i].bar(r1, fn_to_controller_avg_day_dict[day],
                       color=self._COLOR_DICT["fn_color"], width=barWidth, label="FN")
            axs[i].bar(r2, fp_to_controller_avg_day_dict[day],
                       color=self._COLOR_DICT["fp_color"], width=barWidth, label="FP")
            axs[i].bar(r3, tn_to_controller_avg_day_dict[day],
                       color=self._COLOR_DICT["tn_color"], width=barWidth, label="TN")
            axs[i].bar(r4, tp_to_controller_avg_day_dict[day],
                       color=self._COLOR_DICT["tp_color"], width=barWidth, label="TP")
            # axs[i].bar(r5, flows_to_controller_sum_avg_day_tmp, color=self._COLOR_DICT["sum_color"], width=barWidth, label="Flows Sent to Controller")

            # add std for the total flows
            if with_std:
                axs[i].errorbar(r1, fn_to_controller_avg_day_dict[day],
                                yerr=fn_to_controller_std_day_dict[day], fmt='none', ecolor='black', capsize=3)
                axs[i].errorbar(r2, fp_to_controller_avg_day_dict[day],
                                yerr=fp_to_controller_std_day_dict[day], fmt='none', ecolor='black', capsize=3)
                axs[i].errorbar(r3, tn_to_controller_avg_day_dict[day],
                                yerr=tn_to_controller_std_day_dict[day], fmt='none', ecolor='black', capsize=3)
                axs[i].errorbar(r4, tp_to_controller_avg_day_dict[day],
                                yerr=tp_to_controller_std_day_dict[day], fmt='none', ecolor='black', capsize=3)
                # axs[i].errorbar(r5, flows_to_controller_sum_avg_day_tmp, yerr=flows_to_controller_sum_std_day_dict[day], fmt='none', ecolor='black', capsize=3)

            # add absolute number for the total flows
            # if with_number:
            #     for j, val in enumerate(flows_to_controller_sum_avg_day_tmp):
            #         if j <= 1:
            #             diff_x_tmp = barWidth * 1.5
            #         else:
            #             diff_x_tmp = barWidth
            #         y_position = flows_to_controller_sum_avg_day_tmp[j] + flows_to_controller_sum_avg_day_tmp[j] / 10
            #         axs[i].text(r5[j] - diff_x_tmp, y_position, str(int(flows_to_controller_sum_avg_day_tmp[j])))

            axs[i].set_xticks(
                [r + barWidth*2 for r in range(len(self._GINI_THRESHOLD_LIST))], self._GINI_THRESHOLD_LIST)
            axs[i].set_yscale("log")
            axs[i].set_xlabel("Model Confidence Threshold")
            axs[i].legend()

        # set the shared ylabel
        axs[0].set_ylabel("Number of Flows Sent to Controller (log scale)")
        ylim_max += 100000
        axs[0].set_ylim([10, ylim_max])

        # set titles for each subplot
        axs[0].set_title("(A) Brute Force")
        axs[1].set_title("(B) DoS/DDoS")
        axs[2].set_title("(C) Botnet")

        # save figure
        fig_name = "gini_threshold_to_confusion_matrix_to_controller_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_confusion_matrix_to_controller_ratio_stacked(self, wspace_val, bbox_arr):
        """Plot the numbers of fn, fp, tn, tp and total flows classified in switch and sent to controller for different gini threshold value.

        Args:
        """
        metrics = ["fn_to_controller",
                   "fp_to_controller",
                   "tn_to_controller",
                   "tp_to_controller",
                   "flows_to_controller_sum"]
        # columns should be extracted from indexed file of each dataset
        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # ratio of average fn, fp, tn, tp and sum for each day
        fn_to_controller_avg_day_ratio_dict = {}
        fp_to_controller_avg_day_ratio_dict = {}
        tn_to_controller_avg_day_ratio_dict = {}
        tp_to_controller_avg_day_ratio_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            # extract the values of pre, re and f1 of each gini value threshold
            df_index = self.df_index_list[i][columns]
            # save the avg and std for each gini threshold
            fn_to_controller_avg_list = []
            fp_to_controller_avg_list = []
            tn_to_controller_avg_list = []
            tp_to_controller_avg_list = []
            flows_to_controller_sum_avg_list = []
            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]
                # get the list of values of pre, re and f1 for each gini threshold
                fn_to_controller_tmp = df_index_gini[metrics[0]].tolist()
                fp_to_controller_tmp = df_index_gini[metrics[1]].tolist()
                tn_to_controller_tmp = df_index_gini[metrics[2]].tolist()
                tp_to_controller_tmp = df_index_gini[metrics[3]].tolist()
                flows_to_controller_sum_tmp = df_index_gini[metrics[4]].tolist(
                )
                fn_to_controller_avg_list.append(np.mean(fn_to_controller_tmp))
                fp_to_controller_avg_list.append(np.mean(fp_to_controller_tmp))
                tn_to_controller_avg_list.append(np.mean(tn_to_controller_tmp))
                tp_to_controller_avg_list.append(np.mean(tp_to_controller_tmp))
                flows_to_controller_sum_avg_list.append(
                    np.mean(flows_to_controller_sum_tmp))

            # compute the percentage of fn, fp, tn and tp
            fn_to_controller_avg_day_ratio_dict[day] = np.array(
                fn_to_controller_avg_list) / np.array(flows_to_controller_sum_avg_list)
            fp_to_controller_avg_day_ratio_dict[day] = np.array(
                fp_to_controller_avg_list) / np.array(flows_to_controller_sum_avg_list)
            tn_to_controller_avg_day_ratio_dict[day] = np.array(
                tn_to_controller_avg_list) / np.array(flows_to_controller_sum_avg_list)
            tp_to_controller_avg_day_ratio_dict[day] = np.array(
                tp_to_controller_avg_list) / np.array(flows_to_controller_sum_avg_list)

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            12, 4.5), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.5

        # Set position of bars on x-axis
        r1 = np.arange(len(self._GINI_THRESHOLD_LIST))

        for i, day in enumerate(self.dataset_day_list):
            # plot bars
            axs[i].bar(r1, fn_to_controller_avg_day_ratio_dict[day],
                       width=barWidth, color=self._COLOR_DICT["fn_color"], label="FN")
            axs[i].bar(r1, fp_to_controller_avg_day_ratio_dict[day], width=barWidth,
                       bottom=fn_to_controller_avg_day_ratio_dict[day], color=self._COLOR_DICT["fp_color"], label="FP")
            axs[i].bar(r1, tn_to_controller_avg_day_ratio_dict[day], width=barWidth, bottom=(
                fn_to_controller_avg_day_ratio_dict[day]+fp_to_controller_avg_day_ratio_dict[day]), color=self._COLOR_DICT["tn_color"], label="TN")
            axs[i].bar(r1, tp_to_controller_avg_day_ratio_dict[day], width=barWidth, bottom=(fn_to_controller_avg_day_ratio_dict[day] +
                       fp_to_controller_avg_day_ratio_dict[day]+tn_to_controller_avg_day_ratio_dict[day]), color=self._COLOR_DICT["tp_color"], label="TP")

            # plot lines
            axs[i].plot(r1, fn_to_controller_avg_day_ratio_dict[day] +
                        fp_to_controller_avg_day_ratio_dict[day], color="black", marker='o', label="FN and FP")
            # add text around the point of line
            for j in r1:
                y_val = fn_to_controller_avg_day_ratio_dict[day][j] + \
                    fp_to_controller_avg_day_ratio_dict[day][j]
                # convert y value to percentage
                y_val_str = format(y_val * 100, '.1f') + '%'
                x_pos_diff = 0
                y_pos_diff = 0
                if j == 0:
                    x_pos_diff = barWidth * 0.95
                    y_pos_diff = -0.01
                elif j == 1:
                    x_pos_diff = barWidth * 0.7
                    y_pos_diff = -0.07
                elif j == 2:
                    y_pos_diff = 0.05
                elif j == 3:
                    y_pos_diff = -0.07

                axs[i].text(j+x_pos_diff, y_val+y_pos_diff, y_val_str,
                            fontsize=self.fontsize_text_subplot, ha='center', va='center')

            axs[i].set_xticks(
                [r for r in range(len(self._GINI_THRESHOLD_LIST))], self._GINI_THRESHOLD_LIST)
            axs[i].xaxis.set_tick_params(labelsize=self.fontsize_ticks_subplot)

        axs[1].set_xlabel("Model Confidence Threshold",
                          fontsize=self.fontsize_label_subplot)
        # set the shared ylabel
        axs[0].set_ylabel("Sub-flows Sent to CP-IDS",
                          fontsize=self.fontsize_label_subplot)
        axs[0].set_ylim([0, 1])
        axs[0].set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        axs[0].set_yticklabels(
            ["0%", "20%", "40%", "60%", "80%", "100%"], fontsize=self.fontsize_ticks_subplot)
        axs[0].legend(loc="best", bbox_to_anchor=bbox_arr,
                      fontsize=self.fontsize_legend_subplot, ncol=5, fancybox=True)
        # set titles for each subplot
        axs[0].set_title("(A) Brute Force",
                         fontsize=self.fontsize_title_subplot)
        axs[1].set_title("(B) DoS/DDoS", fontsize=self.fontsize_title_subplot)
        axs[2].set_title("(C) Botnet", fontsize=self.fontsize_title_subplot)
        # change the space between plots
        plt.subplots_adjust(left=None, bottom=None, right=None,
                            top=None, wspace=wspace_val, hspace=None)
        # save figure
        fig_name = f"gini_threshold_to_confusion_matrix_to_controller_ratio_stacked_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_confusion_matrix(self, plane, ratio_form=False, stacked=False, log_plot=False):
        """Plot the numbers or percentages of fn, fp, tn and tp classified in switch for different gini threshold value.

        Args:
            plane: p4, to_controller
                Classified plane
                p4: flows are classified in P4.
                to_controller: flows are sent to controller.
            ratio_form: True, False, default: False
                Enable plotting percentage.
            stacked: True, False, default: False
                Enable plotting stacked bar chart.
        """
        # set the metric to plot
        # flow classified in switch
        if plane == "p4":
            metric_name_list = ["fn_p4", "fp_p4",
                                "tn_p4", "tp_p4", "flow_predicted_p4_sum"]
        # flow sent to controller
        elif plane == "to_controller":
            metric_name_list = ["fn_to_controller", "fp_to_controller",
                                "tn_to_controller", "tp_to_controller", "flows_to_controller_sum"]
        else:
            raise ValueError("The given plane name is illegal.")

        # labels to plot the results
        labels = ["FN", "FP", "TN", "TP", "Sum"]
        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metric_name_list
        # colors for fn, fp, tnm tp and sum to plot
        color_list = [
            self._COLOR_DICT["fn_color"],
            self._COLOR_DICT["fp_color"],
            self._COLOR_DICT["tn_color"],
            self._COLOR_DICT["tp_color"],
            self._COLOR_DICT["sum_color"]]

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # get the dataframe of this day
            df_tmp = self.df_final_list[i]
            # dataframe to plot
            if ratio_form:
                # compute the percentage of fn, fp, tn and tp
                df_plot = df_tmp[metric_name_list[:4]].apply(
                    lambda x: x / df_tmp[metric_name_list[len(metric_name_list) - 1]], axis=0)
                # insert the gini_threshold column
                df_plot[columns[0]] = df_tmp[columns[0]]
                y_label_name = "Percentage of Flows"
            else:
                if stacked:
                    df_plot = df_tmp[columns[:len(columns) - 1]]
                else:
                    df_plot = df_tmp[columns]
                y_label_name = "Number of Flows"

            df_plot.plot(x=columns[0], kind="bar", stacked=stacked, logy=log_plot, rot=0, style='-o', color=color_list,
                         xlabel="Gini Threshold", ylabel=y_label_name)
            # if plot the percentage, set the range of y axis
            if ratio_form:
                plt.ylim(0, 1)
            plt.legend(labels)
            # save figure
            if ratio_form:
                fig_name = f"{day}_gini_threshold_to_confusion_matrix_{plane}_ratio"
            else:
                fig_name = f"{day}_gini_threshold_to_confusion_matrix_{plane}_number"
            if stacked:
                fig_name = fig_name + f"_stacked_bar.png"
            else:
                fig_name = fig_name + f"_bar.png"

            fig_path = self.fig_save_base_path + \
                f"/{day}/figs_lite/" + fig_name
            # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_classification_distribution_controller(self, day, gini_thr):
        """Plot the classification distribution of the given day and gini threshold.

        """
        # set the metric to plot
        metrics = ["fn_to_fn_controller",
                   "fn_to_tp_controller",
                   "fp_to_fp_controller",
                   "fp_to_tn_controller",
                   "tn_to_fp_controller",
                   "tn_to_tn_controller",
                   "tp_to_fn_controller",
                   "tp_to_tp_controller"]

        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # get the dataset to plot
        day_index = self.dataset_day_list.index(day)
        df_index = self.df_index_list[day_index][columns]
        df_index_gini = df_index[df_index["gini_threshold"] == gini_thr]

        data_avg_list = []
        data_std_list = []
        for metric in metrics:
            # convert the float to int
            data_avg_tmp = np.mean(df_index_gini[metric].tolist()).round()
            data_std_tmp = np.std(df_index_gini[metric].tolist())
            data_avg_list.append(data_avg_tmp)
            data_std_list.append(data_std_tmp)

        # convert to numpy array
        data_avg_arr = np.array(data_avg_list)
        data_std_arr = np.array(data_std_list)

        ############################## plot ##############################
        # Set width of bar
        barWidth = 0.35

        # Set position of bars on x-axis
        x_positions = np.arange(4)

        to_false_avg_list = data_avg_arr[np.arange(0, len(data_avg_arr), 2)]
        to_false_std_list = data_std_arr[np.arange(0, len(data_std_arr), 2)]
        to_true_avg_list = data_avg_arr[np.arange(0, len(data_avg_arr), 2) + 1]
        to_true_std_list = data_std_arr[np.arange(0, len(data_std_arr), 2) + 1]

        plt.bar(x_positions - barWidth/2, to_false_avg_list,
                width=barWidth, label="Classified Incorrectly")
        plt.errorbar(x_positions - barWidth/2, to_false_avg_list,
                     yerr=to_false_std_list, fmt='none', ecolor='black', capsize=5)
        plt.bar(x_positions + barWidth/2, to_true_avg_list,
                width=barWidth, label="Classified Correctly")
        plt.errorbar(x_positions + barWidth/2, to_true_avg_list,
                     yerr=to_true_std_list, fmt='none', ecolor='black', capsize=5)

        # add number on top of each bar
        for i, pos in enumerate(x_positions):
            plt.text(pos - barWidth,
                     to_false_avg_list[i], int(to_false_avg_list[i]))
            plt.text(pos, to_true_avg_list[i], int(to_true_avg_list[i]))

        plt.xticks(x_positions, ["FN", "FP", "TN", "TP"])
        plt.xlabel("Classified Result in Switch")
        plt.ylabel("Number of Flows Classified in Controller")
        plt.legend(loc="best")

        # save figure
        fig_name = f"classification_distribution_{day}_{gini_thr}_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_reduction_fn_fp(self, gini_thr):
        """Plot the classification distribution of the given day and gini threshold.

        """
        # set the metric to plot
        metrics = ["fn_to_controller",
                   "fp_to_controller",
                   "tn_to_controller",
                   "tp_to_controller",
                   "flows_to_controller_sum",
                   "fn_to_fn_controller",
                   "fn_to_tp_controller",
                   "fp_to_fp_controller",
                   "fp_to_tn_controller",
                   "tn_to_fp_controller",
                   "tn_to_tn_controller",
                   "tp_to_fn_controller",
                   "tp_to_tp_controller"]

        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average values of classification distribution
        data_reduction_day_list = []

        for i, day in enumerate(self.dataset_day_list):
            # extract data with the given gini threshold
            df_index = self.df_index_list[i][columns]
            df_index_gini = df_index[df_index["gini_threshold"] == gini_thr]

            data_avg_dict = {}
            # extract mean values for each metric
            for metric in metrics:
                data_avg_dict[metric] = np.mean(df_index_gini[metric].tolist())

            # compute the reduction of fn and fp
            # fn_per = data_avg_dict["fn_to_controller"] / \
            #     data_avg_dict["flows_to_controller_sum"]
            # fp_per = data_avg_dict["fp_to_controller"] / \
            #     data_avg_dict["flows_to_controller_sum"]

            # fn_reduction = fn_per * \
            #     (data_avg_dict["fn_to_tp_controller"] /
            #      data_avg_dict["fn_to_controller"])
            # fp_reduction = fp_per * \
            #     (data_avg_dict["fp_to_tn_controller"] /
            #      data_avg_dict["fp_to_controller"])

            reduction = (FN / SUM) * (FN2TP / FN)

            print(fn_reduction)
            fn_reduction = data_avg_dict["fn_to_tp_controller"] / \
                data_avg_dict["flows_to_controller_sum"]

            sum_reduction = fn_reduction + fp_reduction
            data_reduction_day_list.append(sum_reduction)

        # ############################## plot ##############################
        bar_width = 0.3
        x_pos = range(3)

        plt.bar(x_pos, data_reduction_day_list, width=bar_width)
        plt.ylim(0, 0.5)
        plt.xticks(x_pos, ["Brute Force", "DoS/DDoS", "Botnet"])

        # ############################## plot ##############################
        # fig, axs = plt.subplots(1, 3, figsize=(
        #     12, 4), sharey=True, sharex=True)
        # fig.tight_layout()

        # # Set width of bar
        # barWidth = 0.35

        # # Set position of bars on x-axis
        # x_positions = np.arange(4)

        # for i, day in enumerate(self.dataset_day_list):
        #     to_false_avg_list = data_avg_day_dict[day][np.arange(
        #         0, len(data_avg_day_dict[day]), 2)]
        #     to_false_std_list = data_std_day_dict[day][np.arange(
        #         0, len(data_std_day_dict[day]), 2)]
        #     to_true_avg_list = data_avg_day_dict[day][np.arange(
        #         0, len(data_avg_day_dict[day]), 2) + 1]
        #     to_true_std_list = data_std_day_dict[day][np.arange(
        #         0, len(data_std_day_dict[day]), 2) + 1]

        #     axs[i].bar(x_positions + barWidth/2, to_true_avg_list,
        #                width=barWidth, label="Reclassified Correctly")
        #     axs[i].errorbar(x_positions + barWidth/2, to_true_avg_list,
        #                     yerr=to_true_std_list, fmt='none', ecolor='black', capsize=5)
        #     axs[i].bar(x_positions - barWidth/2, to_false_avg_list,
        #                width=barWidth, label="Reclassified Incorrectly")
        #     axs[i].errorbar(x_positions - barWidth/2, to_false_avg_list,
        #                     yerr=to_false_std_list, fmt='none', ecolor='black', capsize=5)

        #     axs[i].set_xticks(x_positions, ["FN", "FP", "TN", "TP"],
        #                       fontsize=self.fontsize_ticks_subplot)
        #     axs[i].set_xlabel("Classified Result in DP-IDS",
        #                       fontsize=self.fontsize_label_subplot)
        #     axs[i].legend(fontsize=self.fontsize_legend_subplot)

        #     # add number on top of each bar
        #     for j, pos in enumerate(x_positions):
        #         if j == 1:
        #             x_pos_diff = barWidth
        #         elif j == 3:
        #             x_pos_diff = barWidth * 0.7
        #         else:
        #             x_pos_diff = barWidth * 0.5

        #         axs[i].text(pos - x_pos_diff, to_false_avg_list[j] +
        #                     120, int(to_false_avg_list[j]), ha='center', va='center', fontsize=self.fontsize_text_subplot)
        #         axs[i].text(pos + x_pos_diff, to_true_avg_list[j] +
        #                     120, int(to_true_avg_list[j]), ha='center', va='center', fontsize=self.fontsize_text_subplot)

        # axs[0].set_ylabel("Number of Sub-flows Classified in CP-IDS",
        #                   fontsize=14)
        # axs[0].set_ylim([0, 3300])
        # axs[0].yaxis.set_tick_params(labelsize=self.fontsize_ticks_subplot)

        # # set titles for each subplot
        # axs[0].set_title("(A) Brute Force",
        #                  fontsize=self.fontsize_title_subplot)
        # axs[1].set_title("(B) DoS/DDoS", fontsize=self.fontsize_title_subplot)
        # axs[2].set_title("(C) Botnet", fontsize=self.fontsize_title_subplot)

        # # save figure
        # fig_name = f"classification_distribution_{gini_thr}_bar.png"
        # fig_path = self.fig_save_base_path + "figs/" + fig_name
        # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        # plt.show()

    def plot_classification_distribution_controller_day(self, gini_thr):
        """Plot the classification distribution of the given day and gini threshold.

        """
        # set the metric to plot
        metrics = ["fn_to_fn_controller",
                   "fn_to_tp_controller",
                   "fp_to_fp_controller",
                   "fp_to_tn_controller",
                   "tn_to_fp_controller",
                   "tn_to_tn_controller",
                   "tp_to_fn_controller",
                   "tp_to_tp_controller"]

        columns = ["gini_threshold"] + metrics

        ############################## compute the data to plot ##############################
        # average values of classification distribution
        data_avg_day_dict = {}
        # standard deviation of classification distribution
        data_std_day_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            # extract data with the given gini threshold
            df_index = self.df_index_list[i][columns]
            df_index_gini = df_index[df_index["gini_threshold"] == gini_thr]

            data_avg_list = []
            data_std_list = []
            # extract values for each metric and save them into one list
            for metric in metrics:
                # convert the float to int
                data_avg_tmp = np.mean(df_index_gini[metric].tolist()).round()
                data_std_tmp = np.std(df_index_gini[metric].tolist())
                data_avg_list.append(data_avg_tmp)
                data_std_list.append(data_std_tmp)

            # save the avg and std for each day into the dictionary
            data_avg_day_dict[day] = np.array(data_avg_list)
            data_std_day_dict[day] = np.array(data_std_list)

        ############################## plot ##############################
        fig, axs = plt.subplots(1, 3, figsize=(
            12, 4), sharey=True, sharex=True)
        fig.tight_layout()

        # Set width of bar
        barWidth = 0.35

        # Set position of bars on x-axis
        x_positions = np.arange(4)

        for i, day in enumerate(self.dataset_day_list):
            to_false_avg_list = data_avg_day_dict[day][np.arange(
                0, len(data_avg_day_dict[day]), 2)]
            to_false_std_list = data_std_day_dict[day][np.arange(
                0, len(data_std_day_dict[day]), 2)]
            to_true_avg_list = data_avg_day_dict[day][np.arange(
                0, len(data_avg_day_dict[day]), 2) + 1]
            to_true_std_list = data_std_day_dict[day][np.arange(
                0, len(data_std_day_dict[day]), 2) + 1]

            axs[i].bar(x_positions + barWidth/2, to_true_avg_list,
                       width=barWidth, label="Reclassified Correctly")
            axs[i].errorbar(x_positions + barWidth/2, to_true_avg_list,
                            yerr=to_true_std_list, fmt='none', ecolor='black', capsize=5)
            axs[i].bar(x_positions - barWidth/2, to_false_avg_list,
                       width=barWidth, label="Reclassified Incorrectly")
            axs[i].errorbar(x_positions - barWidth/2, to_false_avg_list,
                            yerr=to_false_std_list, fmt='none', ecolor='black', capsize=5)

            axs[i].set_xticks(x_positions, ["FN", "FP", "TN", "TP"],
                              fontsize=self.fontsize_ticks_subplot)
            axs[i].set_xlabel("Classified Result in DP-IDS",
                              fontsize=self.fontsize_label_subplot)
            axs[i].legend(fontsize=self.fontsize_legend_subplot)

            # add number on top of each bar
            for j, pos in enumerate(x_positions):
                if j == 1:
                    x_pos_diff = barWidth
                elif j == 3:
                    x_pos_diff = barWidth * 0.7
                else:
                    x_pos_diff = barWidth * 0.5

                axs[i].text(pos - x_pos_diff, to_false_avg_list[j] +
                            120, int(to_false_avg_list[j]), ha='center', va='center', fontsize=self.fontsize_text_subplot)
                axs[i].text(pos + x_pos_diff, to_true_avg_list[j] +
                            120, int(to_true_avg_list[j]), ha='center', va='center', fontsize=self.fontsize_text_subplot)

        axs[0].set_ylabel("Number of Sub-flows Classified in CP-IDS",
                          fontsize=14)
        axs[0].set_ylim([0, 3300])
        axs[0].yaxis.set_tick_params(labelsize=self.fontsize_ticks_subplot)

        # set titles for each subplot
        axs[0].set_title("(A) Brute Force",
                         fontsize=self.fontsize_title_subplot)
        axs[1].set_title("(B) DoS/DDoS", fontsize=self.fontsize_title_subplot)
        axs[2].set_title("(C) Botnet", fontsize=self.fontsize_title_subplot)

        # save figure
        fig_name = f"classification_distribution_{gini_thr}_bar.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_gini_to_classification_distribution_controller(self, matrix_class, ratio_form=False, stacked=False, log_plot=False):
        """Plot the distribution of confusion matrix classified in controller according to
           the classified class in switch for different gini threshold value.

        Args:
            matrix_class: fn, fp, tn, tp
                Predicted class in switch
            ratio_form: True, False, default: False
                Enable plotting percentage.
            stacked: True, False, default: False
                Enable plotting stacked bar chart.
        """
        # set the metric to plot
        if matrix_class in ["fn", "tp"]:
            metric_name_list = [
                f"{matrix_class}_to_fn_controller", f"{matrix_class}_to_tp_controller"]
            # labels of each plot
            labels = ["fn", "tp"]
            # colors of each plot
            color_list = [self._COLOR_DICT["fn_color"],
                          self._COLOR_DICT["tp_color"]]
            # get the column name of to_controller according to the given matrix class
            to_controller_column_name = f"{matrix_class}_to_controller"
        elif matrix_class in ["fp", "tn"]:
            metric_name_list = [
                f"{matrix_class}_to_fp_controller", f"{matrix_class}_to_tn_controller"]
            # labels of each plot
            labels = ["fp", "tn"]
            # colors of each plot
            color_list = [self._COLOR_DICT["fp_color"],
                          self._COLOR_DICT["tn_color"]]
            # get the column name of to_controller according to the given matrix class
            to_controller_column_name = f"{matrix_class}_to_controller"
        else:
            raise ValueError("The given plane name is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metric_name_list

        # plot each day
        for i, day in enumerate(self.dataset_day_list):
            # get the dataframe of this day
            df_tmp = self.df_final_list[i]
            # dataframe to plot
            if ratio_form:
                # compute the percentage of fn, fp, tn and tp
                df_plot = df_tmp[metric_name_list[:4]].apply(
                    lambda x: x / df_tmp[to_controller_column_name], axis=0)
                # insert the gini_threshold column
                df_plot[columns[0]] = df_tmp[columns[0]]
                y_label_name = "Percentage of Flows"
            else:
                df_plot = df_tmp[columns]
                y_label_name = "Number of Flows"

            df_plot.plot(x=columns[0], kind="bar", stacked=stacked, logy=log_plot, rot=0, style='-o', color=color_list,
                         xlabel="Gini Threshold", ylabel=y_label_name)
            # if plot the percentage, set the range of y axis
            if ratio_form:
                plt.ylim(0, 1)
            plt.legend(labels)
            # save figure

            if ratio_form:
                fig_name = f"{day}_gini_threshold_to_classification_distribution_{matrix_class}_ratio"
            else:
                fig_name = f"{day}_gini_threshold_to_classification_distribution_{matrix_class}_number"
            if stacked:
                fig_name = fig_name + f"_stacked_bar.png"
            else:
                fig_name = fig_name + f"_bar.png"

            fig_path = self.fig_save_base_path + \
                f"/{day}/figs_lite/" + fig_name
            # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_classification_time(self):
        """Plot the classification time in switch and controller.
        """
        # set the metric to plot
        metric_name_list = ["classification_time_mean_p4",
                            "classification_time_mean_controller"]
        # colors of each plot
        color_list = [self._COLOR_DICT["time_p4_color"],
                      self._COLOR_DICT["time_controller_color"]]
        # labels of each plot
        labels = ["classification in switch", "classification with controller"]
        y_label_name = "time in second"

        # dictionary to save the average values of classification time in switch and controller for each day
        time_dict = {
            "classification_time_p4_avg": [],
            "classification_time_controller_avg": []
        }

        # get the average value of expired flows and total flows
        for i, day in enumerate(self.dataset_day_list):
            # get the dataset of the given columns
            df_tmp = self.df_final_list[i][metric_name_list]
            # compute the mean of each column
            df_tmp_mean = df_tmp.mean(axis=0)
            time_dict["classification_time_p4_avg"].append(
                df_tmp_mean[metric_name_list[0]])
            time_dict["classification_time_controller_avg"].append(
                df_tmp_mean[metric_name_list[1]])

        df_plot = pd.DataFrame(
            time_dict, index=["Tuesday", "Wednesday", "Thursday", "Friday"])
        df_plot.plot(kind="bar", style='-o', color=color_list,
                     xlabel="dataset", ylabel=y_label_name)
        plt.legend(labels)
        # save figure
        fig_name = "classification_time_each_day.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        # plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_expired_flows_and_hash_collision(self, plot_log=False):
        """Plot the number of expired flows, flows with hash collision and total flows for each day.

        """
        # set the metric to plot
        metrics = ["flow_expired", "flow_total"]

        ############################## compute the data to plot ##############################
        # average number of expired flow and total flow for each day
        flow_expired_avg_day_list = []
        flow_total_avg_day_list = []
        flow_hash_collision_avg_day_list = []

        # standard deviation of number of expired flow and total flow for each day
        flow_expired_std_day_list = []
        flow_total_std_day_list = []
        flow_hash_collision_std_day_list = []

        for i, day in enumerate(self.dataset_day_list):
            df_index = self.df_index_list[i][metrics]
            flow_expired_avg_tmp = np.mean(df_index[metrics[0]].tolist())
            flow_total_avg_tmp = np.mean(df_index[metrics[1]].tolist())
            flow_hash_collision_avg_tmp = np.mean(
                self.df_final_list[i]["hash_collision_flow_number"].tolist())

            flow_expired_std_tmp = np.std(df_index[metrics[0]].tolist())
            flow_total_std_tmp = np.std(df_index[metrics[1]].tolist())
            flow_hash_collision_std_tmp = np.std(
                self.df_final_list[i]["hash_collision_flow_number"].tolist())

            flow_expired_avg_day_list.append(flow_expired_avg_tmp)
            flow_total_avg_day_list.append(flow_total_avg_tmp)
            flow_hash_collision_avg_day_list.append(
                flow_hash_collision_avg_tmp)

            flow_expired_std_day_list.append(flow_expired_std_tmp)
            flow_total_std_day_list.append(flow_total_std_tmp)
            flow_hash_collision_std_day_list.append(
                flow_hash_collision_std_tmp)

        ############################## plot ##############################
        fig = plt.figure(figsize=self.figsize_single)
        # Set width of bar
        barWidth = 0.25

        # Set position of bars on x-axis
        r1 = np.arange(len(self.dataset_day_list))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]

        plt.bar(r1, flow_hash_collision_avg_day_list,
                width=barWidth, label="Sub-flow with Hash Collision")
        plt.errorbar(r1, flow_hash_collision_avg_day_list,
                     yerr=flow_hash_collision_std_day_list, fmt='none', ecolor='black', capsize=5)
        plt.bar(r2, flow_expired_avg_day_list,
                width=barWidth, label="Sub-flow Expired")
        plt.errorbar(r2, flow_expired_avg_day_list,
                     yerr=flow_expired_std_day_list, fmt='none', ecolor='black', capsize=5)
        plt.bar(r3, flow_total_avg_day_list, width=barWidth,
                label="Sub-flow Extracted")
        plt.errorbar(r3, flow_total_avg_day_list, yerr=flow_total_std_day_list,
                     fmt='none', ecolor='black', capsize=5)

        if plot_log:
            # add number on top of each bar
            for i, pos in enumerate(r1):
                plt.text(r1[i], flow_hash_collision_avg_day_list[i] +
                         flow_hash_collision_avg_day_list[i] / 10, int(flow_hash_collision_avg_day_list[i]), ha='center', va='center')
                plt.text(r2[i], flow_expired_avg_day_list[i] +
                         flow_expired_avg_day_list[i] / 10, int(flow_expired_avg_day_list[i]), ha='center', va='center')
                plt.text(r3[i], flow_total_avg_day_list[i] +
                         flow_total_avg_day_list[i] / 10, int(flow_total_avg_day_list[i]), ha='center', va='center')
            plt.yscale("log")
            plt.ylabel("Number of Sub-flows (log scale)",
                       fontsize=self.fontsize_label)
            fig_name = "expired_and_hash_collision_flows_log_bar.png"
        else:
            # add number on top of each bar
            x_pos_diff = barWidth * 0.15
            y_pos_diff = 10000
            for i, pos in enumerate(r1):
                plt.text(r1[i] - x_pos_diff, flow_hash_collision_avg_day_list[i] +
                         y_pos_diff, int(flow_hash_collision_avg_day_list[i]), ha='center', va='center')
                plt.text(r2[i] - x_pos_diff, flow_expired_avg_day_list[i] +
                         y_pos_diff, int(flow_expired_avg_day_list[i]), ha='center', va='center')
                plt.text(r3[i] - x_pos_diff, flow_total_avg_day_list[i] +
                         y_pos_diff, int(flow_total_avg_day_list[i]), ha='center', va='center')
            plt.ylabel("Number of Sub-flows", fontsize=self.fontsize_label)
            plt.ylim((0, 450000))
            fig_name = "expired_and_hash_collision_flows_bar.png"

        xticks_name_list = ["Brute Force", "DoS/DDoS", "Botnet"]

        plt.xticks(r2, xticks_name_list)
        plt.xlabel("Attack Type", fontsize=self.fontsize_label)
        plt.legend(loc="best")

        # save figure
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def plot_avg_std_flow_real(self, plot_log=False):
        """Get the average number and standard deviation of real benign flows or attacks.

        """
        # set the metric to plot
        metrics = ["flow_benign_real_sum", "flow_attack_real_sum"]

        ############################## compute the data  ##############################
        # average number of benign and attack for each day
        benign_real_avg_list = []
        attack_real_avg_list = []
        total_real_avg_list = []

        # standard deviation of benign and attack for each day
        benign_real_std_list = []
        attack_real_std_list = []
        total_real_std_list = []

        for i, day in enumerate(self.dataset_day_list):
            df_index = self.df_index_list[i][metrics]
            benign_real_arr = np.array(df_index[metrics[0]].tolist())
            attack_real_arr = np.array(df_index[metrics[1]].tolist())
            total_real_arr = benign_real_arr + attack_real_arr

            benign_real_avg_tmp = np.mean(benign_real_arr).round()
            attack_real_avg_tmp = np.mean(attack_real_arr).round()
            total_real_avg_tmp = np.mean(total_real_arr).round()

            benign_real_std_tmp = np.std(benign_real_arr)
            attack_real_std_tmp = np.std(attack_real_arr)
            total_real_std_tmp = np.std(total_real_arr)

            benign_real_avg_list.append(benign_real_avg_tmp)
            attack_real_avg_list.append(attack_real_avg_tmp)
            total_real_avg_list.append(total_real_avg_tmp)

            benign_real_std_list.append(benign_real_std_tmp)
            attack_real_std_list.append(attack_real_std_tmp)
            total_real_std_list.append(total_real_std_tmp)

        ############################## plot ##############################
        # Set width of bar
        barWidth = 0.25

        # Set position of bars on x-axis
        r1 = np.arange(len(self.dataset_day_list))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]

        plt.bar(r1, attack_real_avg_list,
                width=barWidth, label="Attack Flow")
        plt.errorbar(r1, attack_real_avg_list,
                     yerr=attack_real_std_list, fmt='none', ecolor='black', capsize=5)
        plt.bar(r2, benign_real_avg_list,
                width=barWidth, label="Benign Flow")
        plt.errorbar(r2, benign_real_avg_list,
                     yerr=benign_real_std_list, fmt='none', ecolor='black', capsize=5)
        plt.bar(r3, total_real_avg_list, width=barWidth,
                label="Flow with Minimum 8 Packets")
        plt.errorbar(r3, total_real_avg_list, yerr=total_real_std_list,
                     fmt='none', ecolor='black', capsize=5)

        if plot_log:
            # add number on top of each bar
            for i, pos in enumerate(r1):
                plt.text(r1[i] - barWidth/2, attack_real_avg_list[i] +
                         attack_real_avg_list[i] / 10, int(attack_real_avg_list[i]))
                plt.text(r2[i] - barWidth/2, benign_real_avg_list[i] +
                         benign_real_avg_list[i] / 10, int(benign_real_avg_list[i]))
                plt.text(r3[i] - barWidth/2, total_real_avg_list[i] +
                         total_real_avg_list[i] / 10, int(total_real_avg_list[i]))
            plt.yscale("log")
            plt.ylabel("Number of Flows (log scale)")
            fig_name = "real_benign_attack_log_bar.png"
        else:
            # add number on top of each bar
            x_pos_diff_factor = 0.7
            for i, pos in enumerate(r1):
                plt.text(r1[i], attack_real_avg_list[i] +
                         3000, int(attack_real_avg_list[i]), ha='center', va='center')
                plt.text(r2[i], benign_real_avg_list[i] +
                         3000, int(benign_real_avg_list[i]), ha='center', va='center')
                plt.text(r3[i], total_real_avg_list[i] +
                         3000, int(total_real_avg_list[i]), ha='center', va='center')
            plt.ylabel("Number of Flows")
            plt.ylim([0, 160000])
            fig_name = "real_benign_attack_bar.png"

        xticks_name_list = ["Brute Force", "DoS/DDoS", "Botnet"]

        plt.xticks(r2, xticks_name_list)
        plt.xlabel("Attack Type")
        plt.legend(loc="best")

        # save figure
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
        plt.show()

    def get_classification_time_avg_std(self):
        """Get the mean and standard deviation of classification time in swich and witch controller.

        """
        # set the metric to plot
        metrics = ["classification_time_mean_p4",
                   "classification_time_mean_controller"]

        columns = ["gini_threshold"] + metrics

        ############################## compute the data  ##############################
        classification_time_p4_avg_day_dict = {}
        classification_time_controller_avg_day_dict = {}

        classification_time_p4_std_day_dict = {}
        classification_time_controller_std_day_dict = {}

        for i, day in enumerate(self.dataset_day_list):
            df_index = self.df_index_list[i][columns]
            classification_time_p4_avg_list_tmp = []
            classification_time_controller_avg_list_tmp = []

            classification_time_p4_std_list_tmp = []
            classification_time_controller_std_list_tmp = []

            for gini_threshold_val in self._GINI_THRESHOLD_LIST:
                df_index_gini = df_index[df_index["gini_threshold"]
                                         == gini_threshold_val]

                classification_time_p4_avg_tmp = np.mean(
                    df_index_gini[metrics[0]].tolist())
                classification_time_controller_avg_tmp = np.mean(
                    df_index_gini[metrics[1]].tolist())

                classification_time_p4_std_tmp = np.std(
                    df_index_gini[metrics[0]].tolist())
                classification_time_controller_std_tmp = np.std(
                    df_index_gini[metrics[1]].tolist())

                classification_time_p4_avg_list_tmp.append(
                    classification_time_p4_avg_tmp)
                classification_time_controller_avg_list_tmp.append(
                    classification_time_controller_avg_tmp)

                classification_time_p4_std_list_tmp.append(
                    classification_time_p4_std_tmp)
                classification_time_controller_std_list_tmp.append(
                    classification_time_controller_std_tmp)

            classification_time_p4_avg_day_dict[day] = classification_time_p4_avg_list_tmp
            classification_time_controller_avg_day_dict[day] = classification_time_controller_avg_list_tmp

            classification_time_p4_std_day_dict[day] = classification_time_p4_std_list_tmp
            classification_time_controller_std_day_dict[day] = classification_time_controller_std_list_tmp

        return (classification_time_p4_avg_day_dict, classification_time_controller_avg_day_dict, classification_time_p4_std_day_dict, classification_time_controller_std_day_dict)
