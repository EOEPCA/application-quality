# Requirements

Here is the list of original requirements applying to the Application Quality Building Block.

## General

* **BR116**: The Application Quality BB shall provide a set of web-enabled services that support the development of open reproducible science in accordance with best development practice.
* **BR117**: The Application Quality BB shall support automated pipelines that can be triggered via the Notification & Automation BB.
* **BR118**: The Application Quality BB shall provide a web-enabled UI with interactive access to all capabilities of the BB.

## Development Best Practice

* **BR119**: The Development Best Practice component shall provide a static code analysis function that can be applied to a git repository to identify a variety of problems and areas for improvement, including (not limited to): errors, complexity, maintainability, known vulnerabilities (e.g. in library dependencies).
* **BR120**: The Development Best Practice component shall perform checks against the git repository of a processing workflow project to analyse its adherence to software development best practices for open reproducible science. Software development best practice checks include (amongst others) those for documentation, testing and portability.
* **BR121**: The Development Best Practice component shall integrate in the Application Quality BB automated pipelines.

## Application Quality Tooling

* **BR122**: The Application Quality BB shall include an extensible set of Application Quality Tooling that complement the Development Best Practice component, and can be integrated in the Application Quality BB automated pipelines.

  Possible tools include:
  - Vulnerability Scanner, that can be applied to application runtime artefacts (such as containers) to identify known vulnerabilities
  - Others, to be defined...

  *The Contractor shall propose additional application quality tooling, pending agreement with the stakeholders for specific requirements.*

## Application Performance

* **BR123**: The Application Performance component shall provide tooling to support the test and optimisation of processing workflows.
* **BR124**: The Application Performance component shall provide test environments in which the processing workflows can be executed. This is designed to serve a number of purposes:
  - **BR124.1**: To support automated unit/integration testing of applications
  - **BR124.2**: To conduct performance testing to facilitate application optimisation
  - **BR124.3**: To provide validation as a gateway to application releases for production

