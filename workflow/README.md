## Running the workflow

To run the workflow, use the [`cwltool`](https://github.com/common-workflow-language/cwltool) command-line tool with the required inputs.

### Command

```bash
cwltool workflow.cwl --repo_url <repository_url> --run_id <unique_run_id>
```

### Example

```bash
cwltool workflow.cwl --repo_url https://github.com/your/repo.git --run_id 4242
```

In this example:
- `https://github.com/your/repo.git` is the Git repository URL to clone and analyze.
- `4242` is the unique identifier for the current run.

## Troubleshooting

- Make sure Docker is installed and running on your machine.
- Ensure you have access to the specified Git repository (public or private with credentials if necessary).
- If you encounter issues with the workflow execution, check the error messages for clues, such as permission errors or missing dependencies.
