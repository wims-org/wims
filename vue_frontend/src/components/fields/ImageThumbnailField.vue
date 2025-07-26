<template>
  <container>
    <div class="form-group d-flex align-items-center justify-content-between flex-wrap p-2"
      data-testid="image-thumbnail-field">
      <span v-if="!hideLabel || !label" :for="name">{{ label }}</span>
      <div class="thumbnail-container-wrapper d-flex flex-wrap align-items-center">
        <div v-for="(image, index) in value" :key="index" class="thumbnail-container m-2"
          @click="openImageModal(image)">
          <img :src="image" class="thumbnail" alt="Image Thumbnail" />
          <button type="button" class="remove-btn" @click.stop="removeImage(index)">
            <font-awesome-icon icon="times" />
          </button>
        </div>
        <div v-if="value.length === 0" class="text-center m-2">
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
      <ImageModal v-if="showModal && selectedImage" :image="selectedImage" @close="closeImageModal" />
    </div>
  </container>
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
    name: {
      type: String,
      required: false,
    },
    label: {
      type: String,
      required: false,
    },
    value: {
      type: Array as PropType<string[]>,
      required: true,
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
  width: 4rem;
  height: 4rem;
  cursor: pointer;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  cursor: pointer;
  color: #ff0000;
  border-radius: 50%;
}

.remove-btn:hover {
  color: #ff0000;
  transform: scale(1.2);
  background: rgba(0, 0, 0, 0.2);
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
</style>
