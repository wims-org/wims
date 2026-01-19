<template>
  <BCol>
    <h3 class="mb-4">Profile of {{ user?.username }}</h3>
    <BForm @submit.prevent="submitUser">
      <BFormGroup label="Edit User" label-for="user-form">
        <TextField
          class="mb-3"
          name="username"
          label="Username"
          :value="user?.username ?? ''"
          @update:value="updateUsername"
          required
        />
        <TextField
          name="email"
          label="Email"
          type="email"
          :value="user?.email ?? ''"
          @update:value="updateEmail"
          required
        />
        <ArrayField
          class="mt-3"
          name="tags"
          label="Tags"
          :value="user?.tag_uuids ?? []"
          @update:value="updateTags"
          item-label="Tag"
        />
        <BButton
          type="submit"
          variant="primary"
          :disabled="blockSubmission"
          :class="{ success: success }"
        >
          Update User
        </BButton>
        <span class="ms-2">since: {{ formatDate(user?.date_created) }}</span>
      </BFormGroup>
    </BForm>
    <hr />
    <BRow>
      <BForm>
        <BButton v-if="clientStoreInstance.user" variant="secondary" class="me-2" @click="logout">
          Logout
        </BButton>
        <BButton v-else variant="primary" class="me-2" @click="selectUser(user?._id ?? '')">
          Select this user
        </BButton>
        <BButton variant="danger" @click="deleteUser"> Delete this user </BButton>
      </BForm>
    </BRow>
  </BCol>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import type { components } from '@/interfaces/api-types'
import { useRouter } from 'vue-router'
type User = components['schemas']['User'] & { [key: string]: unknown }

const router = useRouter()
const blockSubmission = ref(false)
const user = ref<User | undefined>(undefined)
const success = ref(false)

function updateUsername(value: string | number | null) {
  // coerce to string; keep existing value if nullish
  if (!user.value) return
  user.value.username = value == null ? '' : String(value)
}

function updateEmail(value: string | number | null) {
  if (!user.value) return
  user.value.email = value == null ? '' : String(value)
}

function updateTags(value: Array<string | number>) {
  if (!user.value) return
  user.value.tag_uuids = value.map((v) => String(v))
}

import { clientStore } from '@/stores/clientStore'
const clientStoreInstance = clientStore()

onMounted(async () => {
  const userId = router.currentRoute.value.path.split('/').pop()
  const response = await axios.get(`/users/${userId}`)
  console.log('Fetched user data:', response.data)
  user.value = response.data
})

const submitUser = async () => {
  blockSubmission.value = true
  axios
    .put(`/users/${user.value?._id}`, user.value)
    .then((response) => {
      const updatedUser = response.data as User
      user.value = updatedUser
      clientStoreInstance.setUser(updatedUser._id as string)
      success.value = true
      setTimeout(() => {
        success.value = false
      }, 2000)
    })
    .catch((error) => {
      console.error('Error creating user:', error)
      alert('Failed to create user. Please check the console for details.')
    })
    .finally(() => {
      blockSubmission.value = false
    })
}

async function selectUser(userId: string) {
  await clientStoreInstance.setUser(userId)
}

async function logout() {
  await clientStoreInstance.unsetUser()
}

const deleteUser = async () => {
  await axios.delete(`/users/${user.value?._id}`)
  if (clientStoreInstance.user?._id === user.value?._id) {
    await clientStoreInstance.unsetUser()
  }
  router.push('/users')
}

function formatDate(date: string | undefined) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}
</script>
<style scoped>
:deep(.form-control) {
  width: unset;
}
.success {
  animation: successFlash 2s;
}

@keyframes successFlash {
  0% {
    background-color: var(--color-success);
  }
  100% {
    background-color: var(--bs-btn-bg);
  }
}
</style>
