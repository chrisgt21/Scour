import boto3, json, datetime, sys, os


type = os.environ.get('TYPE', 'all')
resource = os.environ.get('RESOURCE', '')
action = os.environ.get('ACTION', '')
key = os.environ.get('AWS_ACCESS_KEY')
secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('AWS_REGION')
session = os.environ.get('AWS_SESSION_TOKEN', '')


results = []

print(session)
if(session == ''):
    client = boto3.client('iam',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        aws_session_token=session
    )

if(resource == '' and action == ''):
    raise Exception('Cannot have both ACTION and RESOURCE empty. You must define either one or both.')

def find(type, resource, action):
    count = 0

    resourceSearch = resource
    actionSearch = action

    response = client.list_policies(
        Scope='Local',
        OnlyAttached=False,
        MaxItems=1000
    )

    total = len(response['Policies'])

    for policy in response['Policies']:
        #print(count, "_of_", total, end='\r')

        name = policy['PolicyName']
        arn = policy['Arn']
        versionId = policy['DefaultVersionId']

        response2 = client.get_policy_version(
            PolicyArn=arn,
            VersionId=versionId
        )


        iamPolicy = response2['PolicyVersion']['Document']
        #evaluate_policy(iamPolicy)
        search_policy(type, iamPolicy, resourceSearch, actionSearch, name)
        count = count + 1
        sys.stdout.write("\rScaning Policies: {0}/{1}".format(count, total))
        sys.stdout.flush()

    print()
    print(json.dumps(results, indent=2))



def evaluate_policy(policy):
    print(policy['Version'])

def search_policy(type, policy, resourceSearch, actionSearch, policyName):
    resourceFinding = False
    actionFinding = False

    for obj in policy['Statement']:
        if(resourceSearch != ''):
            if(resourceFinding == False):
                if resourceSearch in obj['Resource']:
                    #print("%s in resource definition" % resourceSearch)
                    add_finding(type, policyName, resourceSearch)
                    resourceFinding = True

        if(actionSearch != ''):
            if(actionFinding == False):
                if actionSearch in obj['Action']:
                    #print("%s in action definition" % actionSearch)
                    add_finding(type, policyName, actionSearch)
                    actionFinding = True

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def add_finding(type, finding, finding_type):
    obj = {'scour_type': type, 'finding_policy': finding, 'finding_type': finding_type}
    results.append(obj)

if __name__ == '__main__':
    find(type, resource, action)