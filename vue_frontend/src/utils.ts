const formatDate = (timestamp: number): string => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return isNaN(date.getTime()) ? '' : date.toISOString().split('T')[0]
}

const getFieldModel = (
  formData: { [x: string]: unknown },
  key: string,
  type: string,
): string | undefined => {
  if (formData === undefined) {
    return undefined
  } else if (type === 'checkbox') {
    return (formData as { [key: string]: boolean })[key] ? 'checked' : ''
  } else if (type === 'epoch') {
    return formatDate((formData as { [key: string]: number })[key])
  }
  if (formData && typeof formData === 'object' && key in formData) {
    console.log((formData as { [key: string]: unknown })[key])
  }
  return (formData as { [key: string]: never })[key]
}

const updateFieldModel = (
  formData: { [x: string]: unknown },
  event: Event,
  key: string,
  type: string,
) => {
  const target = event.target as HTMLInputElement
  if (type === 'checkbox') {
    ;(formData as { [key: string]: boolean })[key] = target.checked
  } else if (type === 'epoch') {
    ;(formData as { [key: string]: number })[key] = new Date(target.value).getTime() / 1000
  } else if (type === 'number') {
    ;(formData as { [key: string]: number })[key] = Number(target.value)
  } else if (type === 'array') {
    ;(formData as { [key: string]: string[] })[key] = target.value
      .split(',|;')
      .map((item) => item.trim())
  } else {
    ;(formData as { [key: string]: string })[key] = target.value
  }
}

export { formatDate, getFieldModel, updateFieldModel }
