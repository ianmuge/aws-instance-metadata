from flask import Flask
import boto.ec2
import json
app = Flask(__name__)
def get_cfg(file):
    with open(file) as json_file:
        cfg=json.load(json_file)
    return cfg

@app.route('/')
def get_instances():
    aws_cfg=get_cfg('cfg.json')

    conn = boto.ec2.connect_to_region(aws_cfg["aws_region"],
                                      aws_access_key_id = aws_cfg["aws_access_key_id"],
                                      aws_secret_access_key = aws_cfg["aws_secret_access_key"])
    reservations = conn.get_all_reservations()

    instances=[]
    for res in reservations:
        for instance in res.instances:
            inst = {}
            inst["instance_type"]=instance.instance_type
            inst["placement"]=instance.placement
            inst["image_id"]=instance.image_id
            instances.append(inst)

    return json.dumps(instances)
@app.route("/<instance_id>")
def get_instance_meta(instance_id):
    aws_cfg = get_cfg('cfg.json')

    conn = boto.ec2.connect_to_region(aws_cfg["aws_region"],
                                      aws_access_key_id=aws_cfg["aws_access_key_id"],
                                      aws_secret_access_key=aws_cfg["aws_secret_access_key"])
    instance=conn.get_instance_attribute(instance_id=instance_id)
    return instance_id
@app.route("/test")
def test():
    import boto3
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    ec2_res = boto3.resource('ec2')
    instance = ec2_res.Instance(response["Reservations"][0]["Instances"][0]["InstanceId"])

    return json.dumps(instance.report_status())
