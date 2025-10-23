<template>
  <v-app>
    <VueNotifications
      :reverse="notify.reverse"
      :width="notify.width"
      :position="notify.position"
      :max="notify.max"
      :close-on-click="notify.closeOnClick"
      :pause-on-hover="notify.pauseOnHover"
      :speed="notify.speed"
      :timeout="notify.timeout"
      :clean="notify.clean"
      :ignore-duplicates="notify.ignoreDuplicate"
    />
    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="rail = !rail"></v-app-bar-nav-icon>
      <v-app-bar-title>{{ settings.instance__name }}</v-app-bar-title>
      <!-- Login / Logout button -->
      <v-spacer></v-spacer>

      <v-btn
        style="padding: 0px"
        min-width="0px"
        v-tooltip:bottom-end="'User Manual (new page)'"
        target="appquality_user_manual"
        :href="settings.user_manual__url"
      >
        <v-icon size="24px"> mdi-help-box </v-icon>
      </v-btn>

      <v-btn
        style="padding: 0px"
        min-width="0px"
        v-tooltip:bottom-end="'Dashboards (new page)'"
        target="_blank"
        :href="settings.getGrafanaDashboardsURL()"
      >
        <v-icon size="24px"> mdi-chart-box </v-icon>
      </v-btn>

      <v-btn
        style="padding: 0px"
        min-width="0px"
        v-tooltip:bottom-end="'Source Code (new page)'"
        target="_blank"
        :href="settings.source__url"
      >
        <v-icon size="24px"> mdi-github </v-icon>
      </v-btn>

      <span
        style="padding-left: 20px"
        class="vuetify-label"
        v-tooltip:bottom-end="authStore.username"
      >
        {{ authStore.firstname }} {{ authStore.lastname }}
      </span>
      <v-chip v-if="authStore.isAdmin" size="small" class="ml-2">
        Admin
      </v-chip>
      <v-chip v-if="authStore.isSuperuser" size="small" class="ml-2">
        Superuser
      </v-chip>
      <v-btn class="ml-2" @click="toggleLogin">{{
        authStore.isLoggedIn ? 'Logout' : 'Login'
      }}</v-btn>
    </v-app-bar>

    <v-navigation-drawer :rail="rail">
      <v-list v-if="rail">
        <v-list-item
          v-for="item in menuItems"
          v-tooltip="item.title"
          :key="item.title"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
        />
      </v-list>
      <v-list v-else>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
        />
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';

export default {
  name: 'App',
  components: {},
  data() {
    return {
      rail: true, // Show only icons in the side menu by default
      isLoggedIn: false,
      //loginDialog: false, // Control the visibility of the login dialog
      menuItems: [
        { title: 'Home', path: '/', icon: 'mdi-home' },
        { title: 'Analysis Tools', path: '/tools', icon: 'mdi-tools' },
        { title: 'Pipelines', path: '/pipelines', icon: 'mdi-pipe' },
        { title: 'Monitoring', path: '/executions', icon: 'mdi-monitor-eye' },
        { title: 'Reports', path: '/reports', icon: 'mdi-note-text-outline' },
        { title: 'Settings', path: '/settings', icon: 'mdi-cog' },
      ],
      userDetails: null,
      notify: {
        reverse: false,
        width: '600px',
        position: 'center',
        timeout: 5000, // Default: 400
        max: 5000,
        closeOnClick: true,
        pauseOnHover: true,
        speed: 300,
        clean: false,
        ignoreDuplicates: true,
      },
    };
  },
  setup() {
    const settings = useSettingsStore();
    const authStore = useAuthStore();
    return { settings, authStore };
  },

  mounted() {
    this.settings.fetchSettings();
    this.authStore
      .fetchUserDetails()
      .then((this.userDetails = this.authStore.details));
  },

  methods: {
    toggleLogin() {
      console.log('Toggle Login. Is logged in:', this.isLoggedIn);
      if (this.authStore.isLoggedIn) {
        // TODO: Navigate to the logout URL
        this.authStore.logout();
      } else {
        // Navigate to the login URL
        this.authStore.login();

        //this.loginDialog = true; // Open the login dialog
      }
    },
    // handleLoginSuccess() {
    //   this.isLoggedIn = true;
    //   this.loginDialog = false; // Close the login dialog on successful login
    // },
  },
};
</script>

<style>
#app {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 0fr;
}
</style>
