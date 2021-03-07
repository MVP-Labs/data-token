<h1 align="center">DataToken</h1>

## 概览

本项目为Ownership Labs开发的跨域分布式数据权限管理和链下可信计算中间件(DataToken SDK)，由[LatticeX](https://github.com/LatticeX-Foundation)基金会提供支持，细节可查阅[Grants](./docs/grants_cn.md)和[论文](./docs/white_paper.md)。该SDK利用了区块链的多方对等共识和信息不可篡改等可信特征，实现了数据归属确权、数据服务授权和数据计算追溯。

## 核心理念

项目设计了资产层次化聚合和计算约束满足方案，允许资产方在其服务条款中声明可信操作的许可列表，同时聚合方可在多个不同域的数据资产和算力资产上定义可信的分布式计算工作流。当满足资产预先声明的操作规范时，聚合计算才会被授权，且该过程可自动执行，最终实现(数据)资产一次发布、多次出售。数据共享计算的全生命周期将变得更透明合规且具有可追溯性，我们希望交易市场上出现契合数据流动结构的数据联合体和自主经济代理。

## 系统组成

| 模块                     | 描述                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| [dt-contracts](https://github.com/ownership-labs/dt-contracts)            | 数据通证颁发、可信算子发布、任务市场等合约                                          |
| [dt-web3](https://github.com/ownership-labs/dt-web3)            | 与链上合约交互的链下模型类和web3工具集                                          |
| [dt-asset](https://github.com/ownership-labs/dt-asset)             | 资产元数据管理和跨域可信计算服务规范                                           |
| [dt-sdk](https://github.com/ownership-labs/DataToken/dt_sdk)           | 为开发者提供DataToken在数据协作中的完整功能                                         |
| [rtt-tracer](https://github.com/ownership-labs/Compute-to-Data)            | 面向远程资产的可追溯、隐私保护的机器学习 |

## SDK功能特性

### 功能特性

该仓库下的dt-sdk封装了数据协作过程中的几个关键服务模块，包括系统管理模块、资产管理模块、任务工作模块、跨域追溯模块和服务验证模块。不同的业务角色可以使用不同的模块：

- 系统管理员可通过系统模块来管理链上的资产提供方和可信算子模版；
- 资产提供方和聚合方可通过资产模块来实现数据资产的发布、授权和聚合；
- 需求方和求解方可通过任务工作模块来完成任务发布、计算求解和远程执行验证；
- 监管方可通过跨域追溯模块来确认资产的合理利用，交易方也可根据资产的来源和历史生命周期来定价。

### 运行流程

在运行测试前，首先需要部署dt-contracts到alaya私链，参考[部署教程](https://github.com/ownership-labs/dt-contracts)，使用其中预先设置的四个账户。同时配置DataToken目录下的config.ini，包括artifacts_path和address_file。

使用如下命令测试：
```
$ git clone https://github.com/ownership-labs/DataToken
$ git clone https://github.com/ownership-labs/dt-contracts
$ git clone https://github.com/ownership-labs/dt-web3
$ git clone https://github.com/ownership-labs/dt-asset
$ cd DataToken
$ export PYTHONPATH=$PYTHONPATH:../dt-asset:../dt-web3:../DataToken
$ pip install -r requirements.txt
$ python tests/test.py
```

### MVP用例

我们还提供了DataToken在实际场景中的用例，分别是企业间数据协作、用户级边缘计算和可追溯的隐私AI，查看[examples](./examples)和[Compute-to-Data](https://github.com/ownership-labs/Compute-to-Data)。