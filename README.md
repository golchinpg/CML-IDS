# Collaborative ML-based NIDS in SDN

This repository hosts the code for the research paper titled "CML-IDS: Enhancing Intrusion Detection in SDN through Collaborative Machine Learning" which is accepted to publish in the "19th International Conference on Network and Service Management (CNSM), 2023".

Stay tuned for the upcoming link to access the paper.

If you use the code, please cite us:
"Golchin, P., Zhou, C., Agnihotri, P., Hajizadeh, M., Kundel, R., Steinmetz, R., 2023 October. CML-IDS: Enhancing Intrusion Detection in SDN through Collaborative Machine Learning.
To appear in the Proceedings of the 19th International Conference on Network and Service Management (CNSM), 2023."

The code is provided by Chengbo Zhou and Pegah Golchin.

## Table of Contents

- [**Prerequisites**](#prerequisites)
- [**Run CML-IDS**](#run_cml_ids)
- [**Evaluate CML-IDS**](#evaluation)
- [**FAQ**](#faq)

## <span id="prerequisites">Prerequisites</span>

### Install P4 related tools

The following tools provided by [p4language](https://github.com/p4lang) should be installed before running CML-IDS. The installation guides can be found in their repositories.

- [bmv2](https://github.com/p4lang/behavioral-model): an implementation of P4 programmable software switch.

- [p4c](https://github.com/p4lang/p4c): a reference compiler for the P4 program.

- [PI](https://github.com/p4lang/PI): an implementation of P4Runtime server.

- [p4runtime-shell](https://github.com/p4lang/p4runtime-shell): an implementation of P4Runtime client.
    - Add `my_sniff` function to the class `PacketIn` located in the file `shell.py`. 
        ```python
        def my_sniff(self, function, timeout=None):
        """
        Modifed sniff function provided by P4Runtime Shell. The given function is applied directly when a packet is sniffed by the controller. 
        """
        if timeout is not None and timeout < 0:
            raise ValueError("Timeout can't be a negative number.")

        if timeout is None:
            while True:
                try:
                    msg = self.packet_in_queue.get(block=True)
                    function(msg)
                except KeyboardInterrupt:
                    # User sends a Ctrl+C -> breaking
                    break
        ```

### Install other tools

These tools are required to process dataset, train machine learning models, send network packets, etc. Please install them using your favorite packet management tool or from the source.

- [Scapy](https://scapy.net/): generate and send network packets.

- [NFStream](https://www.nfstream.org/): aggregate network packets into flows.

- [Tcpreplay](https://tcpreplay.appneta.com/): replay network packets from .pcap file.

- [scikit-learn](https://scikit-learn.org/stable/): machine learning tool, used by CML-IDS for generating random forest model, refining dataset, etc.

- [XGBoost](https://github.com/dmlc/xgboost/tree/master): gradient boosting library, used to generate gradient boosting trees.

- [TensorFlow](https://www.tensorflow.org/): machine learning library, used for generating neural networking model.

- [Pandas](https://pandas.pydata.org/): data analysis tool.

## <span id="run_cml_ids">Run CML-IDS</span>

The existing trained models for CP-IDS and DP-IDS are located in the directory `/cml_ids/ml_models`. If you want to train your own models as well as generate P4 code snippets and table entries, the example codes are provided in the directory `/cml_ids/scripts`.

CML-IDS can be started by the following steps.

1. Setup the virtual network interfaces

```bash
    sudo ./control/interface_setup.sh
```

2. Compile the P4 program and start up bmv2 using `simple_switch_grpc`

```bash
    sudo ./control/switch_setup.sh
```

3. Start the controller in a new console

```bash
    ./control/start_controller_p4runtime_shell.py
```

4. Install table entries in a new console

```bash
    sudo ./control/add_entries.sh
```

5. Replay the dataset [CIC-IDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) using `tcpreplay` in a new console

```bash
    sudo tcpreplay -i veth1 -v <.pcap file path>
```

## <span id="evaluation">Evaluate CML-IDS</span>
You can add your customized counters or registers for monitoring in the P4 program and extend the file `./cml_ids/p4/debug/status_entries.txt` properly. Show the evaluation result by running

```bash
    sudo ./control/read_status.sh
```

## <span id="faq">FAQ</span>
