<template>
  <div class="image-thumbnail-field">
    <div v-if="value && value.length" class="d-flex flex-wrap">
      <div
        v-for="(image, index) in value"
        :key="index"
        class="thumbnail-container m-2"
        @click="openImageModal(image)"
      >
        <img :src="image" class="thumbnail" alt="Image Thumbnail" />
        <button
          class="btn btn-danger btn-sm mt-1"
          @click.stop="removeImage(index)"
        >
          Remove
        </button>
      </div>
    </div>
    <p v-else>No images available.</p>
    <div class="add-image-container mt-3">
      <input
        ref="cameraInput"
        type="file"
        class="d-none"
        accept="image/*"
        capture="environment"
        @change="addImage"
      />
      
    </div>
    <button
        type="button"
        class="btn btn-primary add-image-btn"
        @click="triggerCameraInput"
      >
        +
      </button>
    <!-- Use the new ImageModal component -->
    <ImageModal
      v-if="showModal && selectedImage"
      :image="selectedImage"
      @close="closeImageModal"
    />
    
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref } from 'vue'
import ImageModal from '@/components/shared/ImageModal.vue'

export default defineComponent({
  name: 'ImageThumbnailField',
  components: {
    ImageModal,
  },
  props: {
    value: {
      type: Array as PropType<string[]>,
      required: true,
      default: () => [],
    },
  },
  emits: ['update:value'],
  setup(props, { emit }) {
    const cameraInput = ref<HTMLInputElement | null>(null)
    const showModal = ref(false)
    const selectedImage = ref<string | null>(null)

    const triggerCameraInput = () => {
      cameraInput.value?.click()
    }

    const addImage = (event: Event) => {
      const input = event.target as HTMLInputElement
      if (input.files && input.files.length > 0) {
        const file = input.files[0]
        const reader = new FileReader()
        reader.onload = (e) => {
          if (e.target?.result) {
            const updatedValue = [...props.value, e.target.result as string]
            emit('update:value', updatedValue) // Emit updated value
          }
        }
        reader.readAsDataURL(file)
      }
    }

    const removeImage = (index: number) => {
      const updatedValue = props.value.filter((_, i) => i !== index)
      emit('update:value', updatedValue) // Emit updated value
    }

    const openImageModal = (image: string) => {
      selectedImage.value = image
      showModal.value = true
    }

    const closeImageModal = () => {
      showModal.value = false
      selectedImage.value = null
    }

    return {
      cameraInput,
      triggerCameraInput,
      addImage,
      removeImage,
      showModal,
      selectedImage,
      openImageModal,
      closeImageModal,
    }
  },
})
</script>

<style scoped>
.thumbnail-container {
  position: relative;
  width: 100px;
  height: 100px;
  cursor: pointer;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
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
</style>
