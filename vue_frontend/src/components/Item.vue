<template>
    <div class="container mt-5">
        <button @click="toggleDetails" class="btn btn-secondary mb-3">
            {{ showDetails ? 'Hide Details' : 'Show Details' }}
        </button>
        <h1 class="mb-4">Item Details</h1>
        <form v-if="item" @submit.prevent="handleSubmit">
            <div class="form-group" v-for="(field, key) in formFields" :key="key" v-show="!field.hidden && (!field.details || (showDetails && field.details))">
                <label :for="key">{{ field.label }}</label>
                <input v-if="field.type !== 'textarea'" :type="field.type" :name="key" :disabled="field.disabled" 
                    v-model="item[key]" class="form-control" />
                <textarea v-else :name="key" :disabled="field.disabled" v-model="item[key]" class="form-control"></textarea>
            </div>
            <button type="submit" class="btn btn-primary mt-3">Submit</button>
        </form>
        <div v-else>
            <p>Error loading item details. Please try again later.</p>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import axios from 'axios';


import { FormField } from "@/interfaces/FormField.interface";
import useValidate, { ValidationArgs } from "@vuelidate/core";

const formFields = {
    tag_uuid: { label: 'Tag UUID', type: 'text', disabled: true, hidden: false, details: false },
    short_name: { label: 'Short Name', type: 'text', disabled: false, hidden: false, details: true },
    amount: { label: 'Amount', type: 'number', disabled: false, hidden: false, details: false },
    item_type: { label: 'Item Type', type: 'text', disabled: false, hidden: false, details: false },
    consumable: { label: 'Consumable', type: 'checkbox', disabled: false, hidden: false, details: false },
    created_at: { label: 'Created At', type: 'text', disabled: true, hidden: false, details: false },
    created_by: { label: 'Created By', type: 'text', disabled: true, hidden: false, details: false },
    changes: { label: 'Changes', type: 'array', disabled: true, hidden: true, details: false },
    ai_generated: { label: 'AI Generated', type: 'array', disabled: true, hidden: true, details: false },
    description: { label: 'Description', type: 'textarea', disabled: false, hidden: false, details: true },
    min_amount: { label: 'Minimum Amount', type: 'number', disabled: false, hidden: false, details: false },
    tags: { label: 'Tags', type: 'array', disabled: false, hidden: false, details: false },
    images: { label: 'Images', type: 'array', disabled: false, hidden: false, details: true },
    cost_new: { label: 'Cost New', type: 'number', disabled: false, hidden: false, details: false },
    acquisition_date: { label: 'Acquisition Date', type: 'number', disabled: false, hidden: false, details: false },
    cost_used: { label: 'Cost Used', type: 'number', disabled: false, hidden: false, details: false },
    manufacturer: { label: 'Manufacturer', type: 'text', disabled: false, hidden: false, details: false },
    model_number: { label: 'Model Number', type: 'text', disabled: false, hidden: false, details: false },
    manufacturing_date: { label: 'Manufacturing Date', type: 'number', disabled: false, hidden: false, details: false },
    upc: { label: 'UPC', type: 'text', disabled: false, hidden: false, details: false },
    asin: { label: 'ASIN', type: 'text', disabled: false, hidden: false, details: false },
    serial_number: { label: 'Serial Number', type: 'text', disabled: false, hidden: false, details: false },
    vendors: { label: 'Vendors', type: 'array', disabled: false, hidden: false, details: true },
    shop_url: { label: 'Shop URL', type: 'array', disabled: false, hidden: false, details: true },
    size: { label: 'Size', type: 'object', disabled: false, hidden: false, details: false },
    documentation: { label: 'Documentation', type: 'array', disabled: false, hidden: false, details: true },
    related_items: { label: 'Related Items', type: 'array', disabled: false, hidden: false, details: true },
    container_tag_uuid: { label: 'Container Tag UUID', type: 'text', disabled: false, hidden: true, details: false },
    current_location: { label: 'Current Location', type: 'text', disabled: false, hidden: false, details: false },
    borrowed_by: { label: 'Borrowed By', type: 'unix_epoch', disabled: false, hidden: false, details: false },
    borrowed_at: { label: 'Borrowed At', type: 'unix_epoch', disabled: false, hidden: false, details: false },
    borrowed_until: { label: 'Borrowed Until', type: 'text', disabled: false, hidden: false, details: false },
    owner: { label: 'Owner', type: 'text', disabled: false, hidden: false, details: false }
};


export default defineComponent({
    props: {
        formFields: {
            type: Object as PropType<{ [key: string]: FormField }>,
            required: true,
        },
        schema: {
            type: Object as PropType<ValidationArgs>,
            required: true,
        },
    },
    data() {
        return {
            rfid: this.$route.params.rfid,
            item: {},
            showDetails: false,
            formFields,
        };
    },
    created() {
        this.fetchItem();
    },
    methods: {
        async fetchItem() {
            try {
                const response = await axios.get(`/item/${this.rfid}`);
                this.item = response.data;
                console.log('Item:', this.item);
            } catch (error) {
                console.error('Error fetching item:', error);
            }
        },
        async handleSubmit() {
            try {
                await axios.post(`http://localhost:5005/item`, this.item);
                alert('Item updated successfully');
            } catch (error) {
                console.error('Error updating item:', error);
            }
        },

        toggleDetails() {
            this.showDetails = !this.showDetails;
        },
        formatDate(timestamp: number): string {
            const date = new Date(timestamp * 1000);
            return date.toISOString().split('T')[0];
        }
    },
});
</script>

<style scoped>
/* Add your styles here */
</style>
