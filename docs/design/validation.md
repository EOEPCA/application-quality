# Validation Plan

## Introduction

This validation plan defines the scenarios that must be executed to verify that the Application Quality Service, resulting from the work on the Application Quality BB, is behaving as expected.

## Test Cases

### User Authentication and Access Control

This test case verifies the ability for users to access the Application Quality Service.

#### Scenario: Access as anonymous user

This scenario verifies the following:

- Anonymous users visiting the Application Quality Web Portal:
  - may see the home page, including the links to the user manual, the dashboards and the GitHub repository
  - may access the login form
  - may access the list of available analysis tools and display their properties
  - may not access the list of available pipelines, nor the executions and reports
- Anonymous users may not access the Application Quality Dashboards


#### Scenario: Access as authenticated user

- Users may login using the EOEPCA IAM BB (if integrated) to access the Application Quality Web Portal.
- Users may login using the EOEPCA IAM BB (if integrated) to access the Application Quality Dashboards.
- Users authenticated in the Application Quality Web Portal:
  - may access the list of default analysis pipelines
  - may define and edit custom analysis pipelines
  - may access their custom analysis pipelines
  - may not access analysis pipelines created by other users
  - may execute analysis pipelines, monitor their execution and access the execution reports
- Users authenticated in the Application Quality Dashboards:
  - may access the dashboards displaying information about the pipeline executions, the execution-specific dashboard and the report-specific dashboards


### Analysis Pipelines Creation, Editing and Deletion

This test case focuses on the ability for authenticated users to create, edit and delete custom analysis pipelines.


#### Scenario: Creation of Customer-Defined Pipeline

This scenario verifies that an authenticated user may create new analysis pipelines.

- The user must be able to select multiple analysis tools.
- The user must be able to provide a default value for each analysis tool parameter.
- The customer-defined pipelines must persist after a page refresh or a logout/login cycle.

#### Scenario: Editing of Customer-Defined Pipeline

This scenario verifies that an authenticated user may edit the analysis pipelines they have created.

- The user must be able to add and remove analysis tools from the pipeline definition.
- The user must be able to modify the default values.
- The modified customer-defined pipelines must persist after a page refresh or a logout/login cycle.

#### Scenario: Customer-Defined Pipeline Deletion

This scenario verifies that an authenticated user may delete analysis pipelines they have created.

- The user must be able to delete a pipeline they have created.
- The user must not be able to delete a system-defined pipeline (provisioned by default).
- The deleted pipelines must not re-appear after a page refresh or a logout/login cycle.

### Manual Execution of Analysis Pipelines

This test case focuses on the ability to execute analysis pipelines manually, via the Application Quality Web Portal.

#### Scenario: Analysis Pipeline Execution

This scenario verifies that an authenticated user may execute analysis pipelines using their own parameters.

- The user must be able to select an analysis pipeline, enter execution parameters, and request its execution.

#### Scenario: Analysis Pipeline Execution Monitoring

This scenario verifies that an authenticated user may monitor the pipeline executions they have requested, and access the generated reports.

- The user must be able to list the ongoing and past pipeline executions.
- The user must be able to visualise the pipeline execution details, including the input parameters and the execution times.
- The user must be able to visualise the resources consumed by a pipeline execution, after its completion.
- The user must be able to visualise the generated analysis reports, after the completion of the pipeline execution.


### Visualisation Dashboards

This test case focuses on the access and use of the Application Quality Dashboards component.

#### Scenario: Navigation from the Web portal

This scenario verifies that an authenticated user may navigate from the Application Quality Web Portal to the Dashboards.

- The user must be able to navigate from the Web portal to the Dashboards home page.
- The user must be able to navigate from the Web portal to a dedicated pipeline execution dashboard.
- The user must be able to navigate from the Web portal to a dedicated analysis report dashboard.

#### Scenario: Default Visualisation Dashboards

This scenario verifies that an authenticated user may access the default dashboards to visualise pipeline executions data and analysis reports.

- The user must be able to access a dashboard that provides statistical information about the past and on-going pipeline executions.
- The user must be able to list the past and on-going pipeline executions.
- The user must be able to access a dashboard that provides information about a specific pipeline execution.
- The user must be able to list the analysis tools executed in a specific pipeline execution.
- The user must be able to access dashboards visualising the analysis reports.

#### Scenario: Custom Visualisation Dashboards

This scenario verifies that an authenticated user may create custom dashboards for visualising pipeline executions data and analysis reports.

- The user must be able to use the Dashboards component (Grafana) to create new visualisation panels.
- The user must be able to use the Dashboards component (Grafana) to create new dashboards and integrate default and custom visualisation panels.


### Analysis Pipelines Execution Automation

This test case will be specified when the integration with the Notification and Automation services will take place.
