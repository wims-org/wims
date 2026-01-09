<template>
  <div class="category-tree-view">
    <div v-if="saveError" class="sticky-note sticky-note-error">{{ saveError }}</div>
    <div v-if="saveSuccess" class="sticky-note sticky-note-success">{{ saveSuccess }}</div>
    <ul class="category-list">
      <li v-for="category in categories" :key="getCategoryKey(category)" class="category-node">
        <div class="d-flex align-items-center gap-2 py-1 flex-row category"
          @click.stop="hasChildren(category) && toggleExpanded(category)" @mouseenter="hoveredKey = getCategoryKey(category)"
          @mouseleave="hoveredKey = null">
          <div class="list-toggle">
            <span v-if="hasChildren(category)">
              <font-awesome-icon :icon="`fa-chevron-${isExpanded(category) ? 'down' : 'right'}`" />
            </span>
            <span v-else class="toggle-placeholder">•</span>
          </div>
          <span class="title">
            {{ category.title }}
          </span>

          <div v-if="selectable" class="actions"
            :class="{ 'actions-visible': hoveredKey === getCategoryKey(category) }">
            <button class="btn btn-sm btn-outline-secondary" type="button" @click.stop="
              $router.push({
                name: 'category',
                params: { categoryId: getCategoryKey(category) },
              })
              ">
              <font-awesome-icon icon="fa-arrow-right" />
              View
            </button>
          </div>

          <div class="actions" :class="{ 'actions-visible': hoveredKey === getCategoryKey(category) }">
            <button v-if="!formKey" class="btn btn-sm btn-outline-secondary" type="button"
              @click.stop="formKey = getCategoryKey(category)">
              Add
            </button>
            <button v-else class="btn btn-sm btn-outline-secondary" type="button" @click.stop="closeAddForm">
              Cancel
            </button>
          </div>
        </div>

        <div v-if="formKey === getCategoryKey(category)" class="add-form">
          <form class="d-flex gap-2" @submit.prevent="submitAddChild(category)">
            <input v-model="newChildTitle" type="text" class="form-control form-control-sm"
              placeholder="New subcategory title" required />
            <button class="btn btn-sm btn-primary" type="submit">Create</button>
          </form>
        </div>

        <CategoryTreeView v-if="isExpanded(category) && hasChildren(category)" :categories="category.children || []"
          :expand-all="expandAll" :expanded-categories="expandedCategories" @add-child="$emit('add-child', $event)"
          :selectable="selectable" />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
// Component for displaying an expandable tree view of categories, grouped by parent categories.

import { ref } from 'vue'
import type { components } from '@/interfaces/api-types'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

type Category = components['schemas']['CategoryReqRes']

type CategoryNode = Category & {
  _id?: string
  children?: CategoryNode[]
}

const props = defineProps<{
  categories: Category[]
  expandAll?: boolean
  expandedCategories?: string[]
  selectable?: boolean
}>()

const emit = defineEmits<{
  (e: 'add-child', payload: { parentKey: string; title: string }): void
}>()

const hoveredKey = ref<string | null>(null)
const expandedCategories = ref<string[]>(
  [...props.expandedCategories || []],
)

const formKey = ref<string>()
const newChildTitle = ref<string>('')

const saveError = ref<string>('')
const saveSuccess = ref<string>('')


const getCategoryKey = (category: CategoryNode): string => {
  return category._id || category.title
}

const hasChildren = (category: CategoryNode): boolean => {
  return Array.isArray(category.children) && category.children.length > 0
}

const isExpanded = (category: CategoryNode) => {
  return expandedCategories.value && expandedCategories.value.includes(getCategoryKey(category))
}

const toggleExpanded = (category: CategoryNode) => {
  if (isExpanded(category)) {
    const index = expandedCategories.value?.indexOf(getCategoryKey(category))
    if (index !== undefined && index > -1 && expandedCategories) {
      expandedCategories.value.splice(index, 1)
    }
  } else {
    expandedCategories.value.push(getCategoryKey(category))
  }
}


const closeAddForm = () => {
  formKey.value = ''
  newChildTitle.value = ''
}

const submitAddChild = (parent: CategoryNode) => {
  const title = newChildTitle.value.trim()
  if (!title) return

  const parentKey = getCategoryKey(parent)
  createCategory(title, parentKey)
    .then((newCategory) => {
      if (newCategory) {
        if (!Array.isArray(parent.children)) parent.children = []
        parent.children.push(newCategory)
        emit('add-child', { parentKey, title })
      }
    })
    .finally(() => {
      closeAddForm()
    })
}

const createCategory = async (
  title: string,
  parentKey: string | null,
): Promise<CategoryNode | null> => {
  return axios
    .post('/categories/', {
      title,
      _id: null,
      parent_id: parentKey,
      description: null,
      children: [],
    } as Category)
    .then((response) => {
      console.log('Category created:', response.data)
      saveSuccess.value = 'Category created successfully.'
      setTimeout(() => saveSuccess.value = '', 5000)
      return response.data
    })
    .catch((error) => {
      console.error('Error creating category:', error)
      if (error.response && error.response.data && error.response.data.detail) {
        saveError.value = `Error: ${error.response.data.detail}`
      } else {
        saveError.value = 'An unexpected error occurred while creating the category.'
      } setTimeout(() => saveError.value = '', 10000)
      return null
    })
}
</script>

<style scoped>
.category-list {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.category-node {
  margin: 0;
}

.category {
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: var(--color-bg-light);
  }
}

.toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  background: transparent;
  padding: 0;
  color: var(--text-secondary);
}

.toggle:disabled {
  opacity: 0.6;
}

.toggle-placeholder {
  display: inline-block;
  width: 1rem;
  text-align: center;
}

.title {
  flex: 1;
  cursor: default;
}

.actions {
  opacity: 0;
  transition: opacity 120ms ease-in-out;
}

.actions-visible {
  opacity: 1;
}

.add-form {
  padding: 0 0 0.25rem 1.5rem;
  margin-left: 1.5rem;
}

.category-tree-view :deep(.category-tree-view) {
  padding-left: 1.5rem;
}

.list-toggle {
  width: 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
