# Helm chart for reference deployment

This is a deployment of the Application Quality BB, including Grafana.
This leads to a fully functional setup.

## Validating the Helm templates

To debug templates and ensure they may be rendered to valid YAML files using the values, install `helm`, then use the following commands:

```bash
cd application-quality-reference-deployment
helm dependency update
cd -
helm template --debug application-quality-reference-deployment
```

This outputs the rendered files on the console.