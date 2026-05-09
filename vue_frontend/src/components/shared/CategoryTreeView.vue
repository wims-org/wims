<template>
  <div class="category-tree-view">
    <div v-if="saveError" class="sticky-note sticky-note-error">{{ saveError }}</div>
    <div v-if="saveSuccess" class="sticky-note sticky-note-success">{{ saveSuccess }}</div>
    <ul class="category-list">
      <li v-for="category in categories" :key="category.id" class="category-node">
        <div class="d-flex align-items-center gap-2 py-1 flex-row category"
          @click.stop="hasChildren(category) && toggleExpanded(category)"
          @mouseenter="hoveredKey = category.id" @mouseleave="hoveredKey = null">
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
            :class="{ 'actions-visible': hoveredKey === category.id }">
            <button class="btn btn-sm btn-outline-secondary" type="button" @click.stop="
              $router.push({
                name: 'category',
                params: { categoryId: category.id },
              })
              ">
              <font-awesome-icon icon="fa-magnifying-glass" />
              <span class="ms-1 d-none d-md-inline-flex">View</span>
            </button>
          </div>

          <div class="actions"
            :class="{ 'actions-visible': hoveredKey === category.id || formKey === category.id }">
            <button v-if="formKey != category.id" class="btn btn-sm btn-outline-secondary" type="button"
              @click.stop="formKey = category.id; expandedCategories.add(category.id)">
              <span class="d-md-none">
                <font-awesome-icon icon="fa-plus" />
              </span>
              <span class="d-none d-md-inline-flex">Add Sub Category</span>
            </button>
            <button v-else class="btn btn-sm btn-outline-secondary" type="button" @click.stop="closeAddForm">
              Cancel
            </button>
          </div>
        </div>

        <div v-if="formKey === category.id" class="add-form">
          <form class="d-flex gap-2" @submit.prevent="submitAddChild(category)">
            <input v-model="newChildTitle" type="text" class="form-control form-control-sm"
              placeholder="New subcategory title" required />
            <button class="btn btn-sm btn-primary" type="submit">Create</button>
          </form>
        </div>

        <CategoryTreeView v-if="isExpanded(category) && hasChildren(category)" :categories="category.children || []"
          :expand-all="expandAll" :expanded-categories="expandedCategories" @add-child="$emit('add-child', $event)"
          :selectable="selectable" :parent="category" />
      </li>
    </ul>

    <div v-if="formKey !== 0 && !parent && showActions" class="row text-center mt-3 gap-2 justify-content-center">
      <button class="btn btn-sm btn-outline-primary rounded mx-auto add-category-button" type="button"
        @click.stop="formKey = 0" title="Add Category">
        +
      </button>
    </div>
    <div v-if="formKey === 0 && showActions" class="add-form">
      <form class="d-flex gap-2" @submit.prevent="submitAddChild(parent || null)">
        <input v-model="newChildTitle" type="text" class="form-control form-control-sm"
          placeholder="New root category title" required />
        <button class="btn btn-sm btn-primary" type="submit">Create</button>
        <button class="btn btn-sm btn-outline-secondary" type="button" @click.stop="closeAddForm">
          Cancel
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component for displaying an expandable tree view of categories, grouped by parent categories.

import { ref, watch } from 'vue'
import type { components } from '@/interfaces/api-types'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

type Category = components['schemas']['CategoryPublic']

type CategoryNode = Category & {
  id?: string
  children?: CategoryNode[]
}

const props = defineProps<{
  categories: Category[]
  expandAll?: boolean
  expandedCategories?: Set<number>
  selectable?: boolean
  parent?: CategoryNode
  showActions?: boolean
}>()

const emit = defineEmits<{
  (e: 'add-child', payload: { parentKey: string | null; title: string }): void
}>()

const hoveredKey = ref<number | null>(null)
const expandedCategories = ref<Set<number>>(new Set(props.expandedCategories || []))
const categories = ref<CategoryNode[]>([...props.categories || []])

const formKey = ref<number | null>(null)
const newChildTitle = ref<string>('')

const saveError = ref<string>('')
const saveSuccess = ref<string>('')
const showActions = ref<boolean>(props.showActions ?? true)

watch(
  () => props.categories,
  (newCategories) => {
    categories.value = [...newCategories]
  },
)

const hasChildren = (category: CategoryNode): boolean => {
  return Array.isArray(category.children) && category.children.length > 0
}

const isExpanded = (category: CategoryNode) => {
  return expandedCategories.value && expandedCategories.value.has(category.id)
}

const toggleExpanded = (category: CategoryNode) => {
  if (isExpanded(category)) {
    expandedCategories.value.delete(category.id)
  } else {
    expandedCategories.value.add(category.id)
  }
}

const closeAddForm = () => {
  formKey.value = null
  newChildTitle.value = ''
}

const submitAddChild = (parent: CategoryNode | null) => {
  const title = newChildTitle.value.trim()
  if (!title) return
  const parentKey = parent ? parent.id : null
  createCategory(title, parentKey)
    .then((newCategory) => {
      if (newCategory) {
        emit('add-child', { parentKey, title })
        closeAddForm()
      }
    })
    .finally(() => {
    })
}

const createCategory = async (
  title: string,
  parentKey: string | null,
): Promise<CategoryNode | null> => {
  return axios
    .post('/categories', {
      title,
      parent_id: parentKey,
      description: null
    } as Category)
    .then((response) => {
      console.log('Category created:', response.data)
      saveSuccess.value = 'Category created successfully.'
      setTimeout(() => (saveSuccess.value = ''), 5000)
      return response.data
    })
    .catch((error) => {
      console.error('Error creating category:', error)
      if (error.response && error.response.data && error.response.data.detail) {
        saveError.value = `Error: ${error.response.data.detail}`
      } else {
        saveError.value = 'An unexpected error occurred while creating the category.'
      }
      setTimeout(() => (saveError.value = ''), 10000)
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

@media (max-width: 768px) {
  .actions {
    opacity: 1;
  }
}

.actions-visible {
  opacity: 1;
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

.add-category-button {
  width: 40px;
  height: 40px;
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}
</style>
