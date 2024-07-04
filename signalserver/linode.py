from linode_api4 import LinodeClient, Instance
from os import environ
import uuid

'''
%load_ext dotenv
%dotenv
'''
# Create a Linode API client
client = LinodeClient(environ.get("LINODE_TOKEN"))

# Get a list of all Linode instances by Tag "scct"
instances = client.linode.instances(Instance.label.contains("scct-dev"))
for x in instances:
    print(x.label, x.status, x.id)

if len(instances) == 3:
    print("All instances are running")
    exit(0)

# Create a new Linode instance
linode, root_pass = client.linode.instance_create(
    ltype="g6-nanode-1",
    region="us-ord",
    tags=["scct"],
    label=f"scct-dev-{str(uuid.uuid4())}",
    image="linode/ubuntu24.04",
    authorized_keys=[environ.get("SSH_KEY")],
    stackscript_id=1408160,
    stackscript_data={"host": environ.get("DEV_IP")}
)

# dev_instances = client.linode.instances(Instance.label.contains("scct-dev"))
# for x in dev_instances:
#     x.delete()
