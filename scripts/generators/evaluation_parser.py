import pandas as pd
import numpy as np


class EvaluationPaser():

    # counter and resiger names in p4
    _confusion_matrix_sum_fn_str = 'flow_fn_sum_counter'
    _confusion_matrix_sum_fp_str = 'flow_fp_sum_counter'
    _confusion_matrix_sum_tn_str = 'flow_tn_sum_counter'
    _confusion_matrix_sum_tp_str = 'flow_tp_sum_counter'

    _confusion_matrix_p4_fn_str = 'flow_fn_p4_sum_counter'
    _confusion_matrix_p4_fp_str = 'flow_fp_p4_sum_counter'
    _confusion_matrix_p4_tn_str = 'flow_tn_p4_sum_counter'
    _confusion_matrix_p4_tp_str = 'flow_tp_p4_sum_counter'

    _confusion_matrix_to_controller_fn_str = 'flow_fn_to_controller_sum_counter'
    _confusion_matrix_to_controller_fp_str = 'flow_fp_to_controller_sum_counter'
    _confusion_matrix_to_controller_tn_str = 'flow_tn_to_controller_sum_counter'
    _confusion_matrix_to_controller_tp_str = 'flow_tp_to_controller_sum_counter'

    _confusion_matrix_controller_fn_str = 'flow_fn_controller_sum_counter'
    _confusion_matrix_controller_fp_str = 'flow_fp_controller_sum_counter'
    _confusion_matrix_controller_tn_str = 'flow_tn_controller_sum_counter'
    _confusion_matrix_controller_tp_str = 'flow_tp_controller_sum_counter'

    _confusion_matrix_to_controller_threshold_fn_str = 'flow_fn_controller_threshold_sum_counter'
    _confusion_matrix_to_controller_threshold_fp_str = 'flow_fp_controller_threshold_sum_counter'
    _confusion_matrix_to_controller_threshold_tn_str = 'flow_tn_controller_threshold_sum_counter'
    _confusion_matrix_to_controller_threshold_tp_str = 'flow_tp_controller_threshold_sum_counter'

    _confusion_matrix_to_controller_2_le_1_fn_str = 'flow_fn_controller_2_le_1_sum_counter'
    _confusion_matrix_to_controller_2_le_1_fp_str = 'flow_fp_controller_2_le_1_sum_counter'
    _confusion_matrix_to_controller_2_le_1_tn_str = 'flow_tn_controller_2_le_1_sum_counter'
    _confusion_matrix_to_controller_2_le_1_tp_str = 'flow_tp_controller_2_le_1_sum_counter'

    _fn_controller_classification_distribution_str = 'flow_fn_controller_classification_distribution_counter'
    _fp_controller_classification_distribution_str = 'flow_fp_controller_classification_distribution_counter'
    _tn_controller_classification_distribution_str = 'flow_tn_controller_classification_distribution_counter'
    _tp_controller_classification_distribution_str = 'flow_tp_controller_classification_distribution_counter'

    _classification_time_sum_p4_str = 'classification_time_p4_egress_register'
    _classification_time_sum_controller_str = 'classification_time_controller_register'

    _flow_sum_total_str = 'flow_total_counter'
    _flow_sum_benign_real_sum_str = 'flow_benign_real_sum_counter'
    _flow_sum_attack_real_sum_str = 'flow_attack_real_sum_counter'
    _flow_sum_predicted_p4_sum_str = 'flow_predicted_p4_sum_counter'
    _flow_sum_predicted_controller_sum_str = 'flow_predicted_controller_sum_counter'

    _packet_ipv4_total_str = 'packet_ipv4_total_counter'
    _flow_expired_str = 'flow_expired_counter'
    _hash_collision_packet_str = 'hash_collision_packet_counter'

    def __init__(self) -> None:
        self.confusion_matrix_sum_dict = {}
        self.confusion_matrix_sum_wo_controller_dict = {}
        self.confusion_matrix_p4_dict = {}
        self.confusion_matrix_to_controller_dict = {}
        self.confusion_matrix_controller_dict = {}

        self.confusion_matrix_to_controller_threshold_dict = {}
        self.confusion_matrix_to_controller_2_le_1_dict = {}

        self.fn_controller_classification_distribution_dict = {}
        self.fp_controller_classification_distribution_dict = {}
        self.tn_controller_classification_distribution_dict = {}
        self.tp_controller_classification_distribution_dict = {}

        self.classification_time_dict = {}
        self.flow_sum_dict = {}

        self.packet_ipv4_total_val = 0
        self.flow_expired_val = 0
        self.hash_collision_packet_val = 0

        self.metric_cal = MetricCalculator()

    def parse_file(self, file_path):
        """Parse the evaluation file (.txt)

        Args:
            file_path: Path of .txt file
        """
        # patterns to get the metric value from string
        counter_start_str = 'bytes, '
        counter_end_str = ' packets'
        register_start_str = 'register[0]= '

        with open(file_path, 'r') as file:
            line = file.readline()
            while (line):
                # get the metric value
                counter_start_index = line.find(counter_start_str)
                counter_end_index = line.find(counter_end_str)
                reigister_start_index = line.find(register_start_str)

                if ((counter_start_index != -1) and (counter_end_index != -1)):
                    metric_value = int(
                        line[counter_start_index + len(counter_start_str): counter_end_index])
                elif reigister_start_index != -1:
                    metric_value = int(line[reigister_start_index +
                                            len(register_start_str):].strip('\n'))
                else:
                    metric_value = -1

                ########################## parse the evaluation file ##########################
                # parse confusion_matrix_sum_dict
                if self._confusion_matrix_sum_fn_str in line:
                    self.confusion_matrix_sum_dict['fn_sum'] = metric_value
                elif self._confusion_matrix_sum_fp_str in line:
                    self.confusion_matrix_sum_dict['fp_sum'] = metric_value
                elif self._confusion_matrix_sum_tn_str in line:
                    self.confusion_matrix_sum_dict['tn_sum'] = metric_value
                elif self._confusion_matrix_sum_tp_str in line:
                    self.confusion_matrix_sum_dict['tp_sum'] = metric_value

                # parse confusion_matrix_p4_dict
                elif self._confusion_matrix_p4_fn_str in line:
                    self.confusion_matrix_p4_dict['fn_p4'] = metric_value
                elif self._confusion_matrix_p4_fp_str in line:
                    self.confusion_matrix_p4_dict['fp_p4'] = metric_value
                elif self._confusion_matrix_p4_tn_str in line:
                    self.confusion_matrix_p4_dict['tn_p4'] = metric_value
                elif self._confusion_matrix_p4_tp_str in line:
                    self.confusion_matrix_p4_dict['tp_p4'] = metric_value

                # parse confusion_matrix_to_controller_dict
                elif self._confusion_matrix_to_controller_fn_str in line:
                    self.confusion_matrix_to_controller_dict['fn_to_controller'] = metric_value
                elif self._confusion_matrix_to_controller_fp_str in line:
                    self.confusion_matrix_to_controller_dict['fp_to_controller'] = metric_value
                elif self._confusion_matrix_to_controller_tn_str in line:
                    self.confusion_matrix_to_controller_dict['tn_to_controller'] = metric_value
                elif self._confusion_matrix_to_controller_tp_str in line:
                    self.confusion_matrix_to_controller_dict['tp_to_controller'] = metric_value

                # parse confusion_matrix_controller_dict
                elif self._confusion_matrix_controller_fn_str in line:
                    self.confusion_matrix_controller_dict['fn_controller'] = metric_value
                elif self._confusion_matrix_controller_fp_str in line:
                    self.confusion_matrix_controller_dict['fp_controller'] = metric_value
                elif self._confusion_matrix_controller_tn_str in line:
                    self.confusion_matrix_controller_dict['tn_controller'] = metric_value
                elif self._confusion_matrix_controller_tp_str in line:
                    self.confusion_matrix_controller_dict['tp_controller'] = metric_value

                # parse confusion_matrix_to_controller_threshold_dict
                elif self._confusion_matrix_to_controller_threshold_fn_str in line:
                    self.confusion_matrix_to_controller_threshold_dict[
                        'fn_to_controller_threshold'] = metric_value
                elif self._confusion_matrix_to_controller_threshold_fp_str in line:
                    self.confusion_matrix_to_controller_threshold_dict[
                        'fp_to_controller_threshold'] = metric_value
                elif self._confusion_matrix_to_controller_threshold_tn_str in line:
                    self.confusion_matrix_to_controller_threshold_dict[
                        'tn_to_controller_threshold'] = metric_value
                elif self._confusion_matrix_to_controller_threshold_tp_str in line:
                    self.confusion_matrix_to_controller_threshold_dict[
                        'tp_to_controller_threshold'] = metric_value

                # parse confusion_matrix_to_controller_2_le_1_dict
                elif self._confusion_matrix_to_controller_2_le_1_fn_str in line:
                    self.confusion_matrix_to_controller_2_le_1_dict[
                        'fn_to_controller_2_le_1'] = metric_value
                elif self._confusion_matrix_to_controller_2_le_1_fp_str in line:
                    self.confusion_matrix_to_controller_2_le_1_dict[
                        'fp_to_controller_2_le_1'] = metric_value
                elif self._confusion_matrix_to_controller_2_le_1_tn_str in line:
                    self.confusion_matrix_to_controller_2_le_1_dict[
                        'tn_to_controller_2_le_1'] = metric_value
                elif self._confusion_matrix_to_controller_2_le_1_tp_str in line:
                    self.confusion_matrix_to_controller_2_le_1_dict[
                        'tp_to_controller_2_le_1'] = metric_value

                # parse fn_controller_classification_distribution_dict
                elif self._fn_controller_classification_distribution_str + '[0]' in line:
                    self.fn_controller_classification_distribution_dict[
                        'fn_to_fn_controller'] = metric_value
                elif self._fn_controller_classification_distribution_str + '[1]' in line:
                    self.fn_controller_classification_distribution_dict[
                        'fn_to_fp_controller'] = metric_value
                elif self._fn_controller_classification_distribution_str + '[2]' in line:
                    self.fn_controller_classification_distribution_dict[
                        'fn_to_tn_controller'] = metric_value
                elif self._fn_controller_classification_distribution_str + '[3]' in line:
                    self.fn_controller_classification_distribution_dict[
                        'fn_to_tp_controller'] = metric_value

                # parse fp_controller_classification_distribution_dict
                elif self._fp_controller_classification_distribution_str + '[0]' in line:
                    self.fp_controller_classification_distribution_dict[
                        'fp_to_fn_controller'] = metric_value
                elif self._fp_controller_classification_distribution_str + '[1]' in line:
                    self.fp_controller_classification_distribution_dict[
                        'fp_to_fp_controller'] = metric_value
                elif self._fp_controller_classification_distribution_str + '[2]' in line:
                    self.fp_controller_classification_distribution_dict[
                        'fp_to_tn_controller'] = metric_value
                elif self._fp_controller_classification_distribution_str + '[3]' in line:
                    self.fp_controller_classification_distribution_dict[
                        'fp_to_tp_controller'] = metric_value

                # parse tn_controller_classification_distribution_dict
                elif self._tn_controller_classification_distribution_str + '[0]' in line:
                    self.tn_controller_classification_distribution_dict[
                        'tn_to_fn_controller'] = metric_value
                elif self._tn_controller_classification_distribution_str + '[1]' in line:
                    self.tn_controller_classification_distribution_dict[
                        'tn_to_fp_controller'] = metric_value
                elif self._tn_controller_classification_distribution_str + '[2]' in line:
                    self.tn_controller_classification_distribution_dict[
                        'tn_to_tn_controller'] = metric_value
                elif self._tn_controller_classification_distribution_str + '[3]' in line:
                    self.tn_controller_classification_distribution_dict[
                        'tn_to_tp_controller'] = metric_value

                # parse tp_controller_classification_distribution_dict
                elif self._tp_controller_classification_distribution_str + '[0]' in line:
                    self.tp_controller_classification_distribution_dict[
                        'tp_to_fn_controller'] = metric_value
                elif self._tp_controller_classification_distribution_str + '[1]' in line:
                    self.tp_controller_classification_distribution_dict[
                        'tp_to_fp_controller'] = metric_value
                elif self._tp_controller_classification_distribution_str + '[2]' in line:
                    self.tp_controller_classification_distribution_dict[
                        'tp_to_tn_controller'] = metric_value
                elif self._tp_controller_classification_distribution_str + '[3]' in line:
                    self.tp_controller_classification_distribution_dict[
                        'tp_to_tp_controller'] = metric_value

                # parse classification_time_dict
                elif self._classification_time_sum_p4_str in line:
                    self.classification_time_dict['classification_time_p4_sum_millisecond'] = metric_value
                elif self._classification_time_sum_controller_str in line:
                    self.classification_time_dict['classification_time_controller_sum_millisecond'] = metric_value

               # parse flow_sum_dict
                elif self._flow_sum_total_str in line:
                    self.flow_sum_dict['flow_total'] = metric_value
                elif self._flow_sum_benign_real_sum_str in line:
                    self.flow_sum_dict['flow_benign_real_sum'] = metric_value
                elif self._flow_sum_attack_real_sum_str in line:
                    self.flow_sum_dict['flow_attack_real_sum'] = metric_value
                elif self._flow_sum_predicted_p4_sum_str in line:
                    self.flow_sum_dict['flow_predicted_p4_sum'] = metric_value
                elif self._flow_sum_predicted_controller_sum_str in line:
                    self.flow_sum_dict['flow_predicted_controller_sum'] = metric_value

                # parse packet_ipv4_total_val
                elif self._packet_ipv4_total_str in line:
                    self.packet_ipv4_total_val = metric_value
                # parse flow_expired_val
                elif self._flow_expired_str in line:
                    self.flow_expired_val = metric_value
                # parse hash_collision_packet_val
                elif self._hash_collision_packet_str in line:
                    self.hash_collision_packet_val = metric_value

                else:
                    pass

                line = file.readline()
        # after parse the file, compute other metric values
        # compute the sum of flows sent to controller
        flows_to_controller_sum = self.confusion_matrix_to_controller_dict['fn_to_controller'] + \
            self.confusion_matrix_to_controller_dict['fp_to_controller'] + \
            self.confusion_matrix_to_controller_dict['tn_to_controller'] + \
            self.confusion_matrix_to_controller_dict['tp_to_controller']
        self.flow_sum_dict["flows_to_controller_sum"] = flows_to_controller_sum

        # compute the confusion_matrix_sum_wo_controller_dict
        confusion_matrix = ['fn', 'fp', 'tn', 'tp']
        for matrix_key in confusion_matrix:
            self.confusion_matrix_sum_wo_controller_dict[f'{matrix_key}_sum_wo_controller'] = self.confusion_matrix_p4_dict[f'{matrix_key}_p4'] + \
                self.confusion_matrix_to_controller_dict[f'{matrix_key}_to_controller']

    def parse_file_time(self, file_path):
        """Parse the evaluation file of classification time (.txt).

        Args:
            file_path: Path of .txt file
        """
        # patterns to get the metric value from string
        counter_start_str = 'bytes, '
        counter_end_str = ' packets'
        register_start_str = 'register[0]= '
        with open(file_path, 'r') as file:
            line = file.readline()
            while (line):
                # get the metric value
                counter_start_index = line.find(counter_start_str)
                counter_end_index = line.find(counter_end_str)
                reigister_start_index = line.find(register_start_str)

                if ((counter_start_index != -1) and (counter_end_index != -1)):
                    metric_value = int(
                        line[counter_start_index + len(counter_start_str): counter_end_index])
                elif reigister_start_index != -1:
                    metric_value = int(line[reigister_start_index +
                                            len(register_start_str):].strip('\n'))
                else:
                    metric_value = -1

                ########################## parse the evaluation file ##########################
                if self._flow_sum_predicted_p4_sum_str in line:
                    self.flow_sum_dict['flow_predicted_p4_sum'] = metric_value
                elif self._flow_sum_predicted_controller_sum_str in line:
                    self.flow_sum_dict['flow_predicted_controller_sum'] = metric_value

                # parse classification_time_dict
                elif self._classification_time_sum_p4_str in line:
                    self.classification_time_dict['classification_time_p4_sum_millisecond'] = metric_value
                elif self._classification_time_sum_controller_str in line:
                    self.classification_time_dict['classification_time_controller_sum_millisecond'] = metric_value
                else:
                    pass

                line = file.readline()

    def get_confusion_matrix_sum(self):
        """Get the confusion matrix of the sum of flows classified in switch and controller.
        """
        return self.confusion_matrix_sum_dict

    def get_confusion_matrix_sum_wo_controller(self):
        """Get the confusion matrix of the sum of flows classified in switch without controller.
        """
        return self.confusion_matrix_sum_wo_controller_dict

    def get_confusion_matrix_p4(self):
        """Get the confusion matrix of the sum of flows classified in switch.
        """
        return self.confusion_matrix_p4_dict

    def get_confusion_matrix_to_controller(self):
        """Get the confusion matrix of the sum of flows sent to controller.
        """
        return self.confusion_matrix_to_controller_dict

    def get_confusion_matrix_controller(self):
        """Get the confusion matrix of the sum of flows classified in controller.
        """
        return self.confusion_matrix_controller_dict

    def get_confusion_matrix_to_controller_threshold(self):
        """Get the confusion matrix of the sum of flows sent to controller reached the "threshold" condition.
        """
        return self.confusion_matrix_to_controller_threshold_dict

    def get_confusion_matrix_to_controller_2_le_1(self):
        """Get the confusion matrix of the sum of flows sent to controller reached the "2 le 1" condition.
        """
        return self.confusion_matrix_to_controller_2_le_1_dict

    def get_fn_controller_classification_distribution(self):
        """Get the classification distribution in controller for the flows classified as fn in switch.
        """
        return self.fn_controller_classification_distribution_dict

    def get_fp_controller_classification_distribution(self):
        """Get the classification distribution in controller for the flows classified as fp in switch.
        """
        return self.fp_controller_classification_distribution_dict

    def get_tn_controller_classification_distribution(self):
        """Get the classification distribution in controller for the flows classified as tn in switch.
        """
        return self.tn_controller_classification_distribution_dict

    def get_tp_controller_classification_distribution(self):
        """Get the classification distribution in controller for the flows classified as tp in switch.
        """
        return self.tp_controller_classification_distribution_dict

    def get_classification_time(self):
        """Get the classification time in switch and controller.
        """
        return self.classification_time_dict

    def get_flow_sum(self):
        """Get the counter value of metric which computes the sum values.
        """
        return self.flow_sum_dict

    def get_packet_ipv4_total(self):
        """Get the total ipv4 packets arrived in switch (only TCP and UDP).
        """
        return self.packet_ipv4_total_val

    def get_flow_expired(self):
        """Get the number of expired flows.
        """
        return self.flow_expired_val

    def get_hash_collision_packet_number(self):
        """Get the number of packets with hash collision.
        """
        return self.hash_collision_packet_val

    def compute_benign_sum_metrics(self):
        """Cet the precision, recall and f1 of the sum of the benign flows classified in switch and controller.
        """
        benign_fn = self.confusion_matrix_sum_dict['fp_sum']
        benign_fp = self.confusion_matrix_sum_dict['fn_sum']
        benign_tn = self.confusion_matrix_sum_dict['tp_sum']
        benign_tp = self.confusion_matrix_sum_dict['tn_sum']
        benign_pre = self.metric_cal.compute_precision(benign_fp, benign_tp)
        benign_re = self.metric_cal.compute_recall(benign_fn, benign_tp)
        benign_f1 = self.metric_cal.compute_f1(benign_pre, benign_re)
        return benign_pre, benign_re, benign_f1

    def compute_benign_sum_wo_controller_metrics(self):
        """Cet the precision, recall and f1 of the sum of the benign flows classified in switch without controller.
        """
        benign_fn = self.confusion_matrix_sum_wo_controller_dict['fp_sum_wo_controller']
        benign_fp = self.confusion_matrix_sum_wo_controller_dict['fn_sum_wo_controller']
        benign_tn = self.confusion_matrix_sum_wo_controller_dict['tp_sum_wo_controller']
        benign_tp = self.confusion_matrix_sum_wo_controller_dict['tn_sum_wo_controller']
        benign_pre = self.metric_cal.compute_precision(benign_fp, benign_tp)
        benign_re = self.metric_cal.compute_recall(benign_fn, benign_tp)
        benign_f1 = self.metric_cal.compute_f1(benign_pre, benign_re)
        return benign_pre, benign_re, benign_f1

    def compute_benign_p4_metrics(self):
        """Cet the precision, recall and f1 of the sum of the benign flows classified in switch.
        """
        benign_fn = self.confusion_matrix_p4_dict['fp_p4']
        benign_fp = self.confusion_matrix_p4_dict['fn_p4']
        benign_tn = self.confusion_matrix_p4_dict['tp_p4']
        benign_tp = self.confusion_matrix_p4_dict['tn_p4']
        benign_pre = self.metric_cal.compute_precision(benign_fp, benign_tp)
        benign_re = self.metric_cal.compute_recall(benign_fn, benign_tp)
        benign_f1 = self.metric_cal.compute_f1(benign_pre, benign_re)
        return benign_pre, benign_re, benign_f1

    def compute_attack_sum_metrics(self):
        """Cet the precision, recall and f1 of the sum of the attack flows classified in switch and controller.
        """
        attack_fn = self.confusion_matrix_sum_dict['fn_sum']
        attack_fp = self.confusion_matrix_sum_dict['fp_sum']
        attack_tn = self.confusion_matrix_sum_dict['tn_sum']
        attack_tp = self.confusion_matrix_sum_dict['tp_sum']
        attack_pre = self.metric_cal.compute_precision(attack_fp, attack_tp)
        attack_re = self.metric_cal.compute_recall(attack_fn, attack_tp)
        attack_f1 = self.metric_cal.compute_f1(attack_pre, attack_re)
        return attack_pre, attack_re, attack_f1

    def compute_attack_sum_wo_controller_metrics(self):
        """Cet the precision, recall and f1 of the sum of the attack flows classified in switch without controller.
        """
        attack_fn = self.confusion_matrix_sum_wo_controller_dict['fn_sum_wo_controller']
        attack_fp = self.confusion_matrix_sum_wo_controller_dict['fp_sum_wo_controller']
        attack_tn = self.confusion_matrix_sum_wo_controller_dict['tn_sum_wo_controller']
        attack_tp = self.confusion_matrix_sum_wo_controller_dict['tp_sum_wo_controller']
        attack_pre = self.metric_cal.compute_precision(attack_fp, attack_tp)
        attack_re = self.metric_cal.compute_recall(attack_fn, attack_tp)
        attack_f1 = self.metric_cal.compute_f1(attack_pre, attack_re)
        return attack_pre, attack_re, attack_f1

    def compute_attack_p4_metrics(self):
        """Cet the precision, recall and f1 of the sum of the attack flows classified in switch.
        """
        attack_fn = self.confusion_matrix_p4_dict['fn_p4']
        attack_fp = self.confusion_matrix_p4_dict['fp_p4']
        attack_tn = self.confusion_matrix_p4_dict['tn_p4']
        attack_tp = self.confusion_matrix_p4_dict['tp_p4']
        attack_pre = self.metric_cal.compute_precision(attack_fp, attack_tp)
        attack_re = self.metric_cal.compute_recall(attack_fn, attack_tp)
        attack_f1 = self.metric_cal.compute_f1(attack_pre, attack_re)
        return attack_pre, attack_re, attack_f1

    def compute_macro_avg_sum(self):
        """Get the macro average of precision, recall and f1 of the sum of flows classified in switch and controller.
        """
        benign_arr = np.array(self.compute_benign_sum_metrics())
        attack_arr = np.array(self.compute_attack_sum_metrics())
        macro_avg = (benign_arr + attack_arr) / 2
        return macro_avg

    def compute_macro_avg_sum_wo_controller(self):
        """Get the macro average of precision, recall and f1 of the sum of flows classified in switch without controller.
        """
        benign_arr = np.array(self.compute_benign_sum_wo_controller_metrics())
        attack_arr = np.array(self.compute_attack_sum_wo_controller_metrics())
        macro_avg = (benign_arr + attack_arr) / 2
        return macro_avg

    def compute_macro_avg_p4(self):
        """Get the macro average of precision, recall and f1 of the sum of flows classified in switch.
        """
        benign_arr = np.array(self.compute_benign_p4_metrics())
        attack_arr = np.array(self.compute_attack_p4_metrics())
        macro_avg = (benign_arr + attack_arr) / 2
        return macro_avg

    def compute_weighted_avg_sum(self):
        """Get the weighted average of precision, recall and f1 of the sum of flows classified in switch and controller.
        """
        benign_arr = np.array(self.compute_benign_sum_metrics())
        attack_arr = np.array(self.compute_attack_sum_metrics())
        benign_support = self.flow_sum_dict['flow_benign_real_sum']
        attack_support = self.flow_sum_dict['flow_attack_real_sum']
        benign_weight = benign_support / (benign_support + attack_support)
        attack_weight = attack_support / (benign_support + attack_support)
        weighted_avg = benign_arr * benign_weight + attack_arr * attack_weight
        return weighted_avg

    def compute_weighted_avg_sum_wo_controller(self):
        """Get the weighted average of precision, recall and f1 of the sum of flows classified in switch without controller.
        """
        benign_arr = np.array(self.compute_benign_sum_wo_controller_metrics())
        attack_arr = np.array(self.compute_attack_sum_wo_controller_metrics())
        benign_support = self.flow_sum_dict['flow_benign_real_sum']
        attack_support = self.flow_sum_dict['flow_attack_real_sum']
        benign_weight = benign_support / (benign_support + attack_support)
        attack_weight = attack_support / (benign_support + attack_support)
        weighted_avg = benign_arr * benign_weight + attack_arr * attack_weight
        return weighted_avg

    def compute_weighted_avg_p4(self):
        """Get the weighted average of precision, recall and f1 of the sum of flows classified in switch.
        """
        benign_arr = np.array(self.compute_benign_p4_metrics())
        attack_arr = np.array(self.compute_attack_p4_metrics())
        benign_support = self.confusion_matrix_p4_dict['fp_p4'] + \
            self.confusion_matrix_p4_dict['tn_p4']
        attack_support = self.confusion_matrix_p4_dict['fn_p4'] + \
            self.confusion_matrix_p4_dict['tp_p4']
        benign_weight = benign_support / (benign_support + attack_support)
        attack_weight = attack_support / (benign_support + attack_support)
        weighted_avg = benign_arr * benign_weight + attack_arr * attack_weight
        return weighted_avg

    def compute_classification_time_mean(self):
        """Get the mean of classification time in switch and controller.
        """
        classification_time_p4_sum_millisecond = self.classification_time_dict[
            'classification_time_p4_sum_millisecond']
        classification_time_controller_sum_millisecond = self.classification_time_dict[
            'classification_time_controller_sum_millisecond']
        p4_support = self.flow_sum_dict['flow_predicted_p4_sum']
        controller_support = self.flow_sum_dict['flow_predicted_controller_sum']
        classification_time_p4_mean_second = self.metric_cal.compute_classification_time(
            classification_time_p4_sum_millisecond, p4_support)
        classification_time_controller_mean_second = self.metric_cal.compute_classification_time(
            classification_time_controller_sum_millisecond, controller_support)
        return classification_time_p4_mean_second, classification_time_controller_mean_second

    def convert_benign_sum_metrics_to_dict(self):
        benign_sum_metrics = self.compute_benign_sum_metrics()
        re_dict = {
            'benign_pre_sum': benign_sum_metrics[0],
            'benign_re_sum': benign_sum_metrics[1],
            'benign_f1_sum': benign_sum_metrics[2]
        }
        return re_dict

    def convert_benign_sum_wo_controller_metrics_to_dict(self):
        benign_sum_wo_controller_metrics = self.compute_benign_sum_wo_controller_metrics()
        re_dict = {
            'benign_pre_sum_wo_controller': benign_sum_wo_controller_metrics[0],
            'benign_re_sum_wo_controller': benign_sum_wo_controller_metrics[1],
            'benign_f1_sum_wo_controller': benign_sum_wo_controller_metrics[2]
        }
        return re_dict

    def convert_benign_p4_metrics_to_dict(self):
        benign_p4_metrics = self.compute_benign_p4_metrics()
        re_dict = {
            'benign_pre_p4': benign_p4_metrics[0],
            'benign_re_p4': benign_p4_metrics[1],
            'benign_f1_p4': benign_p4_metrics[2]
        }
        return re_dict

    def convert_attack_sum_metrics_to_dict(self):
        attack_sum_metrics = self.compute_attack_sum_metrics()
        re_dict = {
            'attack_pre_sum': attack_sum_metrics[0],
            'attack_re_sum': attack_sum_metrics[1],
            'attack_f1_sum': attack_sum_metrics[2]
        }
        return re_dict

    def convert_attack_sum_wo_controller_metrics_to_dict(self):
        attack_sum_wo_controller_metrics = self.compute_attack_sum_wo_controller_metrics()
        re_dict = {
            'attack_pre_sum_wo_controller': attack_sum_wo_controller_metrics[0],
            'attack_re_sum_wo_controller': attack_sum_wo_controller_metrics[1],
            'attack_f1_sum_wo_controller': attack_sum_wo_controller_metrics[2]
        }
        return re_dict

    def convert_attack_p4_metrics_to_dict(self):
        attack_p4_metrics = self.compute_attack_p4_metrics()
        re_dict = {
            'attack_pre_p4': attack_p4_metrics[0],
            'attack_re_p4': attack_p4_metrics[1],
            'attack_f1_p4': attack_p4_metrics[2]
        }
        return re_dict

    def convert_macro_avg_sum_to_dict(self):
        macro_avg_sum = self.compute_macro_avg_sum()
        re_dict = {
            'macro_avg_pre_sum': macro_avg_sum[0],
            'macro_avg_re_sum': macro_avg_sum[1],
            'macro_avg_f1_sum': macro_avg_sum[2]
        }
        return re_dict

    def convert_macro_avg_sum_wo_controller_to_dict(self):
        macro_avg_sum_wo_controller = self.compute_macro_avg_sum_wo_controller()
        re_dict = {
            'macro_avg_pre_sum_wo_controller': macro_avg_sum_wo_controller[0],
            'macro_avg_re_sum_wo_controller': macro_avg_sum_wo_controller[1],
            'macro_avg_f1_sum_wo_controller': macro_avg_sum_wo_controller[2]
        }
        return re_dict

    def convert_macro_avg_p4_to_dict(self):
        macro_avg_p4 = self.compute_macro_avg_p4()
        re_dict = {
            'macro_avg_pre_p4': macro_avg_p4[0],
            'macro_avg_re_p4': macro_avg_p4[1],
            'macro_avg_f1_p4': macro_avg_p4[2]
        }
        return re_dict

    def convert_weighted_avg_sum_to_dict(self):
        weighted_avg_sum = self.compute_weighted_avg_sum()
        re_dict = {
            'weighted_avg_pre_sum': weighted_avg_sum[0],
            'weighted_avg_re_sum': weighted_avg_sum[1],
            'weighted_avg_f1_sum': weighted_avg_sum[2]
        }
        return re_dict

    def convert_weighted_avg_sum_wo_controller_to_dict(self):
        weighted_avg_sum_wo_controller = self.compute_weighted_avg_sum_wo_controller()
        re_dict = {
            'weighted_avg_pre_sum_wo_controller': weighted_avg_sum_wo_controller[0],
            'weighted_avg_re_sum_wo_controller': weighted_avg_sum_wo_controller[1],
            'weighted_avg_f1_sum_wo_controller': weighted_avg_sum_wo_controller[2]
        }
        return re_dict

    def convert_weighted_avg_p4_to_dict(self):
        weighted_avg_p4 = self.compute_weighted_avg_p4()
        re_dict = {
            'weighted_avg_pre_p4': weighted_avg_p4[0],
            'weighted_avg_re_p4': weighted_avg_p4[1],
            'weighted_avg_f1_p4': weighted_avg_p4[2]
        }
        return re_dict

    def convert_classification_time_mean_to_dict(self):
        classification_time_mean = self.compute_classification_time_mean()
        re_dict = {
            'classification_time_mean_p4': classification_time_mean[0],
            'classification_time_mean_controller': classification_time_mean[1]
        }
        return re_dict

    def save_to_csv(self, csv_path, keep_header, dataset_day, parameter_dict):
        """Save evaluation in csv file.
        """
        re_dict = {}

        re_dict.update(parameter_dict)

        # concatenate the post metrics dictionaries
        re_dict.update(self.convert_macro_avg_sum_to_dict())
        re_dict.update(self.convert_macro_avg_sum_wo_controller_to_dict())
        re_dict.update(self.convert_macro_avg_p4_to_dict())

        re_dict.update(self.convert_weighted_avg_sum_to_dict())
        re_dict.update(self.convert_weighted_avg_sum_wo_controller_to_dict())
        re_dict.update(self.convert_weighted_avg_p4_to_dict())

        re_dict.update(self.convert_benign_sum_metrics_to_dict())
        re_dict.update(self.convert_benign_sum_wo_controller_metrics_to_dict())
        re_dict.update(self.convert_benign_p4_metrics_to_dict())

        re_dict.update(self.convert_attack_sum_metrics_to_dict())
        re_dict.update(self.convert_attack_sum_wo_controller_metrics_to_dict())
        re_dict.update(self.convert_attack_p4_metrics_to_dict())

        re_dict.update(self.convert_classification_time_mean_to_dict())

        # concatenate basic metrics dictionaries

        re_dict.update(self.confusion_matrix_sum_dict)
        re_dict.update(self.confusion_matrix_sum_wo_controller_dict)
        re_dict.update(self.confusion_matrix_p4_dict)
        re_dict.update(self.confusion_matrix_to_controller_dict)
        re_dict.update(self.confusion_matrix_controller_dict)

        re_dict.update(self.confusion_matrix_to_controller_threshold_dict)
        re_dict.update(self.confusion_matrix_to_controller_2_le_1_dict)

        re_dict.update(self.fn_controller_classification_distribution_dict)
        re_dict.update(self.fp_controller_classification_distribution_dict)
        re_dict.update(self.tn_controller_classification_distribution_dict)
        re_dict.update(self.tp_controller_classification_distribution_dict)

        re_dict.update(self.classification_time_dict)
        re_dict.update(self.flow_sum_dict)

        other_dict = {
            'packet_ipv4_total': self.packet_ipv4_total_val,
            'flow_expired': self.flow_expired_val,
            'hash_collision_packet_number': self.hash_collision_packet_val
        }

        re_dict.update(other_dict)
        df = pd.DataFrame(re_dict, index=[dataset_day])
        df.to_csv(csv_path, mode='a', header=keep_header)

    def save_classification_time_to_csv(self, csv_path, keep_header, dataset_day, parameter_dict):
        """Save evaluation of classification time in csv file.

        """
        re_dict = {}

        re_dict.update(parameter_dict)
        re_dict.update(self.convert_classification_time_mean_to_dict())
        re_dict.update(self.flow_sum_dict)
        df = pd.DataFrame(re_dict, index=[dataset_day])
        df.to_csv(csv_path, mode='a', header=keep_header)


