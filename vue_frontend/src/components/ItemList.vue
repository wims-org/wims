<template>
    <div class="container">
        <h3 class="mt-4">{{ title }}</h3>
        <div class="list-group">
            <div v-for="item in items" :key="item.tag_uuid" 
                class="list-group-item list-group-item-action" @click="selectItem(item)">
                <h5 class="mb-1">{{ item.short_name }}</h5>
                <p class="mb-1">{{ item.description }}</p>
        </div>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
import type { components } from '@/interfaces/api-types';
type Item = components['schemas']['Item'] & { [key: string]: unknown };

export default defineComponent({
    props: {
        items: {
            type: Array as PropType<Item[]>,
            required: true
        },
        title: {
            type: String,
            default: 'Item List'
        }
    },
    emits: ['select'],
    methods: {
        selectItem(item: Item) {
            this.$emit('select', item);
        }
    }
});
</script>

<style scoped>
.container {
    margin-top: 20px;
}
</style>
