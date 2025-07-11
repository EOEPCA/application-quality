import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createPinia } from 'pinia'
import router from '@/router'

import App from '@/App.vue'

import { config } from '@vue/test-utils'

config.global.components = {
  'v-app': components.VApp
}

global.ResizeObserver = require('resize-observer-polyfill')

describe("App.vue", () => {
  const vuetify = createVuetify({ components, directives })
  const pinia = createPinia()
  test("Check side menu", () => {
    const wrapper = mount(App, { global: { plugins: [vuetify, pinia, router] } })
    // Check that links to all the pages are present in the app
    const hrefs = ['/', '/tools', '/pipelines', '/executions', '/reports', '/settings']
    for (var href of hrefs) {
        console.log(href, wrapper.findAll('[href="'+href+'"]'))
        expect(wrapper.findAll('[href="'+href+'"]')).toHaveLength(1)
    }
  })
})