class MetricCalculator():

    def __init__(self) -> None:
        pass

    def compute_precision(self, fp, tp):
        pre = tp / (tp + fp)
        return pre

    def compute_recall(self, fn, tp):
        re = tp / (tp + fn)
        return re

    def compute_f1(self, pre, re):
        f1 = (2 * pre * re) / (pre + re)
        return f1

    def compute_macro_avg(self, benign_value, attack_value):
        macro_avg = (benign_value + attack_value) / 2
        return macro_avg

    def compute_weighted_avg(self, benign_value, attack_value, benign_support, attack_support):
        benign_weight = benign_support / (benign_support + attack_support)
        attack_weight = attack_support / (benign_support + attack_support)
        weighted_avg = benign_value * benign_weight + attack_value * attack_weight
        return weighted_avg

    def compute_classification_time(self, time_sum, support):
        # factor for converting millisecond to second
        factor = 1000000
        time_mean = time_sum / support / factor
        return time_mean


class FileMean():
    """Compute the mean value of each metric.
    """

    def __init__(self, file_path) -> None:
        self.df = pd.read_csv(file_path, index_col=0)
        # get the day of this dataset
        self.day = self.df.index[0]

    def compute_mean(self, final_path):
        """Compute the mean value of the metric with different gini_threshold.
        """
        df_gini_list = []
        gini_threshold_list = [0.1, 0.2, 0.3, 0.4]
        # drop the evaluation index column
        df = self.df.drop(["evaluation_index"], axis=1)

        # compute the mean of different gini_threhold, convert it from data series to dataframe
        # .T convert the index of data series to the columns of dataframe
        for gini_threshold_val in gini_threshold_list:
            df_gini_tmp = df[self.df["gini_threshold"] ==
                             gini_threshold_val].mean(axis=0).to_frame().T
            df_gini_tmp.index = [self.day]
            df_gini_list.append(df_gini_tmp)

        # aggregate four dataframes to one single dataframe
        df_final = pd.concat(df_gini_list)

        # round the values except the precision, recall and f1 metric
        columns_to_round = []
        for col in df_final.columns:
            if ("pre_" not in col) and ("re_" not in col) and ("f1_" not in col) and ("time_mean" not in col):
                columns_to_round.append(col)
        df_final[columns_to_round] = df_final[columns_to_round].round(
            0).astype(int)
        df_final["gini_threshold"] = gini_threshold_list
        df_final.to_csv(final_path, mode='w', header=True)
        return df_final
