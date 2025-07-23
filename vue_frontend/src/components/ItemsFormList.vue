<template>
  <div>
    <form @submit.prevent="handleSubmit">
      <div class="mb-2 d-flex justify-content-between align-items-center">
        <span class="text-nowrap mr-2">
          <font-awesome-icon icon="file-csv" />
          Upload .CSV:</span>
        <input type="file" accept=".csv,text/csv" @change="handleCsvUpload" class="form-control-file" />
        <button type="button" class="btn btn-secondary btn-sm ml-2" @click="resetColumnWidths">
          <font-awesome-icon icon="trash" />
          Reset Columns
        </button>
        <button type="button" class="btn btn-secondary btn-sm ml-2" @click="copyColumnNames">
          <font-awesome-icon icon="clipboard" />
          Copy Column Names to clipboard
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-bordered table-sm">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col" :style="{ width: columnWidths[col] + 'px' }" class="draggable-th">
                <div class="th-content">
                  {{ formFields[col]?.label || col }}
                  <span class="resize-handle" @mousedown="startResize($event, col)"></span>
                </div>
              </th>
              <th class="button-column">
                <button type="button" class="btn btn-success btn-sm" @click="toggleColumnDropdown()">
                  Add Column
                </button>
                <div v-if="columnDropDown" class="dropdown-menu">
                  <button v-for="(field, key) in formFields" :key="key" class="dropdown-item" @click="
                    () => {
                      columns.indexOf(key) === -1
                        ? columns.splice(Object.keys(formFields).indexOf(key), 0, key)
                        : columns.splice(columns.indexOf(key), 1)
                      columnDropDown = false
                    }
                  ">
                    <font-awesome-icon v-if="columns.indexOf(key) !== -1" icon="check" />
                    {{ field.label || key }}
                  </button>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, rowIdx) in items" :key="item.tag_uuid || rowIdx"
              :class="{ 'item-error': item.tag_uuid && errorItems.includes(item.tag_uuid) }">
              <td v-for="col in columns" :key="col" :class="{
                'invalid-cell':
                  !rowEmpty(item) &&
                  formFields[col]?.required &&
                  (item[col] === undefined || item[col] === ''),
              }">
                <component v-if="formFields[col]" :is="getFieldComponent(formFields[col].type)" :name="col"
                  :label="formFields[col].label" :value="item[col]" :disabled="false"
                  :required="!rowEmpty(item) && formFields[col].required" hide-label borderless @update:value="
                    (val: string | number | boolean | string[]) =>
                      updateField(val, rowIdx, col, formFields[col].type)
                  " />
                <span v-else>-</span>
              </td>
              <td class="button-column">
                <button v-if="items.length > 1 && rowIdx !== items.length - 1" type="button"
                  class="btn btn-danger btn-sm" @click="removeRow(rowIdx)">
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="d-flex justify-content-between align-items-center">
        <button type="submit" class="btn btn-primary mt-2">Submit All</button>
      </div>
    </form>
    <div v-if="submitErrorStatus === 406" class="alert alert-danger mt-2">
      <span> Some items were not updated because they already exist in the database.</span>
      <button type="button" class="btn btn-link" @click="filterErrorUUIDs()">
        Remove skipped Duplicates
      </button>
    </div>
    <div v-else-if="submitError" class="alert alert-danger mt-2">{{ submitError }}</div>
    <div v-if="submitSuccess" class="alert alert-success mt-2">Items imported successfully!</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, watch, onMounted, onUnmounted, ref } from 'vue'
import axios from 'axios'
import { formFields } from '@/interfaces/FormField.interface'
import eventBus from '@/stores/eventBus'
import { fieldTypeToComponent } from '@/utils/form.helper'
import { clientStore } from '@/stores/clientStore'
import { EventAction } from '../interfaces/EventAction'
import type { components } from '@/interfaces/api-types'

import TextField from '@/components/fields/TextField.vue'
import TextAreaField from '@/components/fields/TextAreaField.vue'
import ObjectField from '@/components/fields/ObjectField.vue'
import LoadingField from '@/components/fields/LoadingField.vue'
import CheckboxField from '@/components/fields/CheckboxField.vue'
import ArrayField from '@/components/fields/ArrayField.vue'
import ModalField from '@/components/fields/ModalField.vue'
import NumberField from '@/components/fields/NumberField.vue'
import ItemField from '@/components/fields/ItemField.vue'
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue'

type Item = components['schemas']['Item'] & { [key: string]: unknown }

const DEFAULT_COLUMNS = [
  'tag_uuid',
  'short_name',
  'amount',
  'item_type',
  'container_tag_uuid',
  'consumable',
]

