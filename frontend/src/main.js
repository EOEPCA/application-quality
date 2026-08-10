import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css';
import VueNotify from 'vue3-notify';
// Docs: https://github.com/bestkolobok/vue3-jsoneditor
import {JsonEditorPlugin} from 'vue3-ts-jsoneditor';

const vuetify = createVuetify({
  components,
  directives,
});

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(vuetify);
app.use(VueNotify);
app.use(JsonEditorPlugin, {
  componentName: 'JsonEditor',
  options: {
    // Global JSON Editor options
    tabSize: 2,
    indentation: 2,
    fullWidthButton: false,
  }
});

app.mount('#app');
