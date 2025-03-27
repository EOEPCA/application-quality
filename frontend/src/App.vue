<template>
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
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>EOEPCA - Application Quality Service</v-app-bar-title>
      <!-- Login / Logout button -->
      <v-spacer></v-spacer>
      <span class="vuetify-label" v-tooltip:bottom-end="store.username">
        {{ store.firstname }} {{ store.lastname }}
      </span>
      <v-chip v-if="store.isAdmin" size="small" class="ml-2"> Admin </v-chip>
      <v-chip v-if="store.isSuperuser" size="small" class="ml-2">
        Superuser
      </v-chip>
      <v-btn class="ml-2" @click="toggleLogin">{{
        store.isLoggedIn ? 'Logout' : 'Login'
      }}</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" permanent persistent>
      <v-list>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main style="--v-layout-left: 0px">
      <v-container :width="1200">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'App',
  components: {},
  data() {
    return {
      drawer: true, // Displayed by default
      isLoggedIn: false,
      //loginDialog: false, // Control the visibility of the login dialog
      menuItems: [
        { title: 'Home', path: '/', icon: 'mdi-home' },
        { title: 'Analysis Tools', path: '/tools', icon: 'mdi-tools' },
        { title: 'Pipelines', path: '/pipelines', icon: 'mdi-pipe' },
        { title: 'Monitoring', path: '/executions', icon: 'mdi-monitor-eye' },
        { title: 'Reports', path: '/reports', icon: 'mdi-file-chart' },
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
    const store = useAuthStore();
    return { store };
  },

  mounted() {
    this.store.fetchUserDetails().then((this.userDetails = this.store.details));
  },

  methods: {
    toggleLogin() {
      console.log('Toggle Login. Is logged in:', this.isLoggedIn);
      if (this.store.isLoggedIn) {
        // TODO: Navigate to the logout URL
        this.store.logout();
      } else {
        // Navigate to the login URL
        this.store.login();

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
