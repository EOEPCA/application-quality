# Analysis Tools

## Overview

This chapter introduces the analysis tools integrated, or candidate for integration, into the *Application Quality* BB.

Each of these tools allows analysing and validating application code or execution artefacts from the quality, security, or performance perspective.

The analysis tools are pre-loaded in the database at deployment time (from an embedded fixture document). They may be edited directly in the database using the backend (Django) administration interface however this requires a proper understanding of how tools, workflows and pipelines are defined.

The available tools are listed with their details in the *Application Quality* Web interface. The same interface allows authenticated users to integrate the tools in custom pipelines. You will find the instructions in the Application Quality [User Manual](user-manual.md).

### How Analysis Tools Are Implemented and Executed

The tools in the *Application Quality* BB are implemented using the [Common Workflow Language](https://www.commonwl.org/user_guide/index.html) (CWL), and executed by [Calrissian](https://github.com/Duke-GCB/calrissian) and the reference implementation [cwltool](https://github.com/common-workflow-language/cwltool). The BB makes use of the [pycalrissian](https://github.com/Terradue/pycalrissian) Python library to setup and execute the analysis pipelines in the local Kubernetes cluster (possibly in a virtual cluster if this is option is activated).

Each tool is defined as a CWL `CommandLineTool` (CLT). These tools are typically invoked within a CWL `Workflow`, which orchestrates multiple `CommandLineTool` components. Some additional tools in these workflows handle auxiliary tasks such as filtering files from a cloned git repository or saving the analysis results to the database.

### How Tools are Parameterised

Most of the integrated tools support command line parameters that allow controlling their behaviour.

To allow using these parameters in analysis pipelines (through the UI or the API), the CLT in which the tool is integrated must define the corresponding inputs and use these inputs in the embedded scripts.

The sections below describe the parameters that have been implemented in the CLTs and can thus be used to parameterise the pipeline executions.

More parameters may be exposed as necessary by extending the definition of the CLTs in the database.

## Available tools

The following table organises the analysis tools per application type and per check type.

As can be seen, a number of tools are readily available. Feedback and requirements will be necessary to determine which tools will be integrated next.

|                       |                                                          Best Practices                                                          | Application Quality |                        Application Performance                         |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------- |
| **Python scripts**    | [Pylint](#pylint), [Ruff](#ruff), [Flake8](#flake8),<br>[SonarQube](#sonarqube) <sup>1</sup>,<br>[Coding BP for OSS](#coding-best-practices-for-open-source-software-development)                                     | [Bandit](#bandit)   | [Pytest](#pytest) <sup>2</sup>                                         |
| **Jupyter Notebooks** | [Ruff](#ruff), [SonarQube](#sonarqube) <sup>1</sup>,<br>[Notebook Best Practices Validator](#jupyter-notebook-best-practices-validator) |                     | [Papermill](#papermill)                                                |
| **AP CWL**            | [Application Package Validator](#application-package-validator)                                                                  |                     | [Calrissian](#calrissian) <sup>2</sup>                                 |
| **Docker**            |                                                                                                                                  | [Trivy](#trivy)     | [Kaniko](https://docs.gitlab.com/ci/docker/using_kaniko/) <sup>2</sup> |
| **Projects**          | [Coding BP for OSS](#coding-best-practices-for-open-source-software-development) |                     |                                                                        |
| **openEO**            |                                                                                                                                  |                     |                                                                        |

<sup>1</sup> Implementation in progress

<sup>2</sup> Candidate tool

## Tools description

### Development Best Practices

#### Pylint

Pylint is a static code analyser for Python 2 or 3. Pylint analyses your code without actually running it.  

It checks for errors, enforces a coding standard, looks for code smells, and can make suggestions about how the code could be refactored.

[🔗 Documentation](https://pylint.readthedocs.io/en/latest/user_guide/installation/index.html)

**Exposed parameters**

|     Name      |   Type    |                                                                                  Description                                                                                   |
| ------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `errors_only` | *boolean* | In error mode, messages with a category besides ERROR or FATAL are suppressed,<br>and no reports are done by default. Error mode is compatible with disabling specific errors. |
| `verbose`     | *boolean* | In verbose mode, extra non-checker-related info will be displayed.                                                                                                             |
| `disable`     | *string*  | Disable the message, report, category or checker with the given id(s).                                                                                                         |

#### Ruff

An extremely fast Python linter and code formatter, written in Rust.

[🔗 Documentation](https://docs.astral.sh/ruff/)

**Exposed parameters**

|   Name    |   Type    |       Description       |
| --------- | --------- | ----------------------- |
| `verbose` | *boolean* | Enable verbose logging. |

#### Flake8

Flake8 is a wrapper around these tools: *PyFlakes*, *pycodestyle*, *Ned Batchelder's McCabe script*.  
Flake8 runs all the tools by launching the single `flake8` command. It displays the warnings in a per-file, merged output.

[🔗 Documentation](https://flake8.pycqa.org/en/latest/)

**Exposed parameters**

|   Name    |   Type    |                Description                 |
| --------- | --------- | ------------------------------------------ |
| `verbose` | *boolean* | Increase the verbosity of Flake8’s output. |

#### Application Package Validator

This tool verifies the compliance of CWL files for EOEPCA Application Packages (AP CWL) against the requirements specified in the [OGC Best Practice for Earth Observation Application Package](https://docs.ogc.org/bp/20-089r1.html) document.

Each CWL file matching the filter is validated in a separate job, leading to the creation of individual analysis reports.

[🔗 Documentation](https://github.com/EOEPCA/app-package-validation#readme)

**Exposed parameters**

|     Name      |   Type   |                              Description                              |
| ------------- | -------- | --------------------------------------------------------------------- |
| `detail`      | *string* | Output detail (none&#124;errors&#124;hints&#124;all). Default: "hints". |
| `entry_point` | *string* | Name of entry point (Workflow or CommandLineTool)                     |

#### Jupyter Notebook Best Practices Validator

This tool aims at validating the notebooks against the [CEOS Jupyter Notebook Best Practice v1.1](https://ceos.org/document_management/Working_Groups/WGISS/Documents/WGISS%20Best%20Practices/CEOS_JupterNotebooks_Best%20Practice_v1.1.pdf) document.

[🔗 Documentation](https://github.com/EOEPCA/notebook-bp-validator#readme)

**Exposed parameters**

|   Name    |   Type    |                  Description                  |
| --------- | --------- | --------------------------------------------- |
| `abspath` | *boolean* | Uses absolute paths in output.                | 
| `schema`  | *string*  | Supported values: 'eumetsat' or 'schema.org'. | 

#### SonarQube

SonarQube Server is an on-premise analysis tool designed to detect coding issues in 30+ languages, frameworks, and IaC platforms.

[🔗 Documentation](https://docs.sonarsource.com/sonarqube-server/latest/)

**Exposed parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| -    | -    | -           |

#### Coding Best Practices for Open Source Software Development

The main purpose of coding best practices is to achieve efficient and consistent results by providing proven, optimal methods for writing and organising source code (and related files).

Best practices specify rules that should be applied to reach a good level of readability, maintainability and performances.

The validation tool is implemented in the scope of EOEPCA. It is published in its own GitHub repository:

[🔗 Sources and Documentation](https://github.com/EOEPCA/coding-best-practices-for-oss-action/)

**Exposed parameters**

|   Name                |   Type    |                  Description                  |  Default  |
| --------------------- | --------- | --------------------------------------------- | --------- |
| `path-to-check`       | *string*  | Directory to check.                           | `.`       |
| `default-anchor-file` | *string*  | Default anchor file for issues not related to specific files. | `coding-best-practices-issues.md`        |
| `otuput-file`         | *string*  | Report (output) file name. The extension depends on `output-format`.                   |  `coding-best-practices-report.[json\|txt]`            |
| `output-format`       | *string*  | Output report format: `generic` (SonarQube), `sarif` (v2.1.0), or `text` (for humans).                |  `generic`             |
| `config-file`         | *string*  | YAML file for enabling/disabling and configuring rules. |  *none*             |
| `verbose`             | *boolean* | Enable debug logging.                         | `false`   |
| `ai-model-provider`   | *string*  | Free name of the model provider (e.g. Google, OpenAPI, Anthropic, Ollama).                | *none*    |
| `ai-model-base-url`   | *string*  | OpenAI SDK compliant base URL (e.g. https://api.anthropic.com/v1).                | *none*    |
| `ai-model-api-key`    | *string*  | API key giving access to the model.           | *none*    |
| `ai-model-name`       | *string*  | Name of the model to use within the provider (e.g. `claude-sonnet-4.6`, `gpt-4o`, `qwen2.5-coder:14B`).                | *none*    |

Note: If the `ai-model-*` parameters are not provided, the rules that rely on the availability of an LLM are disabled.


### Application Quality

#### Bandit

[🔗 Documentation](https://bandit.readthedocs.io/en/latest/)

Bandit is a tool designed to find common security issues in Python code. To do this, Bandit processes each file, builds an AST from it, and runs appropriate plugins against the AST nodes. Once Bandit has finished scanning all the files, it generates a report.

**Exposed parameters**

|   Name    |   Type    |                        Description                         |
| --------- | --------- | ---------------------------------------------------------- |
| `verbose` | *boolean* | Output extra information like excluded and included files. | 

#### Trivy

The all-in-one open source security scanner.

Trivy is used to find vulnerabilities (CVE) & misconfigurations (IaC) in container images.

Note: Trivy may also be applied to code repositories, binary artifacts, Kubernetes clusters, and more. This is not yet possible in the Application Quality BB.

[🔗 Documentation](https://trivy.dev/latest/docs/)

**Exposed parameters**

|  Name   |   Type   |                  Description                   |
| ------- | -------- | ---------------------------------------------- |
| `image` | *string* | The name and tag of the distant image to scan. | 

### Application Performance

#### Papermill

Papermill is a tool for parameterizing and executing Jupyter Notebooks.

Each Jupyter notebook maching the filter is executed in a separate job, leading to the generation of individual reports.

[🔗 Documentation](https://papermill.readthedocs.io/en/latest/)

**Exposed parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| `extract_requirements` | *boolean* | Tell the tool to extract Python requirements from the notebook content |
| `extra_requirements` | *string* | Python libraries to install before executing the notebook |
| `execution_parameters` | *string* | Parameter values required to execute the notebook |

#### Pytest

[🔗 Documentation](https://docs.pytest.org/en/stable/)

**Exposed parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |

#### Calrissian

Calrissian allows executing a CWL runner inside a Kubernetes cluster. Its goal is to be highly efficient and scalable, taking advantage of high capacity clusters to run many steps in parallel.

[🔗 Documentation](https://github.com/Duke-GCB/calrissian#readme)

**Exposed parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |

