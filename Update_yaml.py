import yaml

with open('service.yaml', 'r') as stream:
    try:
        service = yaml.safe_load(stream)
        # Now 'data' is a Python dictionary containing the contents of the YAML file
    except yaml.YAMLError as exc:
        print(exc)

service['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/maxScale'] = '100'
service['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/minScale'] = '100'
service['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = '1000m'
service['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = '512Mi'

updated_yaml_content = yaml.safe_dump(service, default_flow_style=False)

with open('service.yaml', 'w') as file:
    file.write(updated_yaml_content)
