import yaml

with open("config.yaml", 'r') as stream:
    try:
        #print(yaml.load(stream))
        a = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        
print a

definitions = {"one" : 1, "two" : 2, "three" : 3}
actions = {"run" : "yes", "print" : "no", "report" : "maybe"}

output = yaml.dump(actions, default_flow_style=False, explicit_start=True)
output += yaml.dump(definitions, default_flow_style=False, explicit_start=True)

print output


