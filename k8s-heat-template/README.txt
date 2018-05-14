#############################################################################################

## Steps for using HOT k8s-cluster-v1.7.0-v1.yaml to create k8s cluster with HA master nodes

   For Prod use template: k8s-prod-cluster-v1.7.0-v1-1.yaml

#############################################################################################

Instructions to use:

1) Git clone below file from public Stash repository.

	https://stash.exponential.com/projects/EXS/repos/k8s-heat-template/browse/k8s-cluster-v1.7.0-v1.yaml

2) Login to Expostack (expostack.tf-net.tribalfusion.com) in Engineering Development Project.

3) Click on launch stack under below path
	Project -> Orchestration -> Stacks

4) Click on <Choose file> under Template Source and browse to file k8s-cluster-v1.7.0-v1.yaml.

5) Enter "StackName" & AD Password.

6) Choose flavor for k8s node & workers. No need to change master node image. Choose app image for worker nodes i.e "CentOS7 Heat DG3 Dev Generic"

7) Mention number of worker nodes in num_workers

8) Click on Launch button once you have updated spreadsheet.

9) The stack will show completed in 9/10min & IP details will show in overview tab.
    The k8s nodes should come up by 20/25min.


Note: Use production temaplte k8s-prod-cluster-v1.7.0-v1-1.yaml in Engineering Produciton Project & prod images like "CentOS7 Prod Heat"
