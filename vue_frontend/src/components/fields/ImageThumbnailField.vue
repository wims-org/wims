<template>
  <BContainer>
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="image-thumbnail-field">
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <div class="thumbnail-container-wrapper d-flex flex-wrap align-items-center">
        <div v-for="(image, index) in value" :key="index" class="thumbnail-container m-2"
          @click="selector?selectImage(image):openImageModal(image)">
          <img :src="image.asset_url" class="thumbnail" alt="Image Thumbnail" />
          <button type="button" class="remove-btn" @click.stop="removeImage(index)">
            <font-awesome-icon icon="times" />
          </button>
          <div v-if="selector && selectedImages.includes(image)" class="selected-overlay">
            <font-awesome-icon icon="check" />
          </div>
        </div>
        <div v-if="value?.length === 0" class="text-center m-2">
          <font-awesome-icon icon="camera" size="xl" />
          <p>No images</p>
        </div>
        <div class="add-image-container m-2 position-relative" v-if="!disabled">
          <button type="button" class="btn btn-primary add-image-btn">+</button>
          <input type="file" class="file-input-overlay" accept="image/*" capture="environment"
            @change="addImage" />
        </div>
      </div>
      <div v-if="uploadError" class="text-danger small mt-1 w-100">{{ uploadError }}</div>
      <ImageModal v-if="showModal && selectedImage" :image="selectedImage.asset_url" @close="closeImageModal" />
    </div>
  </BContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ImageModal from '@/components/shared/ImageModal.vue'
import ApiService from '@/services/ApiService'
import type { File } from '@/interfaces/file.interface'

const props = defineProps({
  name: {
    type: String,
    required: false,
  },
  label: {
    type: String,
    required: false,
  },
  value: {
    type: Array as () => (File[] | null),
    default: () => [],
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  hideLabel: {
    type: Boolean,
    default: false,
  },
  borderless: {
    type: Boolean,
    default: false,
  },
  selector: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits<{
  (e: 'update:value', value: File[]): void
  (e: 'update:selectedImages', value: File[]): void
}>()

const showModal = ref(false)
const selectedImage = ref<File | null>(null)
const selectedImages = ref<File[]>([])
const uploadError = ref('')

async function compressImage(file: globalThis.File, maxWidth = 1920, quality = 0.82): Promise<globalThis.File> {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, maxWidth / bitmap.width)
  const canvas = document.createElement('canvas')
  canvas.width = bitmap.width * scale
  canvas.height = bitmap.height * scale
  canvas.getContext('2d')!.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  return new Promise((resolve) => {
    canvas.toBlob(
      (blob) => resolve(blob ? new globalThis.File([blob], file.name, { type: 'image/jpeg' }) : file),
      'image/jpeg', quality,
    )
  })
}

async function addImage(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const compressed = await compressImage(file)
  const formData = new FormData()
  formData.append('file', compressed, file.name)
  uploadError.value = ''
  try {
    const newImage: File = await ApiService.createFile(formData)
    const updatedValue = props.value ? [...props.value, newImage] : [newImage]
    emit('update:value', updatedValue)
  } catch (error) {
    console.error('Error uploading image:', error)
    uploadError.value = 'Upload failed. Please try again.'
  } finally {
    target.value = ''
  }
}

function removeImage(index: number) {
  if (!props.value) return
  const updatedValue = props.value.filter((_, i) => i !== index) as File[]
  emit('update:value', updatedValue)
}

function openImageModal(image: File) {
  selectedImage.value = image
  showModal.value = true
}

function closeImageModal() {
  showModal.value = false
  selectedImage.value = null
}

function selectImage(image: File) {
  if (selectedImages.value.includes(image)) {
    selectedImages.value = selectedImages.value.filter((img) => img !== image)
  } else {
    selectedImages.value.push(image)
  }
  emit('update:selectedImages', selectedImages.value)
}
</script>

<style scoped>
.thumbnail-container {
  position: relative;
  width: 4rem;
  height: 4rem;
  cursor: pointer;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-danger);
  border-radius: 50%;
}

remove-btn:hover {
  color: var(--color-danger);
  transform: scale(1.2);
  background: rgba(var(--color-muted), 0.2);
}

.add-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-image-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.file-input-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.borderless label {
  display: none !important;
}

.selected-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(var(--color-success), 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
