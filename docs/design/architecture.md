# Architecture

The *Application Quality* BB integrates a number of modules that together implement its three main components: Development Best Practice, Application Quality Tooling and Application Performance.

This figure depicts the main constituents of the *Application Quality* BB and its external interfaces:

![Application Quality Service High-Level Architecture](../img/application-quality-bb-architecture.png)

The Building Block includes the following sub‑components:

- The *Application Quality Database* is used to store the data collected and generated in the Building Block, including:
  - The definition of the analysis tools available for integration within automated pipelines (expressed as CWL CLTs). The tools will allow performing various tasks: code quality (flake8, SonarQube), security (Bandit), documentation generation (Sphinx, Swagger), dependency analysis (pyenv, pipreqs), unit tests (pytest), etc.
  - The definition of the pipelines (expressed in CWL). Note: each pipeline will start with a job that clones (stage-in) the application project files to make them available to the analysis tools that are executed next.
  - The pipeline execution requests (triggers) and all the information collected during their execution.
- The *Application Quality Web Portal* (front-end) allows the operators to manage (register/create, edit, delete) analysis tools and pipelines.
- The *Application Quality API* is the back-end service responsible for serving the data to the Web Portal and for communicating with the database.
- The *Application Quality Engine* orchestrates the execution of the pipelines. Its main tasks are as follows:
  1. The Engine listens for pipeline execution requests on a dedicated notification channel.
  1. When an analysis request is received, it retrieves the appropriate pipeline definition from the database, renders the CWL file (especially providing the input values) and submits the resulting CWL document to the CWL Runner.
  1. During and upon completion of the pipeline executions, it collects the status and results and stores them in the database.
  1. In order to perform the performance analysis, it executes applications (processing workflows) in a test environment and collects the execution metrics (execution times, resources consumed, etc.) Note: This may be done by deploying and executing the applications using the [EOEPCA ADES](https://eoepca.readthedocs.io/projects/deploy/en/stable/eoepca/ades-zoo/) provided it allows targeting dedicated worker nodes and provided it gives access to the execution metrics.
  1. The Engine sends notifications through dedicated channels to inform the requesters about the progress. If the Notification Service allows creating channels on-the-fly with hierarchical subjects, a new channel will be created for each running pipeline.
- The *CWL Runner* runs and manages the pipeline life-cycle in the Kubernetes cluster. The [Calrissian](https://duke-gcb.github.io/calrissian) software product
is selected to implement this module.

Each individual tool that may be integrated in the Development Best Practice and Application Quality pipelines will be containerized and specified in CWL "CommandLineTool" resources. They will share a common subset of input and output parameters. Additional inputs may be used to specifically control the behaviour of each tool.

>**Note**: The architecture diagram above does not represent the interactions with external services initiated by the Application Quality pipelines. For example, at the beginning of a pipeline, the application code is fetched from GitHub. This is not performed by a BB component but in a pipeline task. The same applies to the other pipeline tasks that need to communicate with external services to perform their job.
