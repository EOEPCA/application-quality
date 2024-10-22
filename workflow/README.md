# Workflow Module: Code Quality Analysis and Reporting

This module is a Common Workflow Language (CWL) workflow designed to automate code quality analysis for Python repositories. It is used in a Django application and executed using [pycalrissian](https://terradue.github.io/pycalrissian/), which runs the workflow in a Kubernetes environment. The workflow analyzes a Git repository using **pylint** and **flake8**, generates reports, and sends them to a specified database via POST requests.

## Inputs

The workflow requires the following inputs:

- **`repo_url`**: The URL to a Git repository that will be cloned and analyzed.
- **`server_url`**: The address of the database where the pylint and flake8 reports will be saved.
- **`pipeline_id`**: A unique identifier used for organizing report files in the database.
- **`run_id`**: A run-specific identifier to distinguish between different runs within the same pipeline.

## Workflow Overview

1. **Clone Repository**: The specified `repo_url` is cloned.
2. **Run pylint and flake8**: 
   - Two sub-workflows run pylint and flake8 on the cloned repository.
   - Both generate code quality reports.
3. **Post Reports to Database**: Reports are sent to the `server_url` database using POST requests, with `pipeline_id` and `run_id` used to manage report storage.

## Running the Workflow

This workflow is normally executed within a Django app using **pycalrissian**, which handles the orchestration in a Kubernetes environment. Users do not typically run it directly. The app takes care of passing the inputs (`repo_url`, `server_url`, `pipeline_id`, `run_id`), executing the workflow, and processing the reports.

### Manual Execution (Using cwltool)

If manual execution is needed, you can run the workflow using **[cwltool](https://www.commonwl.org/user_guide/introduction/quick-start.html#installing-a-cwl-runner)** by providing inputs through the command line. However, you must modify the tool files to comment out or remove the `baseCommand` lines due to **cwltool** handling Docker ENTRYPOINT differently than Calrissian.

**Example of manual execution:**
```bash
cwltool workflow.cwl \
--repo_url https://github.com/example.git \
--server_url http://your-database-url/api/reports \
--pipeline_id 1234 \
--run_id run5678
```

Note: When using **cwltool**, ensure Docker is properly set up on your machine, as the tools rely on Docker containers for execution.
