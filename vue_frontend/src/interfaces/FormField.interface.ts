export default interface FormField {
  name?: string 
  label: string
  type: string
  value?: string | number | boolean | undefined
  error?: string | null | undefined
  disabled?: boolean 
  hidden?: boolean 
  details?: boolean 
  required?: boolean 
}
