/// <reference types="vite/client" />
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Vue from 'vue'; // this add 
declare module 'vue' {
  import { CompatVue } from '@vue/runtime-dom'
  const Vue: CompatVue
  export default Vue
  export * from '@vue/runtime-dom'
}