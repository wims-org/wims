<template>
    <div class="container">
        <h1 class="my-4">Item List</h1>
        <div class="list-group">
            <router-link v-for="item in items" :key="item.tag_uuid" :to="'/item/' + item.tag_uuid"
                class="list-group-item list-group-item-action">
                <h5 class="mb-1">{{ item.name }}</h5>
                <p class="mb-1">{{ item.description }}</p>
            </router-link>
        </div>
    </div>
</template>

<script lang="ts">

import { defineComponent } from 'vue';
import type { PropType } from 'vue';

interface Item {
    tag_uuid: string;
    name: string;
    description: string;
}

export default defineComponent({
    props: {
        items: {
            type: Array as PropType<Item[]>,
            required: true
        }
    }
});
</script>

<style scoped>
.container {
    margin-top: 20px;
}
</style>
