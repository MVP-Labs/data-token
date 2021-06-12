# """Demo"""

from datatoken.config import Config
from datatoken.web3.wallet import Wallet
from datatoken.web3.utils import add_ethereum_prefix_and_hash_msg
from datatoken.service.system import SystemService
from datatoken.service.asset import AssetService
from datatoken.service.job import JobService
from datatoken.service.tracer import TracerService


config = Config(filename='./config.ini')

system_account = Wallet(
    config.web3, private_key='0x1e771da3a1dcae0fd77a942cc816fd6b9b4cca97220f8ea6c6782a848714129d')
org1_account = Wallet(
    config.web3, private_key='0x65e5b356ab8369c2971d584ade019c84d898f9b5d77d35940813c24a804d3b43')
org2_account = Wallet(
    config.web3, private_key='0x243ba7d269e52c5861aca39cfa21cc94c75d43ad4189d666c06bae590a3a5317')
org3_account = Wallet(
    config.web3, private_key='0xc679156774b1ea1ce27e00ea82efd3a1c5ad48d314abae0d1226452546679422')

# print(system_account.address)
# print(org1_account.address)
# print(org2_account.address)
# print(org3_account.address)

system_service = SystemService(config)
asset_service = AssetService(config)
job_service = JobService(config)
tracer_service = TracerService(config)

############
system_service.register_enterprise(
    org1_account.address, 'org1', 'test_org1', system_account)
system_service.add_provider(org1_account.address, system_account)

system_service.register_enterprise(
    org2_account.address, 'org2', 'test_org2', system_account)
system_service.add_provider(org2_account.address, system_account)

system_service.register_enterprise(
    org3_account.address, 'org3', 'test_org3', system_account)
system_service.add_provider(org3_account.address, system_account)


metadata = {'main': {'name': 'add_op',
                     'desc': 'test add op', 'type': 'Operation'}}
with open('./tests/template/add_op.py', 'r') as f:
    operation = f.read()
with open('./tests/template/args.json', 'r') as f:
    params = f.read()

op1 = system_service.publish_template(
    metadata, operation, params, system_account)

############
metadata = {'main': {'name': 'leaf data1',
                     'desc': 'test leaf1', 'type': 'Dataset'}}
service = {
    'index': 'sid0_for_dt1',
    'endpoint': 'ip:port',
    'descriptor': {
        'template': op1.tid,
        'constraint': {
            'arg1': 1,
            'arg2': {}
        }
    },
    'attributes': {
        'price': 10
    }
}

ddo1 = asset_service.generate_ddo(
    metadata, [service], org1_account.address, verify=True)
asset_service.publish_dt(ddo1, org1_account)

metadata = {'main': {'name': 'leaf data2',
                     'desc': 'test leaf2', 'type': 'Dataset'}}
service = {
    'index': 'sid0_for_dt2',
    'endpoint': 'ip:port',
    'descriptor': {
        'template': op1.tid,
        'constraint': {
            'arg1': {},
            'arg2': 2
        }
    },
    'attributes': {
        'price': 10
    }
}

ddo2 = asset_service.generate_ddo(
    metadata, [service], org2_account.address, verify=True)
asset_service.publish_dt(ddo2, org2_account)

metadata = {'main': {'type': 'Dataset',
                     'desc': 'test union1', 'name': 'data union1'}}
child_dts = [
    ddo1.dt,
    ddo2.dt
]
service = {
    'index': 'sid0_for_cdt1',
    'endpoint': 'ip:port',
    'descriptor': {
        'workflow': {
            ddo1.dt: {
                'service': 'sid0_for_dt1',
                'constraint': {
                    'arg1': 1,
                    'arg2': 3
                }
            },
            ddo2.dt: {
                'service': 'sid0_for_dt2',
                'constraint': {
                    'arg1': {},
                    'arg2': 2
                }
            }
        }
    },
    'attributes': {
        'price': 20,
        'op_name': "federated"
    }
}

service1 = {
    'index': 'sid1_for_cdt2',
    'endpoint': 'ip:port',
    'descriptor': {
        'workflow': {
            ddo1.dt: {
                'service': 'sid0_for_dt1',
                'constraint': {
                    'arg1': 1,
                    'arg2': 3
                }
            },
            ddo2.dt: {
                'service': 'sid0_for_dt2',
                'constraint': {
                    'arg1': 2,
                    'arg2': 2
                }
            }
        }
    },
    'attributes': {
        'price': 30,
        'op_name': "download"
    }
}

