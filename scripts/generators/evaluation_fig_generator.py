from matplotlib import pyplot as plt
import pandas as pd
import math


class EvaluationFigureGenerator():
    """Plot evaluation figures.

    Attributes:
        file_path_list: .csv file
            List of paths of evaluation files saved in .csv format.
        fig_save_base_path_list:
            List of base paths to save figures.
    """

    _COLOR_DICT = {
        "tuesday_color": "tab:red",
        "wednesday_color": "tab:green",
        "thursday_color": "tab:orange",
        "friday_color": "tab:blue",

        "pre_color": "tab:blue",
        "re_color": "tab:orange",
        "f1_color": "tab:red",

        "fn_color": "tab:red",
        "fp_color": "tab:orange",
        "tn_color": "tab:green",
        "tp_color": "tab:blue",

        "time_p4_color": "tab:green",
        "time_controller_color": "tab:blue",

        "baseline_color": "grey",
        "sum_color": "tab:purple"
    }

    _DATASET_DAY_LIST = ["tuesday", "wednesday", "thursday", "friday"]

    def __init__(self, file_path_list, fig_save_base_path) -> None:
        self.fig_save_base_path = fig_save_base_path
        self.df_list = []
        self.fig_dpi = 300
        for i, day in enumerate(self._DATASET_DAY_LIST):
            df_tmp = pd.read_csv(file_path_list[i])
            self.df_list.append(df_tmp)

    def show_file(self):
        print(self.df)

    def show_column(self, column_name):
        print(self.df[column_name])

    def plot_gini_to_macro_avg_sum(self, metric_type, plot_kind):
        """Plot macro-average values for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.

        Args:
            metric_type: precision, recall, f1
                The type of metric.
            plot_kind: "line", "bar"
                The kind of plotted figure.
        """
        # set the metric to plot
        if metric_type == "precision":
            macro_avg_metric = "macro_avg_pre_sum"
            macro_avg_baseline = "macro_avg_pre_sum_wo_controller"
            label_plot = "macro-average precision"
        elif metric_type == "recall":
            macro_avg_metric = "macro_avg_re_sum"
            macro_avg_baseline = "macro_avg_re_sum_wo_controller"
            label_plot = "macro-average recall"
        elif metric_type == "f1":
            macro_avg_metric = "macro_avg_f1_sum"
            macro_avg_baseline = "macro_avg_f1_sum_wo_controller"
            label_plot = "macro-average f1 score"
        else:
            raise ValueError("The given metric name is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold", macro_avg_metric, macro_avg_baseline]

        # labels of each plot
        labels = [label_plot, "baseline"]

        # plot each day
        for i, day in enumerate(self._DATASET_DAY_LIST):
            color_list = [
                self._COLOR_DICT[f"{day}_color"], self._COLOR_DICT["baseline_color"]]
            # dataframe to plot
            df_plot = self.df_list[i][columns]
            df_plot.plot(x=columns[0], kind=plot_kind, style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel="macro average value")
            plt.legend(labels)

            # set the ylim to the range (min_macro_avg - m_distance, max_macro_avg + m_distance)
            m_distance = 0.01
            ylim_min = max(min(df_plot[macro_avg_metric].min(
            ), df_plot[macro_avg_baseline].min()) - m_distance, 0)
            ylim_max = min(max(df_plot[macro_avg_metric].max(
            ), df_plot[macro_avg_baseline].max()) + m_distance, 1)
            plt.ylim(ylim_min, ylim_max)
            # save figure
            fig_name = f"{day}_gini_threshold_to_" + \
                macro_avg_metric + f"_{plot_kind}.png"
            fig_path = self.fig_save_base_path + f"/{day}/figs/" + fig_name
            plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_macro_avg_p4(self, plot_kind):
        """Plot macro-average values for precision, recall and f1, in terms of the changes of gini value threshold.

        Flows are classified in P4 switch.

        Args:
            plot_kind: "line", "bar"
                The kind of plotted figure.
        """
        # column names shoud be extracted in df
        columns = ["gini_threshold", "macro_avg_pre_p4",
                   "macro_avg_re_p4", "macro_avg_f1_p4"]

        # labels of each plot
        labels = ["macro-average precision",
                  "macro-average recall", "macro-average f1 score"]

        # plot each day
        for i, day in enumerate(self._DATASET_DAY_LIST):
            color_list = [
                self._COLOR_DICT["pre_color"], self._COLOR_DICT["re_color"], self._COLOR_DICT["f1_color"]]
            # dataframe to plot
            df_plot = self.df_list[i][columns]
            df_plot.plot(x=columns[0], kind=plot_kind, style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel="macro average value")
            plt.legend(labels)

            # set the ylim to the range (min_macro_avg - m_distance, max_macro_avg + m_distance)
            m_distance = 0.05
            ylim_min = max(min(df_plot[columns[1]].min(), df_plot[columns[2]].min(
            ), df_plot[columns[3]].min()) - m_distance, 0)
            ylim_max = min(max(df_plot[columns[1]].max(), df_plot[columns[2]].max(
            ), df_plot[columns[3]].max()) + m_distance, 1)
            plt.ylim(ylim_min, ylim_max)
            # save figure
            fig_name = f"{day}_gini_threshold_to_macro_avg_p4" + \
                f"_{plot_kind}.png"
            fig_path = self.fig_save_base_path + f"/{day}/figs/" + fig_name
            plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_metric_sum(self, metric_type, flow_type, plot_kind):
        """Plot values of benign and attack for different metrics in terms of the changes of gini value threshold.

        Flows are classified in P4 switch and controller.

        Args:
            metric_type: precision, recall, f1
                The type of metric
            flow_type: benign, attack
                The type of flows
            plot_kind: line, bar
                The kind of plotted figure.
        """
        # set the metric to plot
        # precision
        if metric_type == "precision":
            if flow_type == "benign":
                metric_name = "benign_pre_sum"
                baseline_name = "benign_pre_sum_wo_controller"
                label_plot = "precision of benign flows"
            elif flow_type == "attack":
                metric_name = "attack_pre_sum"
                baseline_name = "attack_pre_sum_wo_controller"
                label_plot = "precision of attack flows"
            else:
                raise ValueError("The given flow type is illegal.")
        # recall
        elif metric_type == "recall":
            if flow_type == "benign":
                metric_name = "benign_re_sum"
                baseline_name = "benign_re_sum_wo_controller"
                label_plot = "recall of benign flows"
            elif flow_type == "attack":
                metric_name = "attack_re_sum"
                baseline_name = "attack_re_sum_wo_controller"
                label_plot = "recall of attack flows"
            else:
                raise ValueError("The given flow type is illegal.")
        # f1 score
        elif metric_type == "f1":
            if flow_type == "benign":
                metric_name = "benign_f1_sum"
                baseline_name = "benign_f1_sum_wo_controller"
                label_plot = "f1 score of benign flows"
            elif flow_type == "attack":
                metric_name = "attack_f1_sum"
                baseline_name = "attack_f1_sum_wo_controller"
                label_plot = "f1 score of attack flows"
            else:
                raise ValueError("The given flow type is illegal.")
        else:
            raise ValueError("The given metric name is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold", metric_name, baseline_name]

        # labels of each plot
        labels = [label_plot, "baseline"]

        # plot each day
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # convert index to bit string, used to set axes of sub figure
            # bit_str = "{0:02b}".format(i)
            # x_axis = int(bit_str[0])
            # y_axis = int(bit_str[1])
            color_list = [
                self._COLOR_DICT[f"{day}_color"], self._COLOR_DICT["baseline_color"]]
            # dataframe to plot
            df_plot = self.df_list[i][columns]
            df_plot.plot(x=columns[0], kind=plot_kind, style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel="metric value")
            plt.legend(labels)

            # set the ylim to the range (min_macro_avg - m_distance, max_macro_avg + m_distance)
            m_distance = 0.01
            ylim_min = max(min(df_plot[metric_name].min(
            ), df_plot[baseline_name].min()) - m_distance, 0)
            ylim_max = min(max(df_plot[metric_name].max(
            ), df_plot[baseline_name].max()) + m_distance, 1)
            plt.ylim(ylim_min, ylim_max)
            # save figure
            fig_name = f"{day}_gini_threshold_to_" + \
                metric_name + f"_{plot_kind}.png"
            fig_path = self.fig_save_base_path + f"/{day}/figs/" + fig_name
            plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_confusion_matrix(self, plane, ratio_form=False, stacked=False):
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
        labels = ["fn", "fp", "tn", "tp", "sum"]
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
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataframe of this day
            df_tmp = self.df_list[i]
            # dataframe to plot
            if ratio_form:
                # compute the percentage of fn, fp, tn and tp
                df_plot = df_tmp[metric_name_list[:4]].apply(
                    lambda x: x / df_tmp[metric_name_list[len(metric_name_list) - 1]], axis=0)
                # insert the gini_threshold column
                df_plot[columns[0]] = df_tmp[columns[0]]
                y_label_name = "percentage of flows"
            else:
                if stacked:
                    df_plot = df_tmp[columns[:len(columns) - 1]]
                else:
                    df_plot = df_tmp[columns]
                y_label_name = "number of flows"

            df_plot.plot(x=columns[0], kind="bar", stacked=stacked, style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel=y_label_name)
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

            fig_path = self.fig_save_base_path + f"/{day}/figs/" + fig_name
            plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_gini_to_confusion_matrix_sum(self, matrix_class):
        """Plot the numbers of fn, fp, tn and tp classified in switch with controler and without controller 
           for different gini threshold value.

        Args:
            matrix_class: fn, fp, tn, tp
                Predicted class in confusion matrix.
        """
        # set the metric to plot
        confusion_matrix_class_list = ["fn", "fp", "tn", "tp"]
        if matrix_class in confusion_matrix_class_list:
            metric_name_list = [f"{matrix_class}_sum",
                                f"{matrix_class}_sum_wo_controller"]
            # labels of each plot
            labels = [f"{matrix_class} with controller",
                      f"{matrix_class} without controller"]
            # colors of each plot
            color_list = [
                self._COLOR_DICT[f"{matrix_class}_color"], self._COLOR_DICT["baseline_color"]]
        else:
            raise ValueError("The given plane name is illegal.")

        # column names shoud be extracted in df
        columns = ["gini_threshold"] + metric_name_list
        y_label_name = "number of flows"

        # plot each day
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataframe of this day with the given columns
            df_plot = self.df_list[i][columns]

            df_plot.plot(x=columns[0], kind="bar", style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel=y_label_name)
            plt.legend(labels)

    def plot_gini_to_classification_distribution_controller(self, matrix_class, ratio_form=False, stacked=False):
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
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataframe of this day
            df_tmp = self.df_list[i]
            # dataframe to plot
            if ratio_form:
                # compute the percentage of fn, fp, tn and tp
                df_plot = df_tmp[metric_name_list[:4]].apply(
                    lambda x: x / df_tmp[to_controller_column_name], axis=0)
                # insert the gini_threshold column
                df_plot[columns[0]] = df_tmp[columns[0]]
                y_label_name = "percentage of flows"
            else:
                df_plot = df_tmp[columns]
                y_label_name = "number of flows"

            df_plot.plot(x=columns[0], kind="bar", stacked=stacked, style='-o', color=color_list,
                         xlabel="gini value threshold", ylabel=y_label_name)
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

            fig_path = self.fig_save_base_path + f"/{day}/figs/" + fig_name
            plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

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

        # get the average value of expired flows and tatal flows
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataset of the given columns
            df_tmp = self.df_list[i][metric_name_list]
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
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_expired_flows(self):
        """Plot the number of expired flows and total flows for each day.
        """
        # set the metric to plot
        metric_name_list = ["flow_expired", "flow_total"]
        # colors of each plot
        color_list = [self._COLOR_DICT["sum_color"],
                      self._COLOR_DICT["baseline_color"]]
        # labels of each plot
        labels = ["expired flows", "total flows"]
        y_label_name = "number of flows"

        # dictionary to save the average values of expired flows and total flows for each day
        flow_dict = {
            "expired_flow_avg": [],
            "total_flow_avg": []
        }

        # get the average value of expired flows and tatal flows
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataset of the given columns
            df_tmp = self.df_list[i][metric_name_list]
            # compute the mean of each column
            df_tmp_mean = df_tmp.mean(axis=0).map(lambda x: round(x))
            flow_dict["expired_flow_avg"].append(
                df_tmp_mean[metric_name_list[0]])
            flow_dict["total_flow_avg"].append(
                df_tmp_mean[metric_name_list[1]])

        df_plot = pd.DataFrame(
            flow_dict, index=["Tuesday", "Wednesday", "Thursday", "Friday"])
        df_plot.plot(kind="bar", style='-o', color=color_list,
                     xlabel="dataset", ylabel=y_label_name)
        plt.legend(labels)
        # save figure
        fig_name = "expired_flows_each_day.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")

    def plot_hash_collision(self):
        """Plot the number of packets with hash collision for each day.
        """
        # set the metric to plot
        metric_name_list = [
            "hash_collision_packet_number", "packet_ipv4_total"]
        # colors of each plot
        color_list = [self._COLOR_DICT["sum_color"],
                      self._COLOR_DICT["baseline_color"]]
        # labels of each plot
        labels = ["packets with hash collision", "total packets"]
        y_label_name = "number of packets"

        # save the average values of expired flows and total flows for each day
        key_str = "collision_packet_avg"
        collision_packet_dict = {
            key_str: []
        }
        total_packets_list = []

        # get the average value of expired flows and tatal flows
        for i, day in enumerate(self._DATASET_DAY_LIST):
            # get the dataset of the given columns
            df_tmp = self.df_list[i][metric_name_list]
            # compute the mean of each column
            df_tmp_mean = df_tmp.mean(axis=0).map(lambda x: round(x))
            collision_packet_dict[key_str].append(
                df_tmp_mean[metric_name_list[0]])
            # text shown on top of each bar
            text_str = f"total packets:\n{df_tmp_mean[metric_name_list[1]]}"
            total_packets_list.append(text_str)

        df_plot = pd.DataFrame(collision_packet_dict, index=[
                               "Tuesday", "Wednesday", "Thursday", "Friday"])
        df_plot.plot(kind="bar", style='-o', color=color_list,
                     xlabel="dataset", ylabel=y_label_name)
        plt.legend(labels)
        # add text on top of each bar
        for x, y, text_str in zip(range(len(df_plot.index)), df_plot[key_str], total_packets_list):
            plt.text(x - 0.3, y + 50, text_str)
        # set the range of y axis to show the text completely
        ylim_max = df_plot[key_str].max() + 500
        plt.ylim(top=ylim_max)
        # save figure
        fig_name = "hash_collision_each_day.png"
        fig_path = self.fig_save_base_path + "figs/" + fig_name
        plt.savefig(fname=fig_path, dpi=self.fig_dpi, bbox_inches="tight")
