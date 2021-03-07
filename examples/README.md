

## MVP交互流程
考虑简单的两方纵向联邦学习，例如金融科技公司C为两家银行A、B提供客户画像和联合风控服务。假设银行的原始客户数据位于私域网络的数据库中，在保证数据安全且操作可审计的情况下，可以通过密码学方案(如秘密共享SS)将客户数据加密传递到银行间的联邦域网络，在密文基础上可进一步实现联合建模。在这里，银行同时作为数据源方和算力提供方，金融科技公司则是算法提供方和任务发起方，MVP流程如下：
1. 合约部署方为系统管理员，可以添加A、B、C的机构名和地址关系;
2. 银行A、B用DDO描述私域数据和联邦域算力的使用条款和服务类型，并生成CDT标识符；
3. 将以上生成的DDO存储在ipfs中，得到存储地址，将CDT、storage和proof注册到链上；
4. 公司C对数据/算力CDT进行组合，填充child_cdt_list以及对各资源的代码哈希，生成算法CDT后上ipfs并上链；
5. 银行A、B分别验证算法CDT是否满足资源使用条款，通过后将数据/算力CDT授权给算法CDT；
6. 算法提供方在链上任务市场新建一个任务，并将算法CDT提交到该任务的工作下；
7. 算法提供方远程操作各银行的数据/算力(附带签名、算法CDT和工作ID)。各银行需要核实该算法CDT是否取得授权、签名有效性和所有者、工作ID对应的状态等。通过的话，就允许访问发起远程计算。

Demo展示了上述流程的完整用例，关键代码模块包括：[demo.py](https://github.com/ownership-labs/cdt-sdk/blob/main/demo.py)、[provider.py](https://github.com/ownership-labs/cdt-sdk/blob/main/market/provider.py)、[dataset.py](https://github.com/ownership-labs/cdt-sdk/blob/main/market/dataset.py)。此外，CDT的潜在用例还很丰富，例如可以用于模型安全推断上。这通常是云提供商利用同态加密技术来加密模型、推断需求方加密数据，因此可以用一个包含两个操作的算法CDT来表示。