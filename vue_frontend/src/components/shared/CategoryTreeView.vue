<template>
  <div class="category-tree-view">
    <ul class="category-list">
      <li v-for="category in categories" :key="getCategoryKey(category)" class="category-node">
        <div
          class="category-row"
          @mouseenter="hoveredKey = getCategoryKey(category)"
          @mouseleave="hoveredKey = null"
        >
          <button
            class="toggle"
            type="button"
            :disabled="!hasChildren(category)"
            @click="toggleExpanded(getCategoryKey(category))"
          >
            <span v-if="hasChildren(category)">
              <font-awesome-icon
                :icon="`fa-chevron-${isExpanded(getCategoryKey(category)) ? 'down' : 'right'}`"
              />
            </span>
            <span v-else class="toggle-placeholder">•</span>
          </button>

          <span
            class="title"
            @click="hasChildren(category) && toggleExpanded(getCategoryKey(category))"
          >
            {{ category.title }}
          </span>

          <div
            class="actions"
            :class="{ 'actions-visible': hoveredKey === getCategoryKey(category) }"
          >
            <button
              class="btn btn-sm btn-outline-secondary"
              type="button"
              @click="openAddForm(getCategoryKey(category))"
            >
              Add
            </button>
          </div>
        </div>

        <div v-if="addFormForKey === getCategoryKey(category)" class="add-form">
          <form class="d-flex gap-2" @submit.prevent="submitAddChild(category)">
            <input
              v-model="newChildTitle"
              type="text"
              class="form-control form-control-sm"
              placeholder="New subcategory title"
              required
            />
            <button class="btn btn-sm btn-primary" type="submit">Create</button>
            <button class="btn btn-sm btn-outline-secondary" type="button" @click="closeAddForm">
              Cancel
            </button>
          </form>
        </div>

        <CategoryTreeView
          v-if="hasChildren(category) && isExpanded(getCategoryKey(category))"
          :categories="category.children || []"
          :expanded-categories="expandedCategories"
          :expand-all="expandAll"
          @add-child="$emit('add-child', $event)"
        />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
// Component for displaying an expandable tree view of categories, grouped by parent categories.

import { computed, ref, watch } from 'vue'
import type { components } from '@/interfaces/api-types'
import axios from 'axios'

type Category = components['schemas']['CategoryReqRes']
type Categories = Category[]

type CategoryNode = Category & {
  _id?: string
  children?: CategoryNode[]
}

const props = defineProps<{
  categories: Categories
  expandedCategories?: string[]
  expandAll?: boolean
}>()

const emit = defineEmits<{
  (e: 'add-child', payload: { parentKey: string; title: string }): void
}>()

const expandedKeys = ref<Set<string>>(new Set())
const hoveredKey = ref<string | null>(null)

const addFormForKey = ref<string | null>(null)
const newChildTitle = ref<string>('')

const initialExpanded = computed(() => {
  if (props.expandAll) {
    return 'ALL'
  }
  return props.expandedCategories && props.expandedCategories.length ? props.expandedCategories : []
})

watch(
  initialExpanded,
  (value) => {
    if (value === 'ALL') {
      expandedKeys.value = new Set(props.categories.map((c) => getCategoryKey(c)))
      return
    }
    expandedKeys.value = new Set(value)
  },
  { immediate: true },
)

const getCategoryKey = (category: CategoryNode): string => {
  return category._id || category.title
}

const hasChildren = (category: CategoryNode): boolean => {
  return Array.isArray(category.children) && category.children.length > 0
}

const isExpanded = (key: string): boolean => {
  return expandedKeys.value.has(key)
}

const toggleExpanded = (key: string) => {
  if (expandedKeys.value.has(key)) {
    expandedKeys.value.delete(key)
  } else {
    expandedKeys.value.add(key)
  }
  expandedKeys.value = new Set(expandedKeys.value)
}

const openAddForm = (key: string) => {
  addFormForKey.value = key
  newChildTitle.value = ''
  expandedKeys.value.add(key)
  expandedKeys.value = new Set(expandedKeys.value)
}

const closeAddForm = () => {
  addFormForKey.value = null
  newChildTitle.value = ''
}

const submitAddChild = (parent: CategoryNode) => {
  const title = newChildTitle.value.trim()
  if (!title) return

  const parentKey = getCategoryKey(parent)
  createCategory(title, parent)
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
  parent: CategoryNode | null,
): Promise<CategoryNode | null> => {
  return axios
    .post('/categories/', {
      title,
      parent_id: parent ? parent._id : null,
      description: null,
      children: [],
    } as Category)
    .then((response) => {
      console.log('Category created:', response.data)
      return response.data
    })
    .catch((error) => {
      console.error('Error creating category:', error)
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

.category-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0;
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
</style>