export default defineComponent({
  name: 'ItemsFormList',
  components: {
    TextField,
    TextAreaField,
    ObjectField,
    LoadingField,
    CheckboxField,
    ArrayField,
    ModalField,
    NumberField,
    ItemField,
    ImageThumbnailField,
  },
  setup() {
    const columns = reactive([...DEFAULT_COLUMNS])
    const submitError = ref('')
    const submitErrorStatus = ref(null)
    const errorItems = ref<Array<string>>([])
    const submitSuccess = ref(false)
    const saved_action = ref<EventAction | null>(null)
    const emptyItem: Partial<Item> = { consumable: false, amount: 1 }
    const items = reactive<Array<Partial<Item>>>([Object.assign({}, emptyItem)])
    const columnDropDown = ref(false)
    const editable = ref(true)

    // Draggable column widths
    const defaultWidth = 160
    const columnWidths = reactive<Record<string, number>>(
      columns.reduce(
        (acc, col) => {
          acc[col] = defaultWidth
          return acc
        },
        {} as Record<string, number>,
      ),
    )
    const resizingCol = ref<string | null>(null)
    let startX = 0
    let startWidth = 0

    const startResize = (e: MouseEvent, col: string) => {
      resizingCol.value = col
      startX = e.clientX
      startWidth = columnWidths[col]
      document.addEventListener('mousemove', onResize)
      document.addEventListener('mouseup', stopResize)
    }

    /**
     * Handles resizing of table columns by dragging the resize handle.
     * Resizes the selected column and proportionally adjusts the widths of columns to its right,
     * ensuring no column becomes smaller than the minimum width.
     */
    const onResize = (e: MouseEvent) => {
      if (!resizingCol.value) return
      const col = resizingCol.value
      const dx = e.clientX - startX

      // Initialize column widths if missing
      columns.forEach((c) => {
        if (!isFinite(columnWidths[c])) columnWidths[c] = defaultWidth
      })

      const colIdx = columns.indexOf(col)
      const rightCols = columns.slice(colIdx + 1)
      if (!rightCols.length) return // No columns to the right, do not resize

      const viewWidth = document.documentElement.clientWidth
      const parentWidth = document.querySelector('.table-responsive')?.clientWidth || viewWidth


      // Ensure right columns have initialized widths
      rightCols.forEach((c) => {
        if (!isFinite(columnWidths[c])) columnWidths[c] = defaultWidth
      })

      const minWidth = 60
      const newWidth = Math.max(minWidth, startWidth + dx)
      const delta = newWidth - columnWidths[col]
      const rightTotalWidth = rightCols.reduce((sum, c) => sum + columnWidths[c], 0)

      // Check if resizing would shrink any right column below minWidth
      const canResize = rightCols.every((c) => {
        const proportion = columnWidths[c] / rightTotalWidth
        const newRightWidth = columnWidths[c] - delta * proportion
        return newRightWidth >= minWidth && newRightWidth <= parentWidth
      })
      if (!canResize) return

      // Apply new width to the resizing column
      columnWidths[col] = newWidth

      // Adjust right columns proportionally
      rightCols.forEach((c) => {
        const proportion = columnWidths[c] / rightTotalWidth
        columnWidths[c] -= delta * proportion
      })

      // Correct rounding errors to keep total width constant
      const totalWidth = columns.reduce((sum, c) => sum + columnWidths[c], 0)
      const expectedTotal = columns.length * defaultWidth
      if (Math.abs(totalWidth - expectedTotal) > 1) {
        const last = rightCols[rightCols.length - 1]
        columnWidths[last] += expectedTotal - totalWidth
      }
    }

    const stopResize = () => {
      resizingCol.value = null
      document.removeEventListener('mousemove', onResize)
      document.removeEventListener('mouseup', stopResize)
      // Save column widths to localStorage
      localStorage.setItem('itemsFormListColumnWidths', JSON.stringify(columnWidths))
    }

    // Always keep an empty row at the end
    watch(
      items,
      (newItems) => {
        const last = newItems[newItems.length - 1]
        if (!rowEmpty(last)) {
          newItems.push(Object.assign({}, emptyItem))
        }
      },
      { deep: true },
    )

    const toggleColumnDropdown = () => {
      columnDropDown.value = !columnDropDown.value
    }
    const removeRow = (idx: number) => {
      if (items.length > 1) items.splice(idx, 1)
    }

    const handleSubmit = async () => {
      submitError.value = ''
      submitErrorStatus.value = null
      submitSuccess.value = false
      const toSubmit = items.filter((item) => !rowEmpty(item))
      if (!toSubmit.length) {
        submitError.value = 'No items to submit.'
        return
      }

      await axios
        .post('/items/bulk', toSubmit, { validateStatus: (status) => status < 300 })
        .then(() => {
          items.filter((item) => !toSubmit.includes(item))
          submitSuccess.value = true
        })
        .catch((error) => {
          console.error('Error submitting items:', error)
          if (error.response?.status === 422 || error.response?.status === 406) {
            submitErrorStatus.value = error.response?.status
            errorItems.value = error.response?.data?.detail?.error_items
            console.warn(
              'Some items were not updated due to validation errors:',
              error.response?.data?.detail?.error_items,
              errorItems,
            )
          } else {
            submitError.value = error.response?.data?.message || 'Failed to import items.'
          }
        })
    }

    const filterErrorUUIDs = () => {
      if (submitErrorStatus.value !== 406 || !errorItems.value.length) {
        submitErrorStatus.value = null
        errorItems.value = []
        return
      }

      errorItems.value.forEach((uuid) => {
        const idx = items.findIndex((item) => item.tag_uuid === uuid)
        if (idx !== -1) removeRow(idx)
      })
      errorItems.value = []
      submitErrorStatus.value = null
    }

    const fetchAndAddItemToTable = async (scanData: { rfid: string }) => {
      if (clientStore().expected_event_action !== EventAction.FORM_SCAN_ADD) return
      if (!scanData?.rfid) return
      if (items.some((item) => item.tag_uuid === scanData.rfid)) return
      const newRow = Object.assign({}, emptyItem)
      newRow.tag_uuid = scanData.rfid
      try {
        const { data } = await axios.get<Item>(`/items/${scanData.rfid}`)
        Object.assign(newRow, data)
      } catch {
        // If not found, leave as new item
      }
      items.splice(items.length - 1, 0, newRow)
    }

    const setColumnWidthsFromStorage = () => {
      const storedWidths = localStorage.getItem('itemsFormListColumnWidths')
      if (storedWidths) {
        const parsedWidths = JSON.parse(storedWidths)
        Object.keys(parsedWidths).forEach((col) => {
          if (!columns.includes(col)) {
            columns.push(col)
          }
          columnWidths[col] = parsedWidths[col]
        })
      }
    }

    onMounted(() => {
      saved_action.value = clientStore().expected_event_action
      setColumnWidthsFromStorage()
      clientStore().setExpectedEventAction(EventAction.FORM_SCAN_ADD)
      eventBus.on(EventAction.FORM_SCAN_ADD, async (scanData: { rfid: string }) =>
        fetchAndAddItemToTable(scanData),
      )
    })

    onUnmounted(() => {
      eventBus.off(EventAction.FORM_SCAN_ADD)
      if (saved_action.value) clientStore().setExpectedEventAction(saved_action.value)
    })

    const getFieldComponent = (type: string) => fieldTypeToComponent(type)

    const rowEmpty = (item: Partial<Item>) => {
      return Object.keys(item).every(
        (key) =>
          item[key] === emptyItem[key] ||
          item[key] === undefined ||
          item[key] === null ||
          item[key] === '',
      )
    }
    const updateField = (
      value: boolean | string | number | Array<string>,
      rowIdx: number,
      col: string,
      type: string,
    ) => {
      if (!editable.value) {
        console.warn('Edit blocked, not updating field:', col)
        return
      }
      submitSuccess.value = false
      if (type === 'checkbox') {
        items[rowIdx][col] = Boolean(value)
      } else if (type === 'epoch') {
        items[rowIdx][col] = new Date(value as string).getTime() / 1000
      } else if (type === 'number') {
        items[rowIdx][col] = Number(value)
      } else if (type === 'array') {
        items[rowIdx][col] = value
      } else if (col === 'container_tag_uuid') {
        items[rowIdx][col] = '' + value
        if (value) {
          axios
            .get<Item>(`/items/${value}`)
            .then((response) => (items[rowIdx]['container'] = response.data))
        } else {
          items[rowIdx]['container'] = undefined // Clear the field if no value
        }
      } else {
        items[rowIdx][col] = value
      }
    }

    // CSV parsing utility that handles quoted fields with commas
    function parseCsv(csv: string): Array<Record<string, string>> {
      const lines = csv.trim().split(/\r?\n/)
      if (lines.length < 2) return []
      // Parse a CSV line into fields, handling quoted commas
      function parseLine(line: string): string[] {
        const result: string[] = []
        let field = ''
        let inQuotes = false
        for (let i = 0; i < line.length; i++) {
          const char = line[i]
          if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
              field += '"'
              i++
            } else {
              inQuotes = !inQuotes
            }
          } else if (char === ',' && !inQuotes) {
            result.push(field)
            field = ''
          } else {
            field += char
          }
        }
        result.push(field)
        return result.map((f) => f.trim())
      }
      const headers = parseLine(lines[0])
      return lines.slice(1).map((line) => {
        const values = parseLine(line)
        const row: Record<string, string> = {}
        headers.forEach((h, i) => {
          row[h] = values[i] ?? ''
        })
        return row
      })
    }

    // Handle CSV file upload
    const handleCsvUpload = (e: Event) => {
      const input = e.target as HTMLInputElement
      if (!input.files?.length) return
      const file = input.files[0]
      const reader = new FileReader()
      reader.onload = (event) => {
        const text = event.target?.result as string
        const rows = parseCsv(text)
        console.log('Reading CSV file:', file.name, 'Parsed rows:', rows)
        // Map CSV rows to Item objects and add to items array (before the empty row)
        rows.forEach((row) => {
          const item: Item = {} as Item
          // Ensure all expected columns have the correct type
          Object.keys(row).forEach((key) => {
            if (formFields[key]?.type === 'checkbox') {
              item[key] = row[key] === 'true' || row[key] === 'x' || row[key] === '1'
            } else if (formFields[key]?.type === 'number') {
              item[key] = Number(row[key])
            } else if (formFields[key]?.type === 'epoch') {
              const date = new Date(row[key])
              item[key] = isNaN(date.getTime()) ? undefined : date.getTime() / 1000
            } else if (formFields[key]?.type === 'array') {
              item[key] = row[key] ? row[key].split(',').map((v: string) => v.trim()) : []
            } else if (formFields[key]?.type === 'images') {
              item[key] = row[key] ? row[key].split(',').map((url: string) => url.trim()) : []
            } else if (row[key]) {
              item[key] = row[key]
            }
          })
          items.splice(items.length - 1, 0, item)
        })
      }
      reader.readAsText(file)
      // Reset file input so the same file can be uploaded again if needed
      input.value = ''
    }

    const copyColumnNames = () => {
      const columnNames = Object.keys(formFields).join(',')
      if (
        typeof navigator !== 'undefined' &&
        navigator.clipboard &&
        typeof navigator.clipboard.writeText === 'function'
      ) {
        navigator.clipboard
          .writeText(columnNames)
          .then(() => alert(`Column names copied to clipboard:\n${columnNames}`))
          .catch(() => fallbackCopyTextToClipboard(columnNames))
      } else {
        fallbackCopyTextToClipboard(columnNames)
      }
    }

    const resetColumnWidths = () => {
      columns.splice(0, columns.length, ...DEFAULT_COLUMNS)
      columns.forEach((col) => {
        columnWidths[col] = defaultWidth
      })
      localStorage.removeItem('itemsFormListColumnWidths')
    }

    const fallbackCopyTextToClipboard = (text: string) => {
      const textArea = document.createElement('textarea')
      textArea.value = text
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      alert(`Column names copied to clipboard:\n${text}`)
    }

    return {
      columns,
      items,
      formFields,
      removeRow,
      handleSubmit,
      submitError,
      submitErrorStatus,
      submitSuccess,
      getFieldComponent,
      updateField,
      columnWidths,
      startResize,
      rowEmpty,
      handleCsvUpload,
      toggleColumnDropdown,
      columnDropDown,
      copyColumnNames,
      resetColumnWidths,
      filterErrorUUIDs,
      errorItems,
    }
  },
})
</script>
<style scoped>
:global(#app) {
  max-width: 100vw !important;
}

