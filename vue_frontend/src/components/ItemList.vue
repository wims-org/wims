<template>
    <div class="container">
        <h1 class="my-4">Item List</h1>
        <div class="list-group">
            <a v-for="item in items" :key="item.tag_uuid" :href="'/item/' + item.tag_uuid" class="list-group-item list-group-item-action">
                <h5 class="mb-1">{{ item.name }}</h5>
                <p class="mb-1">{{ item.description }}</p>
            </a>
        </div>
    </div>
</template>

<script lang="ts">
export default {
    props: {
        items: {
            type: Array,
            required: true
        }
    }
};
</script>

<style scoped>
.container {
    margin-top: 20px;
}
</style>
