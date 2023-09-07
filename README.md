# Collaborative ML-based NIDS
This repository hosts the code for the research paper titled "CML-IDS: Enhancing Intrusion Detection in SDN through Collaborative Machine Learning" which is accepted to publish in the "19th International Conference on Network and Service Management (CNSM), 2023".

Stay tuned for the upcoming link to access the paper.

If you use the code, please cite us:
"Golchin, P., Zhou, C., Agnihotri, P., Hajizadeh, M., Kundel, R., Steinmetz, R., 2023 October. CML-IDS: Enhancing Intrusion Detection in SDN through Collaborative Machine Learning.
To appear in the Proceedings of the 19th International Conference on Network and Service Management (CNSM), 2023."

The code is provided by Chengbo Zhou and Pegah Golchin.
## Table of Contents

- [**Prerequisites**](#prerequisites)
- [**FAQ**](#faq)

## <span id="prerequisites">Prerequisites</span>

The following tools are needed to set up the environment.

### [P4](https://github.com/p4lang)

To set up the P4 environment, you need Bmv2, PI and P4C packages. The following commands based on the [user-dev-bootstrap.sh](https://github.com/p4lang/tutorials/blob/master/vm-ubuntu-20.04/user-dev-bootstrap.sh) from the P4 homepage guide you how to set up the P4 environment.

#### Install dependancies

- Basic dependancies:

```bash
sudo apt-get install -y automake cmake libgmp-dev \
    libpcap-dev libboost-dev libboost-test-dev libboost-program-options-dev libboost-graph-dev libboost-iostreams-dev\
    libboost-system-dev libboost-filesystem-dev libboost-thread-dev \
    libevent-dev libtool flex bison pkg-config g++ libssl-dev \
    git libgc-dev libfl-dev llvm python3 python3-pip tcpdump \
    libreadline-dev valgrind libtool-bin

pip3 install ipaddr scapy ply psutil
```

- [Protobuf v3.18.1](https://github.com/protocolbuffers/protobuf/releases/tag/v3.18.1):  
The version 3.18.1 is out of date, it is not feasible for the P4runtime. Please install the higher version (3.20.1).

```bash
git clone https://github.com/google/protobuf.git
cd protobuf
git checkout v3.18.1
./autogen.sh
./configure --prefix=/usr
make
sudo make install
sudo ldconfig
# Force install python module
# cd python
# sudo python3 setup.py install
# cd ..
cd ..
```

- [gRPC v1.43.2](https://github.com/grpc/grpc/releases/tag/v1.43.2):

```bash
git clone --depth=1 -b v1.43.2 https://github.com/google/grpc.git
cd grpc
git submodule update --init --recursive
mkdir build
cd build
cmake ..
make
sudo make install
cd ..
find /usr/lib /usr/local $HOME/.local | sort > $HOME/usr-local-2b-before-grpc-pip3.txt
pip3 list | tee $HOME/pip3-list-2b-before-grpc-pip3.txt
sudo pip3 install -r requirements.txt
GRPC_PYTHON_BUILD_WITH_CYTHON=1 sudo pip3 install .
sudo ldconfig
cd ..
```

#### Install [PI](https://github.com/p4lang/PI)

```bash
git clone https://github.com/p4lang/PI.git
cd PI
git submodule update --init --recursive
./autogen.sh
./configure --with-proto
make
make check
sudo make install
sudo ldconfig
cd ..
```

#### Install [Bmv2](https://github.com/p4lang/behavioral-model)

```bash
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
./install_deps.sh
./autogen.sh
./configure --enable-debugger --with-pi --with-thrift
make
sudo make install-strip
sudo ldconfig
cd ..
```

#### Install [P4C](https://github.com/p4lang/p4c)

```bash
git clone https://github.com/p4lang/p4c
cd p4c
git submodule update --init --recursive
mkdir -p build
cd build
cmake ..
make -j1
sudo make install
sudo ldconfig
cd ../..
```

The python module code of Bmv2 and PI are installed in the site-packages directory under the Python direcotory. The default Python of Ubuntu system only looks in the dist-packages directory. You have to move these python packages into the dist-packages by calling the function [move_usr_local_lib_python3_from_site_packages_to_dist_packages in the user-dev-bootstrap.sh](https://github.com/p4lang/tutorials/blob/master/vm-ubuntu-20.04/user-dev-bootstrap.sh).  

If an error "No module named google.protobuf" occurs, please check the path of protobuf directory under the dist-packages.

### [Mininet](http://mininet.org/)

```bash
git clone https://github.com/mininet/mininet
mininet/util/install.sh -a
```

### Scripts in Thesis

#### Install dependancies

- [Scapy](https://scapy.readthedocs.io/en/latest/index.html)

```bash
sudo apt install python3-scapy
```

- [NFStream](https://github.com/nfstream)

```bash
pip3 install nfstream
```

- [tshark](https://www.wireshark.org/docs/man-pages/tshark.html)  
Usage: filter the pcap file.

```bash
sudo apt install tshark
```

- Others

```bash
pip3 install matplotlib numpy scipy scikit-learn graphviz
```

If an error (*graphviz.backend.execute.ExecutableNotFound: failed to execute PosixPath('dot'), make sure the Graphviz executables are on your systems' PATH*) occurs for graphviz, install the graphviz package in your system by running `sudo apt install graphviz`.

## <span id="faq">FAQ</span>

> **Q:** Use simple_switch connects network interface with bmv2, but get error: *IPC address is occupied*.  
> **A:** Instead of restarting machine, you can kill the process of simple_switch. It needs to find the PID of simple_switch process.
>
> ```
> ps -ef | grep simple_switch
> sudo kill -9 PID
> ```

> **Q:** *ModuleNotFoundError* occurs while importing protobuf.  
> **A:** Install protobuf with the compitable version via pip3 instead of installing it from source (GitHub).
>