/* Table Styles */
.table-responsive {
  width: 100%;
  max-width: 100vw;
}

.table {
  /* width: 92%;  enable for scrolling */
  width: unset;
  table-layout: fixed;
}

@media screen and (max-width: 768px) {
  .table {
    width: 92%;
  }
}

th,
td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

th:last-child,
td:last-child {
  width: 1%;
  white-space: nowrap;
  overflow: visible;
  text-overflow: initial;
}

.button-column {
  max-width: 100px;
  border: none;
}

/* Form Field Styles */
td .form-group {
  padding: 0 !important;
  margin-bottom: 0 !important;
}

td .form-group>label {
  display: none !important;
}

td .form-group>input.form-control {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* Validation & Error Styles */
td.invalid-cell {
  background-color: #f8d7da;
  color: #721c24;
}

.item-error {
  background-color: #fdde9a;
  color: #e99f00;
}

.draggable-th {
  position: relative;
  user-select: none;
  min-width: 60px;
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.resize-handle {
  width: 8px;
  height: 100%;
  cursor: col-resize;
  display: inline-block;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 2;
  background: transparent;
  transition: background 0.2s;
}

.resize-handle:hover {
  background-color: #ddd;
}

.resize-handle:active {
  background-color: #bbb;
}

.dropdown-menu {
  position: absolute;
  display: block;
  top: 1%;
  left: 10%;
  z-index: 1000;
}
</style>
