# Remote Pipeline Execution

## Remote Pipeline Execution using the Backend API

### Setup

Note: this method requires local users to be created in the Application Quality backend database. It does not allow using users registered with the IAM / OIDC component.

For security reasons, the Application Quality backend API should only accept requests issued from the frontend component (i.e. the origin of the requests must match the scheme, domain and port used to access the frontend). When deployed using Helm, this is configured in the [`web.publicUrl` value](https://github.com/EOEPCA/application-quality/blob/main/helm/values.yaml).

If necessary, the backend may be configured to accept requests from additional hosts such as GitHub. Use the Helm value `api.additionalAllowedHosts` to indicate which hosts (in addition the main public URL) may access the API. The value must contain a comma-separated list of domain names.


### GitHub Workflow

A GitHub Workflow that uses the Application Quality backend API to execute pipelines may be found in a test repository: [eoepca-aqbb-notebooks-testing.yml](https://github.com/SpaceApplications/eoepca-aqbb-test-files/blob/main/.github/workflows/eoepca-aqbb-notebooks-testing.yml).

The test workflow performs the following "jobs":

* Job 1 obtains an access token using user credentials stored in GitHub secrets and uses it to retrieve pipeline details.
* Job 2 uses the token to trigger the execution of the Notebook static validation pipeline.
* Job 3 uses the token to trigger the execution of the Notebook execution testing pipeline.

Jobs 2 and 3 are executed after the completion of Job 1. They prepare pipeline execution payloads and submit them to the backend API. They end immediately, without waiting for the completion of the executed pipelines.


### Test

The GitHub workflow is configured to be executed automatically on any `push` events. It may also be executed on-demand via the Actions Workflow page (`workflow_dispatch` event type).


## Remote Pipeline Execution using Knative and CloudEvents

The objective is to allow requesting the execution of analysis pipelines asynchronously, by sending execution requests through the Notification service implemented in the Notification & Automation Building Block.

The underlying technology used by the N&A BB is *Knative*, and more previsely *Eventing* and *Serving*.

This feature requires Knative Eventing to be properly deployed in the Kubernetes cluster.


### Setup

The event-based execution requests rely on the existence of a Knative Eventing `Broker` (optionally configured using a `ConfigMap`) and a Knative Eventing `Trigger`:

* If no broker is already present:
  * Optionally: create a `ConfigMap` to provide the message broker custom configuration.
  * Create a `Broker` that refers the `ConfigMap`.
* Create a `Trigger`. This binds the broker with the service that must receive the notifications (CloudEvents).
  The trigger may also specify `filters` to ensure the events are delivered to the appropriate services.

Here, the `ConfigMap` tells that the broker must be of type `InMemoryChannel`.

Note: This broker type must not be used in production as it does not provide persistence, does not guarantee ordering and does not attempt redeliveries. Also, rejected messages are ignored.

```yaml
apiVersion: v1
kind: ConfigMap
data:
  name: config-br-default-channel
  namespace: knative-eventing
  channel-template-spec: |
    apiVersion: messaging.knative.dev/v1
    kind: InMemoryChannel
```

The `Broker` indicates that its configuration must be retrieved from the configmap defined above:

```yaml
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: primary
  namespace: default
spec:
  config:
    apiVersion: v1
    kind: ConfigMap
    name: config-br-default-channel
    namespace: knative-eventing
  delivery:
    retry: 2
```

The `Trigger` binds to the broker defined above, specifies a filter (here: two event type prefixes), and identifies the service endpoint to be called when a matching event is sent to the broker:

```yaml
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: org.eoepca.application-quality.events
  namespace: default
spec:
  broker: primary
  # filter: {}
  filters:
  - any:
    - prefix:
        type: org.eoepca.application-quality.probes.
    - prefix:
        type: org.eoepca.application-quality.event.
  subscriber:
    ref:
      apiVersion: v1
      kind: Service
      name: application-quality-api
      namespace: application-quality
    uri: /api/events/
```


### Testing Scripts

The following test scripts may be used to verify that the Application Quality backend component receives the cloudevents sent to the broker.

Note: These example scripts use the internal address of the Knative broker: `http://broker-ingress.knative-eventing.svc.cluster.local`. They must thus be executed from inside the Kubernetes cluster. Should an ingress be created to provide remote access to the broker, the scripts may be executed using the address of the ingress.


#### Health Check

This script sends an event of type `org.eoepca.application-quality.probes.health` to the broker. As its type matches the filter in the trigger, the event is delivered to the Application Quality backend. This replies with an `OK` response.


```bash
#!/bin/sh

BROKER_INGRESS_URL=http://broker-ingress.knative-eventing.svc.cluster.local

BROKER_HOST=knative-broker.eoepca-plus-develop

CHANNEL_NAME=primary
CHANNEL_NAMESPACE=default

EVENT_ID=123
EVENT_TYPE=org.eoepca.application-quality.probes.health

MSG=$(cat <<EOF
{
  "message": "Checking your health!",
  "test": $EVENT_ID
}
EOF
)

echo Broker Host: $BROKER_HOST
echo Channel Name: $CHANNEL_NAME
echo Channel Namespace: $CHANNEL_NAMESPACE
echo Event Type: $EVENT_TYPE
echo Message: $MSG

curl -X POST $BROKER_INGRESS_URL/$CHANNEL_NAMESPACE/$CHANNEL_NAME \
     -H "Host: $BROKER_HOST" \
     -H "ce-id: $EVENT_ID" \
     -H "ce-specversion: 1.0" \
     -H "ce-type: $EVENT_TYPE" \
     -H "ce-source: curl" \
     -H "Content-Type: application/json" \
     -d "$MSG"

echo Done
```

#### Pipeline Execution

This script requests the execution of an analysis pipeline. It prepares a payload with the execution parameters (here: only the URL and branch of the Git repository to clone and analyse). The pipeline is identified using its internal unique identifier (here: `17` is the identifier of the *Notebook statis analysis pipeline*).

When received by the Application Quality backend, this initiates the execution of the pipeline and returns the identifier of the new pipeline execution (run).

Note: The Application Quality backend verifies that the user name provided in the request header `ce-user` matches an existing user. If not, the backend returns an error.

```bash
#!/bin/sh

BROKER_INGRESS_URL=http://broker-ingress.knative-eventing.svc.cluster.local:80

BROKER_HOST=knative-broker.eoepca-plus-develop

CHANNEL_NAME=primary
CHANNEL_NAMESPACE=default

EVENT_ID=123
EVENT_TYPE=org.eoepca.application-quality.events.pipeline.execute
EVENT_SOURCE=curl

# Pipeline 17 = Notebook static analysis pipeline
PIPELINE_ID=17

REPO_URL=https://github.com/SpaceApplications/eoepca-aqbb-test-files
REPO_BRANCH=main

# An existing local user
USER=event

MSG=$(cat <<EOF
{
  "parameters": {
    "clone_subworkflow": {
      "clone": {
        "repo_url": "$REPO_URL",
        "repo_branch": "$REPO_BRANCH"
      }
    }
  }
}
EOF
)

echo Executing Pipeline $PIPELINE_ID for User $USER
echo Checking Repository $REPO_URL \(Branch $REPO_BRANCH\)
echo Broker Host: $BROKER_HOST
echo Channel Name: $CHANNEL_NAME
echo Channel Namespace: $CHANNEL_NAMESPACE
echo Event Type: $EVENT_TYPE
echo Message: $MSG

curl -X POST $BROKER_INGRESS_URL/$CHANNEL_NAMESPACE/$CHANNEL_NAME \
     -H "Host: $BROKER_HOST" \
     -H "ce-id: $EVENT_ID" \
     -H "ce-specversion: 1.0" \
     -H "ce-type: $EVENT_TYPE" \
     -H "ce-user: $USER" \
     -H "ce-source: $EVENT_SOURCE" \
     -H "ce-subject: pipelines/$PIPELINE_ID" \
     -H "Content-Type: application/json" \
     -d "$MSG"

# Note: the broker only returns the response code, not custom header or data

echo Done
```