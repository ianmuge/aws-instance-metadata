from flask import Flask, render_template, jsonify,request
import boto3
import json
def get_cfg(file):
    with open(file) as json_file:
        cfg=json.load(json_file)
    return cfg
app = Flask(__name__)
aws_cfg=get_cfg('cfg.json')

def get_session(region):
    return boto3.session.Session(region_name=region)
def get_client(client):
    session = get_session(aws_cfg["aws_region"])
    return session.client(client,
                          aws_access_key_id = aws_cfg["aws_access_key_id"],
                          aws_secret_access_key = aws_cfg["aws_secret_access_key"]
                          )


@app.route('/')
def get_instances():
    try:
        client = get_client('ec2')
        instances = client.describe_instances()
        return render_template('index.html', instances=instances,count=len(instances['Reservations']))
    except Exception as exc:
        app.logger.error("Exception Raised: {0}".format(exc))
        return "Exception Raised: {0}".format(exc)

@app.route('/instances',methods=['POST'])
def filter_instances():
    try:
        client = get_client('ec2')
        app.logger.info(request.get_data())
        filter_name = request.form['filter_name']
        filter_value = request.form['filter_value']
        tag_key=request.form['tag_key']
        custom_filter=request.form['custom_filter']
        if filter_name=="tag" and tag_key:
            filter_name=filter_name+":"+tag_key
        elif filter_name=="custom" and custom_filter:
            filter_name=custom_filter

        if filter_value and filter_name:
            instances=client.describe_instances(
                Filters=[
                    {
                        'Name': filter_name,
                        'Values': [filter_value]
                    }
                ]
            )
        else:
            instances = client.describe_instances()
        data={
            "count": len(instances['Reservations']),
            "instances": instances
        }
        return data
    except Exception as exc:
        app.logger.error("Exception Raised: {0}".format(exc))
        return "Exception Raised: {0}".format(exc)
# @app.route("/test")
# def test():
#     ec2 = boto3.client('ec2')
#     response = ec2.describe_instances()
#     ec2_res = boto3.resource('ec2')
#     instance = ec2_res.Instance(response["Reservations"][0]["Instances"][0]["InstanceId"])
#
#     return (instance.report_status())
if __name__ == '__main__':
    app.run(debug=True)
