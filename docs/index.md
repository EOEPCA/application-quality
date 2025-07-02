# Introduction

The purpose of the **Application Quality** BB is to support the evolution of a scientific algorithm
(processing workflow) from a research project to one that can be utilised in a production
environment. To achieve this, the *Application Quality* BB provides tools for verifying non-functional
requirements - including code quality, software development best practice for open reproducible
science, and optimisation through performance testing.

The *Application Quality* BB delivers a set of services that can be used in automated pipelines that
are linked to the source and runtime resources of processing workflow developments. Dedicated test
environments provide representative sandboxed execution services that can be used as a gateway to
production.

See also the [Application Quality BB in the EOEPCA System Architecture](https://eoepca.readthedocs.io/projects/architecture/en/latest/reference-architecture/application-quality-BB/).

## About the Application Quality Building Block

The *Application Quality* BB provides tooling that supports and encourages the development of
Processing Workflows in accordance with software engineering best practices – whilst providing
an environment to test their workflow execution and optimise the code.

The *Application Quality* BB is modular and integrates a high number of third-party FOSS tools and
applications that are traditionally used by software developers to verify, optimise and document
their code.

## Capabilities

The capabilities of the *Application Quality* BB may be grouped in the following categories, each of
which is implemented by a different set of tools that may be integrated into automated development
pipelines:

### Development Best Practice

Analysis of source code and repositories for code quality, and adherence to development best
practices for reproducible open science.
Users are provided with a set of services that allow linking their development resources – for
example, connecting the tooling to their Git and container image repositories. Static Code Analysis
tooling (e.g. SonarQube) is used to analyse connected git repositories, report code quality issues,
detect security vulnerabilities and advise best practice.s

### Application Quality Tooling

Set of tools that complement the Development Best Practice tools. Examples include vulnerability
scanning of application runtime artefacts such as containers.

### Application Performance

Integrated tools supporting performance testing and optimisation of processing workflows, supported
by test execution environments.
To implement this capability, the *Application Quality* BB provides an environment in which processing
workflows can be tested (executed). This test environment is sandboxed for development, such that
it cannot impact operational systems.
The test environment provides support for profiling, identifying bottlenecks and optimising
application code.

## Web-enabled Portal

The *Application Quality* BB provides a Web Portal through which the tooling is accessed.

Operators may use the Web Portal to manage the integrated tools, configure pipelines, and access
usage metrics.
Users may use the Web Portal to monitor the execution of the pipelines and access the results.

## Analysis Dashboards

The *Application Quality* BB integrates with Grafana to visualize the various reports and metrics generated during pipeline executions.

Default panels and dashboards are provided. Users may use the provided panels to create new dashboards.

## Pipeline Automation

The *Application Quality* BB supports the automated execution of pipelines triggered by updates to
the applications resources (git, containers, etc.), as reported by the Automation Service via the
Notification Service.
