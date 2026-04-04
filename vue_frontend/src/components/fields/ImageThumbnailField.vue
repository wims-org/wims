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
        <div class="add-image-container m-2" v-if="!disabled">
          <input ref="cameraInput" type="file" class="d-none" accept="image/*" capture="environment"
            @change="addImage" />
          <button type="button" class="btn btn-primary add-image-btn" @click="triggerCameraInput">
            +
          </button>
        </div>
      </div>
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

const cameraInput = ref<HTMLInputElement | null>(null)
const showModal = ref(false)
const selectedImage = ref<File | null>(null)
const selectedImages = ref<File[]>([])

function triggerCameraInput() {
  cameraInput.value?.click()
}

async function addImage(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const formData = new FormData()
    formData.append('file', file) 
    try {
      const newImage: File = await ApiService.createFile(formData)
      const updatedValue = props.value ? [...props.value, newImage] : [newImage]
      emit('update:value', updatedValue)
    } catch (error) {
      console.error('Error uploading image:', error)
    } finally {
      target.value = '' // Reset the input
    }
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
