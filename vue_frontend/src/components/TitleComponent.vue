<template>
  <BNavbar class="header" sticky="top">
    <BNavbar class="nav-container" fluid>
      <BNavbarBrand to="/">
        <img src="@/assets/icon.svg" alt="WIMS Logo" class="d-inline-block me-2" height="50" />
        <span class="d-none d-sm-inline">{{ msg }}</span>
      </BNavbarBrand>

      <!-- Offcanvas side menu for mobile screens -->
      <BOffcanvas id="offcanvasMenu" class="offcanvas-menu" title="Menu" placement="start" is-nav width="280px">
        <template #header="{ hide }">
          <div class="d-flex align-items-center w-100 navbar-brand">
            <img src="@/assets/icon.svg" alt="WIMS Logo" class="d-inline-block me-2" height="50" />
            <span class="d-sm-inline me-auto">{{ msg }}</span>
            <BButton size="sm" @click="($event) => hide()" variant="outline-light" aria-label="Close menu">
              <IMaterialSymbolsClose />
            </BButton>
          </div>
        </template>
        <div>
          <BNav vertical>
            <BNavItem to="/items" data-testid="offcanvas-nav-items">Items</BNavItem>
            <BNavItem to="/readers" data-testid="offcanvas-nav-readers">Readers</BNavItem>
            <BNavItem to="/users">Users</BNavItem>
            <BNavItem to="/about">About</BNavItem>
            <BNavItem :href="`${api_url}/redoc`" target="_blank">API Docs</BNavItem>
            <hr />

            <BNavItem v-if="user" :to="`/users/${user?._id}`">{{ user?.username }}</BNavItem>
            <BNavItem v-if="user" @click="signOut">Sign Out</BNavItem>
            <BNavItem v-else to="/users">Sign In</BNavItem>
          </BNav>
          <!-- Search bar disabled for now, has no functionality -->
          <div class="mt-2" v-if="false">
            <BFormGroup class="d-flex">
              <BFormInput placeholder="Search" />
              <BButton variant="outline-light" class="me-2" @click="search">
                <IMaterialSymbolsChevronRight />
              </BButton>
            </BFormGroup>
          </div>

          <div class="mt-3 ms-3 d-flex align-items-center">
            <IMaterialSymbolsSunny v-if="isDark" @click="toggleTheme" aria-label="Toggle dark theme" />
            <IMaterialSymbolsMoonStarsOutline v-else @click="toggleTheme" aria-label="Toggle dark theme" />
          </div>
        </div>
      </BOffcanvas>

      <!-- Mobile Navigation -->

      <BNav class="d-flex d-lg-none ms-auto">
        <BNavItem to="/readers" class="text-nowrap" data-testid="sse-connection-state">{{
          connection_msg
          }}</BNavItem>
      </BNav>

      <!-- Desktop Navigation -->

      <BNavbar class="d-none d-lg-flex align-items-center">
        <BNav>
          <BNavItem to="/readers" class="text-nowrap" data-testid="sse-connection-state-lg">{{
            connection_msg
            }}</BNavItem>
          <BNavItem v-if="user" :to="`/users/${user?._id}`">{{ user?.username }}</BNavItem>
          <BNavItem v-else to="/users">Sign In</BNavItem>
        </BNav>

        <BCollapse id="nav-collapse" class="d-lg-flex d-none">
          <BNavbarNav>
            <BNavItemDropdown left hover @hide="menuOpen = false" @show="menuOpen = true">
              <template #button-content>
                <IMaterialSymbolsChevronRight @click="menuOpen = !menuOpen" :style="{
                  transform: menuOpen ? 'rotate(-90deg)' : 'rotate(90deg)',
                  transition: 'transform 0.3s ease',
                }" />
              </template>
              <BNavItem to="/" data-testid="desktop-nav-home">Home</BNavItem>
              <BNavItem to="/items" data-testid="desktop-nav-items">Items</BNavItem>
              <BNavItem to="/readers" data-testid="desktop-nav-readers">Readers</BNavItem>
              <BNavItem to="/users">Users</BNavItem>
              <BNavItem to="/about">About</BNavItem>
              <BNavItem :href="`${api_url}/redoc`" target="_blank">API Docs</BNavItem>
            </BNavItemDropdown>
          </BNavbarNav>
        </BCollapse>
        <BNavForm @onSubmit.prevent="search" class="mx-2">
          <BFormInput placeholder="Search" />
        </BNavForm>
        <IMaterialSymbolsSunny v-if="isDark" @click="toggleTheme" aria-label="Toggle dark theme" />
        <IMaterialSymbolsMoonStarsOutline v-else @click="toggleTheme" aria-label="Toggle dark theme" />
      </BNavbar>

      <BNavbarToggle target="offcanvasMenu" class="d-flex d-lg-none" aria-label="Open menu">
        <IMaterialSymbolsMenu />
      </BNavbarToggle>
    </BNavbar>
  </BNavbar>
</template>

<style scoped>
.header {
  align-items: center;
  background-color: var(--color-navbar);
  display: block;
  width: 100%;
  background: linear-gradient(45deg, var(--color-navbar), var(--color-primary));
}

.header ::after {
  display: none;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding: 0;
  width: var(--content-max-width);
}

.navbar-brand {
  font-weight: bold;
  font-size: 2rem;
  font-family: 'Space Mono', monospace;
  color: var(--color-primary-contrast) !important;
}

.offcanvas-menu {
  .navbar-brand {
    color: var(--color-text) !important;
  }
}

@media (max-width: var(--content-max-width)) {
  .nav-container {
    max-width: var(--content-max-width-small) !important;
    margin: 0 0 !important;
  }
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { clientStore } from '@/stores/clientStore'
import { serverStream } from '@/stores/serverStream'
import { useThemeStore } from '@/stores/themeStore'
import { ref } from 'vue'

// State and Stores
const client_store = clientStore()
const server_stream = serverStream()
const msg = 'WIMS?!'
const menuOpen = ref(false)
const api_url = import.meta.env.VITE_API_URL || ''

// Computed Properties

const connection_msg = computed(() => {
  if (connection_state.value === 0) {
    const name = client_store.reader?.reader_name || ''
    return `🟢 ${name.length > 20 ? name.substring(0, 20) + '...' : name}`
  } else if (connection_state.value === 1) {
    return 'Connecting...'
  } else {
    return '🔴 Connect'
  }
})

const connection_state = computed(() => {
  if (
    server_stream.alive &&
    client_store?.reader_id.length > 0 &&
    client_store?.reader_id !== 'loading'
  ) {
    return 0 // Connected
  } else if (client_store?.reader_id.length > 0) {
    return 1 // Connecting
  } else {
    return 2 // Disconnected
  }
})

const user = computed(() => {
  return client_store.user
})

function signOut() {
  // clear user in client store
  client_store.unsetUser()
}

// Theme
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.theme === 'dark')

function toggleTheme() {
  themeStore.toggle()
}

function search() {
  // Implement search functionality here
  console.log('Search triggered')
}
</script>
