# Pipeline Execution Automation

## Introduction

Triggers may be defined to automate the execution of analysis pipelines when external events occur.

The events must be delivered as [CloudEvents](https://github.com/cloudevents/spec) to the *Application Quality* service backend.

An implementation of this mechanism uses the [Knative Eventing](https://knative.dev/docs/eventing/) middleware, powering the *Notification and Automation* BB, and the [Webhook Source function](https://github.com/EOEPCA/na-webhook-source), implemented in the context of EOEPCA.

## Deployment and Setup

### Knative and the Webhook Source Function

The procedures for deploying these components are described in their respective documentation:

* Knative Eventing: https://knative.dev/docs/eventing/
* *Notification and Automation* BB: https://eoepca.readthedocs.io/projects/notification-automation/en/latest/
* Webhook Source: https://github.com/EOEPCA/na-webhook-source#deployment

### Application Quality Service Trigger

A *Knative Eventing Trigger* resource must be created in the Kubernetes environment to tell the Knative Broker to deliver the events having a given type (i.e. matching a filter) to the *Application Quality* backend (the Subscriber).

The Helm Charts template for the Knative Trigger can be found in the [GitHub Application Quality repository](https://github.com/EOEPCA/application-quality/blob/reference-deployment/helm/templates/api-notifications.yaml).

This is configured with the following values:

```yaml
  notifications:
    enabled: true
    middleware: "knative"
    # The Knative Trigger is created in the same namespace as the Broker
    brokerName: "default"
    brokerNamespace: "na"
    # Also used as type prefix for incoming events
    channelPrefix: "org.eoepca.application-quality"
    responseSource: "/eoepca/application-quality"
    responseTypePrefix: "org.eoepca.application-quality.response"
```

The example *Trigger* resource, below, considers the following:

* The *Broker* to connect to is deployed in the `na` namespace and is named `default`.
* The Webhook is configured to process events issued by GitLab and GitHub. The Webhook automatically sets the appropriate event type (e.g. `org.eoepca.webhook.github.push`) in the CloudEvents.
* The *Application Quality* service is deployed in the `application-quality` namespace. The backend pod name is `application-quality-api` and the CloudEvents must be delivered to the `/api/events` endpoint.

!!! note
    The *Trigger* must be deployed in the same namespace as the *Broker*.

```yaml
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  labels:
    argocd.argoproj.io/instance: application-quality-core
    eventing.knative.dev/broker: default
  name: org.eoepca.application-quality.events
  namespace: na
spec:
  broker: default
  filters:
  - any:
    - prefix:
        type: org.eoepca.webhook.github.
    - prefix:
        type: org.eoepca.webhook.gitlab.
  subscriber:
    ref:
      apiVersion: v1
      kind: Service
      name: application-quality-api
      namespace: application-quality
    uri: /api/events/
```

### GitHub Webhooks

GitHub repositories must be configured to send events when certain actions are executed.

Steps:

1. In the GitHub Web interface, access the **Webhooks** page in the repository **Settings**.
2. Click on **Add Webhook**. Use your passkey if asked.
3. In the form, do the following:
   - **Payload URL**: *Public address of the Knative Webhook Source (ingress URL)*
   - **Content type**: Select `application/json`
   - **Secret**: *The secret string configured in the Knative Webhook Source*
   - **Enable SSL Verification**: *It is recommended to enable this*
   - **Which events...?** => Let me select individual events.
   - In the events list, select **Pull requests** and **Pushes**.
   - **Active**: *Check to enable the webhook*
4. Click on **Add webhook**.

Once created, the Webhook definition can still be edited and the recent deliveries may be inspected. Recent deliveries may also be redelivered for testing purpose.

GitHub Webhook Manage page:

![GitHub Webhook Manage Page](img/user-manual/github-webhook-manage.png)

GitHub  Webhook Recent Deliveries:

![GitHub Webhook Recent Deliveries](img/user-manual/github-webhook-recent-deliveries.png)


## Analysis Pipeline Triggers

The above *Trigger* resource asks the Broker to deliver any event issued by GitLab and GitHub to the Application Quality service.

The Analysis Pipelines that must be executed and the conditions to do so are configured in the Application Quality Web portal.

The **Pipeline Triggers** page allows creating and managing Analysis Pipelines Triggers:

![Analysis Pipelines Triggers Page](img/user-manual/app-analysis-pipelines-triggers.png)

Click on the edit icon to display the creation form:

![Analysis Pipelines Trigger Creation Form](img/user-manual/app-analysis-pipelines-trigger-creation.png)

Give the Trigger a name, description and status. These are mandatory but have no impact on the service behaviour.

The **Enabled** switch, at the top, allows disabing a Trigger (matching events are then ignored), without deleting it.

Select an *Event Type* (e.g. "GitHub Push Event"), and the Analysis Pipeline to execute when a matching event is received.

!!! note
    Pre-defined *Event Types* are created automatically in the backend database. More types may be added by an administrator.

The form also includes two JSON fields: the first one allows specifying a CQL2 Filter and the second one is for providing Default Input Parameters.

The CQL2 Filter applies on the CloudEvent properties found in the event body.

This example filters indicates that the selected Analysis Pipeline must be executed if the event is issued for the `application-quality` repository in the `EOEPCA` organisation, that the event is related to the `backend` branch, and the original action has been done by GitHub user `bevalentin`:

```json
	
{
  "op": "and",
  "args": [
    {
      "op": "=",
      "args": [
        {
          "property": "repository.full_name"
        },
        "EOEPCA/application-quality"
      ]
    },
    {
      "op": "=",
      "args": [
        {
          "property": "ref"
        },
        "refs/heads/backend"
      ]
    },
    {
      "op": "=",
      "args": [
        {
          "property": "sender.login"
        },
        "bevalentin"
      ]
    }
  ]
}
```

The following example defines default parameters for the selected pipeline:

```json
{
  "parameters": {
    "ruff_subworkflow": {
      "ruff": {
        "verbose": false
      },
      "filter": {
        "regex": ".*\\.py"
      }
    },
    "clone_subworkflow": {
      "clone": {
        "repo_url": "https://github.com/EOEPCA/application-quality",
        "repo_branch": "backend"
      }
    },
    "bandit_subworkflow": {
      "bandit": {
        "verbose": false
      },
      "filter": {
        "regex": ".*\\.py"
      }
    },
    "flake8_subworkflow": {
      "filter": {
        "regex": ".*\\.py"
      },
      "flake8": {
        "verbose": false
      }
    },
    "pylint_subworkflow": {
      "filter": {
        "regex": ".*\\.py"
      },
      "pylint": {
        "disable": "E0401,C0114,C0115,C0116",
        "verbose": false,
        "errors_only": false
      }
    },
    "notebook-bp-validator_subworkflow": {
      "filter": {
        "regex": ".*\\.ipynb"
      },
      "notebook-bp-validator": {
        "schema": "eumetsat",
        "abspath": false
      }
    }
  }
}
```

!!! note
    A more user-friendly form will be provided in a future version of the Application Quality Service Web portal.
