/// <reference types="vite/client" />

declare module 'vue' {
    import { CompatVue } from '@vue'
    const Vue: CompatVue
    export default Vue
    export * from '@vue'
    const { configureCompat } = Vue
    export { configureCompat }
  }