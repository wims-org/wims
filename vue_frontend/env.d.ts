/// <reference types="vite/client" />

declare module '@vue/compat' {
  import { CompatVue } from '@vue/runtime-dom';
  const Vue: CompatVue;
  export * from '@vue/runtime-dom';
  export default Vue;
}