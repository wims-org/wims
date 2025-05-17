export const fieldTypeToComponent = (type: string) => {
  switch (type) {
    case 'textarea':
      return 'TextAreaField'
    case 'object':
      return 'ObjectField'
    case 'loading':
      return 'LoadingField'
    case 'checkbox':
      return 'CheckboxField'
    case 'array':
      return 'ArrayField'
    case 'uuid':
      return 'ModalField'
    case 'number':
      return 'NumberField'
    case 'images':
      return 'ImageThumbnailField'
    case 'item':
      return 'ItemField'
    default:
      return 'TextField'
  }
}
