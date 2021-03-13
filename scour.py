import boto3, json, datetime, click, sys
import PySimpleGUI as sg

results = []


@click.group(chain=True)
def cli():
    pass


@cli.command()
@click.option('--profile', default='default', help='This is to define which AWS profile to use.')
@click.option('--type', default='all', help='Options are: IAM, KMS, S3, or ALL')
@click.option('--resource', default='None', help='Enter the resource you want to scour through policies for.')
@click.option('--action', default='None', help='Enter the action you want to scour through policies for.')
def find(profile, type, resource, action):
    """Helps find what you're looking for..."""

    count = 0
  
    session = boto3.Session(profile_name=profile)
    client = session.client('iam')

    resourceSearch = resource
    actionSearch = action

    response = client.list_policies(
        Scope='Local',
        OnlyAttached=False,
        MaxItems=1000
    )

    total = len(response['Policies'])

    for policy in response['Policies']:
        count = count + 1
        sys.stdout.write("\r{0}/{1}".format(count, total))
        sys.stdout.flush()
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
    print()
    print(json.dumps(results, indent=2))



def evaluate_policy(policy):
    print(policy['Version'])

def search_policy(type, policy, resourceSearch, actionSearch, policyName):
    #print()
    #print(policyName)
    #print(actionSearch)
    #print(resourceSearch)
    for obj in policy['Statement']:
        if(resourceSearch != 'None'):
            if resourceSearch in obj['Resource']:
                #print("%s in resource definition" % resourceSearch)
                add_finding(type, policyName, resourceSearch)

        if(actionSearch != 'None'):
            if actionSearch in obj['Action']:
                #print("%s in action definition" % actionSearch)
                add_finding(type, policyName, actionSearch)

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def add_finding(type, finding, finding_type):
    obj = {'scour_type': type, 'finding_policy': finding, 'finding_type': finding_type}
    results.append(obj)

if __name__ == '__main__':
    cli()