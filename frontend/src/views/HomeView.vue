<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-home" size="x-small" class="mr-2" />Home
    </h2>
    <p>The Application Quality Service aims to support the evolution of scientific algorithms (processing workflows) from research projects to ones that can be utilised in a production environment.
        To achieve this, the Service provides tools for verifying non-functional requirements - including code quality, software development best practice for open reproducible science, and optimisation through performance testing.
      </p>
      <p>&nbsp;</p>
      <p>
        Read about the Service capabilities in the online <a target="_blank" href="https://eoepca.readthedocs.io/projects/application-quality/en/latest/usage/user-manual/">User Manual</a>.
      </p>
      <p>&nbsp;</p>
      <p>
        Analyse the pipeline execution reports in the OpenSearch powered <a target="_blank" href="https://application-quality.develop.eoepca.org/dashboards/">Dashboards</a>.
      </p>
      <p>&nbsp;</p>
      <p>
        More links:
      </p>
      <v-list lines="one">
        <v-list-item>
          <a target="_blank" href="https://eoepca.readthedocs.io/projects/architecture/en/latest/reference-architecture/application-quality-BB/">Reference architecture</a>
        </v-list-item>
        <v-list-item>
          <a target="_blank" href="https://github.com/EOEPCA/application-quality/">GitHub repository</a>
        </v-list-item>
      </v-list>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>