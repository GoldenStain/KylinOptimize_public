python版本3.7.9，从源代码编译安装
参考教程 https://blog.csdn.net/qq_42571592/article/details/122902266 1-4步骤

yum安装的库:
bcc-tools clang llvm llvm-devel llvm-static clang clang-devel clang-libs elfutils-devel elfutils-debuginfod elfutils-debuginfod-client-devel luajit-devel mesa-libGL

额外依赖工具：
perf numad perl

从github上安装的库：
iovisor/bcc仓库里维护量一份代码(/program/ebpf/BCCSource文件夹)，修改部分代码bug
项目中 src/python/bcc 文件夹内version.py文件去掉末尾的".in"再整体移动到 /usr/local/lib/python3.7/site-packages 里面去

eBPF监测的数据（单位时间内）:
磁盘IO量
磁盘IO次数
网络IO量
网络IO次数
CPU使用量
内存使用量

网络有问题时尝试:
nmcli n on

**A-Tune编译安装**

仓库git链接：

<https://gitee.com/goldenstain/A-Tune.git>

速览编译安装步骤:

#### 1、安装依赖系统软件包
```bash
yum install -y golang-bin python3 perf sysstat hwloc-gui lshw
```

#### 2、安装python依赖包  

#### 2.1 安装A-Tune服务的依赖包
```bash
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost python3-pyyaml
```
或
```bash
pip3 install dict2xml Flask-RESTful pandas scikit-optimize xgboost scikit-learn pyyaml
```
#### 2.2、安装数据库依赖包（可选）
如用户已安装数据库应用，并需要将A-Tune的采集和调优数据存储到数据库中，可以安装以下依赖包：
```bash
yum install -y python3-sqlalchemy python3-cryptography
```
或
```bash
pip3 install sqlalchemy cryptography
```
同时，请参照下表，根据对应的数据库应用任选一种方式进行依赖安装。
| **数据库** | **yum安装** | **pip安装** |
| ------------------------------ | ---------- | ------------ |
| PostgreSQL | yum install -y python3-psycopg2 | pip3 install psycopg2 |

#### 4、编译
```bash
cd A-Tune
make
```

#### 5、安装
```bash
make collector-install
make install
```

请在初次使用前，完成配置文件的编辑，否则可能导致运行失败。



