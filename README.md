# Plan for auto redeploy/rollback

## Use Docker tags for version control
Follow the format<br>
```<image>:<v#>```<br>
```owens518/gc_kv_store:v1```<br>
Every new push to docker hub will increment the image tag.

## Redeploy
Use the following command to list details of the instance group:<br>
```gcloud compute instance-groups managed list --project=kvproject-405420 --zones=us-central1-c```<br>
This will return the following output:
```
NAME: key-val-group-inst
LOCATION: us-central1-c
SCOPE: zone
BASE_INSTANCE_NAME: key-val-group-inst
SIZE: 2
TARGET_SIZE: 2
INSTANCE_TEMPLATE: key-val-template-1
AUTOSCALED: yes
```
Get the instance template name from the output, and the trailing number will indicate the version for version control.

**Create a new Template**<br>
We can then create a new template to redeploy with using the following command:<br>
```
gcloud compute instance-templates create-with-container key-val-template-2 \
    --region=us-central1 \
    --machine-type=e2-micro \
    --container-image=owens518/gc_kv_store:v2 \
    --container-env=DB_USERNAME=kvdb_user,DB_PASSWORD=PASSWORD \
    --tags=http-server,lb-health-check \
    --labels=env=prod,app=myapp \
    --scopes=https://www.googleapis.com/auth/cloud-platform
```
Notice how the new template trails with 2 and the new docker image tag is 2.
Come up with some way to run the previous command to get the current _INSTANCE_TEMPLATE_ and extract the current version from the name.
Increment the version and then push to docker hub with new version and then create the new instance template with the updated version.

**Update Instance Group**<br>
Once the new instance-template is created, run the following command to initiate a rolling-action update.
This will drain the instances and replace them with the new version.<br>
```
gcloud compute instance-groups managed rolling-action start-update INSTANCE_GROUP_NAME \
    --version=template=NEW_INSTANCE_TEMPLATE_NAME \
    --zone=us-central1-c

```

## Rollback
For rollback, simply repeat the steps for redeploy, but decrement the version control.<br>
Also, set the max-unavailable to 100% since we are assuming all nodes are already down.
```
gcloud compute instance-groups managed rolling-action start-update INSTANCE_GROUP_NAME \
    --version=template=OLD_INSTANCE_TEMPLATE_NAME \
    --max-unavailable=100% \
    --zone=us-central1-c

```