ddo3 = asset_service.generate_ddo(
    metadata, [service, service1], org3_account.address, child_dts=child_dts, verify=True)
asset_service.publish_dt(ddo3, org3_account)

msg = f'{org3_account.address}{ddo3.dt}'
msg_hash = add_ethereum_prefix_and_hash_msg(msg)
signature = org3_account.sign(msg_hash).signature.hex()

print(asset_service.check_service_terms(
    ddo3.dt, ddo1.dt, org1_account.address, signature))
print(asset_service.check_service_terms(
    ddo3.dt, ddo2.dt, org2_account.address, signature))

asset_service.grant_dt_perm(ddo1.dt, ddo3.dt, org1_account)
asset_service.grant_dt_perm(ddo2.dt, ddo3.dt, org2_account)
asset_service.activate_cdt(ddo3.dt, ddo3.child_dts, org3_account)

metadata = {'main': {'type': 'Algorithm',
                     'name': 'algorithm1', 'desc': 'test algo1'}}
child_dts = [
    ddo3.dt,
]
service1 = {
    'index': 'sid0_for_cdt2',
    'endpoint': 'ip:port',
    'descriptor': {
        'workflow': {
            ddo3.dt: {
                'service': 'sid0_for_cdt1',
                'constraint': {
                    ddo1.dt: {
                        'arg1': 1,
                        'arg2': 3,
                    },
                    ddo2.dt: {
                        'arg1': 1,
                        'arg2': 2
                    }
                }
            }
        }
    },
    'attributes': {
        'price': 30
    }
}

ddo4 = asset_service.generate_ddo(
    metadata, [service1], org3_account.address, child_dts=child_dts, verify=True)
asset_service.publish_dt(ddo4, org3_account)

msg = f'{org3_account.address}{ddo4.dt}'
msg_hash = add_ethereum_prefix_and_hash_msg(msg)
signature = org3_account.sign(msg_hash).signature.hex()

print(asset_service.check_service_terms(
    ddo4.dt, ddo3.dt, org3_account.address, signature))

asset_service.grant_dt_perm(ddo3.dt, ddo4.dt, org3_account)
asset_service.activate_cdt(ddo4.dt, ddo4.child_dts, org3_account)

metadata = {'main': {'type': 'Algorithm',
                     'name': 'algorithm2', 'desc': 'test algo2'}}
child_dts = [
    ddo3.dt,
]
service1 = {
    'index': 'sid0_for_cdt3',
    'endpoint': 'ip:port',
    'descriptor': {
        'workflow': {
            ddo3.dt: {
                'service': 'sid0_for_cdt1',
                'constraint': {
                    ddo1.dt: {
                        'arg1': 1,
                        'arg2': 3,
                    },
                    ddo2.dt: {
                        'arg1': 4,
                        'arg2': 2
                    }
                }
            }
        }
    },
    'attributes': {
        'price': 30
    }
}

ddo5 = asset_service.generate_ddo(
    metadata, [service1], org3_account.address, child_dts=child_dts, verify=True)
asset_service.publish_dt(ddo5, org3_account)

msg = f'{org3_account.address}{ddo5.dt}'
msg_hash = add_ethereum_prefix_and_hash_msg(msg)
signature = org3_account.sign(msg_hash).signature.hex()

print(asset_service.check_service_terms(
    ddo5.dt, ddo3.dt, org3_account.address, signature))

asset_service.grant_dt_perm(ddo3.dt, ddo5.dt, org3_account)
asset_service.activate_cdt(ddo5.dt, ddo5.child_dts, org3_account)


task_id = job_service.create_task('test', 'test_task', org3_account)
job_id = job_service.add_job(task_id, ddo4.dt, org3_account)
job_id = job_service.add_job(task_id, ddo4.dt, org3_account)

msg = f'{org3_account.address}{job_id}'
msg_hash = add_ethereum_prefix_and_hash_msg(msg)
signature = org3_account.sign(msg_hash).signature.hex()

print(job_service.check_remote_compute(ddo4.dt, ddo3.dt,
                                       job_id, org3_account.address, signature))

job_id = job_service.add_job(task_id, ddo5.dt, org3_account)

found = tracer_service.trace_dt_lifecycle(ddo1.dt, prefix=[])
job_list = tracer_service.job_list_format(found)
print(job_list)
tree = tracer_service.tree_format(found)
if tree:
    tracer_service.print_tree(tree, indent=[], final_node=True)


print(tracer_service.get_marketplace_stat())
print(asset_service.get_dt_details(ddo4.dt))
print(asset_service.get_dt_marketplace())