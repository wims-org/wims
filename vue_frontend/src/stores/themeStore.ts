import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'wims_theme'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<'light' | 'dark'>(localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light')

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem(STORAGE_KEY, theme.value)
    applyTheme()
  }

  function set(t: 'light' | 'dark') {
    theme.value = t
    localStorage.setItem(STORAGE_KEY, t)
    applyTheme()
  }

  function applyTheme() {
    const root = document.documentElement
    if (theme.value === 'dark') {
      root.setAttribute('data-theme', 'dark')
    } else {
      root.removeAttribute('data-theme')
    }
  }

  // apply on load
  applyTheme()

  return { theme, toggle, set, applyTheme }
})
