<template>
  <div class="users-view">
    <h1>Users</h1>
    <ul class="list-group block-item-list" data-testid="user-list">
      <li
        v-for="user in users"
        data-testid="user-item"
        :key="user._id"
        @click="user._id === clientStoreInstance?.user?._id ? deselectUser() : selectUser(user._id)"
        class="list-group-item d-flex justify-content-between align-items-center"
        :class="{ active: user?._id === (clientStoreInstance?.user?._id ?? '') }"
      >
        <div>
          {{ user.username }}
          <br />
          <span class="text-muted">{{ user.email }}</span>
        </div>
        <button @click.stop="deleteUser(user._id)" class="btn btn-danger btn-sm">Delete</button>
      </li>
      <div v-if="users.length === 0" class="list-group-item">
        <div class="spinner-border spinner-border-sm" role="status"></div>
        Loading...
      </div>
    </ul>
    <div class="card mt-4">
      <div class="card-header">Add New User</div>
      <div class="card-body">
        <form @submit.prevent="submitUser" class="p-3 col">
          <div class="form-group col-md-5">
            <label for="userName">User Name</label>
            <input
              type="text"
              v-model="newUser.username"
              id="userName"
              class="form-control"
              required
            />
          </div>
          <div class="form-group col-md-5">
            <label for="userId">E-Mail</label>
            <input type="text" v-model="newUser.email" id="userId" class="form-control" required />
          </div>
          <div class="form-group col-md-2 d-flex align-items-end mt-3">
            <button
              type="button"
              :disabled="blockSubmission"
              @click="submitUser"
              v-on:keydown.enter.prevent="submitUser"
              class="btn btn-primary w-100"
            >
              Add User
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import type { components } from '@/interfaces/api-types'

type User = components['schemas']['User'] & { [key: string]: unknown }
const users = ref<User[]>([])
const blockSubmission = ref(false)
const newUser = ref<components['schemas']['UserRequest']>({
  username: '',
  email: '',
})

import { clientStore } from '@/stores/clientStore'
const clientStoreInstance = clientStore()

onMounted(async () => {
  const response = await axios.get('/users')
  users.value = response.data
})

const submitUser = async () => {
  blockSubmission.value = true
  axios
    .post('/users', newUser.value)
    .then((response) => {
      const createdUser = response.data as User
      users.value.push(createdUser)
      newUser.value = { username: '', email: '' }
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

async function deselectUser() {
  await clientStoreInstance.unsetUser()
}

const deleteUser = async (userId: string) => {
  await axios.delete(`/users/${userId}`)
  users.value = users.value.filter((user) => user._id !== userId)
}
</script>
<style scoped></style>
