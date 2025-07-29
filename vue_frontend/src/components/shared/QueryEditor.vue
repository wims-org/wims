<template>
    <BContainer class="mt-4">
        <BCard>
            <BCardTitle>{{ isEditing ? "Edit Query" : "Create Query" }}</BCardTitle>
            <BCardBody>
                <BForm @submit.prevent="submitQuery">
                    <BFormGroup label="Query Name:" label-for="name">
                        <BForm-input id="name" v-model="query.name" required
                            placeholder="Enter query name"></BForm-input>
                    </BFormGroup>

                    <BFormGroup label="Description:" label-for="description">
                        <BFormTextarea id="description" v-model="query.description"
                            placeholder="Enter query description"></BFormTextarea>
                    </BFormGroup>

                    <BFormGroup label="Query (JSON):" label-for="query">
                        <BFormTextarea id="query" v-model="query.query" required
                            placeholder="Enter MongoDB query as JSON" rows="5"></BFormTextarea>
                    </BFormGroup>

                    <BButton type="button" @click="submitQuery" variant="primary" class="mt-3">
                        {{ isEditing ? "Update Query" : "Create Query" }}
                    </BButton>
                </BForm>

                <BAlert v-if="errorMessage" variant="danger" dismissible class="mt-3">
                    {{ errorMessage }}
                </BAlert>
                <BAlert v-if="successMessage" variant="success" dismissible class="mt-3">
                    {{ successMessage }}
                </BAlert>
            </BCardBody>
        </BCard>
    </BContainer>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue";
import axios from "axios";
import type { Query } from "@/interfaces/queries";
import { logger } from "@sentry/vue";


export default defineComponent({
    name: "QueryEditor",
    props: {
        existingQuery: {
            type: Object as PropType<Query | null>,
            default: null,
        },
    },
    data() {
        return {
            query: {
                _id: "",
                name: "",
                description: "",
                query: ""
            } ,
            isEditing: false,
            errorMessage: null as string | null,
            successMessage: null as string | null,
        };
    },
    created() {
        if (this.existingQuery) {
            this.query = {
                _id: this.existingQuery._id || "",
                name: this.existingQuery.name || "",
                description: this.existingQuery.description ?? "",
                query: typeof this.existingQuery.query === "string"
                    ? this.existingQuery.query
                    : JSON.stringify(this.existingQuery.query ?? {}, null, 2)
            };
            this.isEditing = true;
        }
    },
    methods: {
        async submitQuery(): Promise<void> {
            try {
                this.errorMessage = null;
                this.successMessage = null;
                // Sanitize and format the JSON with best effort
                let parsedQuery;
                try {
                    // Replace single quotes with double quotes, remove trailing commas, etc.
                    const input = this.query.query
                        .replace(/'/g, '"')
                        .replace(/,\s*}/g, '}')
                        .replace(/,\s*]/g, ']');

//                        console.log("Submitting query:", this.query);
                    
                    parsedQuery = JSON.parse(input);
                } catch (e) {
                    logger.error("Invalid JSON format in query", e);
                    this.errorMessage = "Invalid JSON format in query. Please check your input." + (e.message ?? "");
                    return;
                }
                const submit_query = { ...this.query, query: parsedQuery };
                console.log("Submitting query:", submit_query);

                const endpoint = this.isEditing
                    ? `/queries/${this.query._id}`
                    : "/queries";

                const method = this.isEditing ? "put" : "post";

                const response = await axios[method](endpoint, submit_query);
                this.query = response.data;
                this.query.query = JSON.stringify(this.query.query, null, 2);
                this.successMessage = this.isEditing
                    ? "Query updated successfully!"
                    : "Query created successfully!";
                this.$emit("update:query", this.query);
            } catch (error: unknown) {
                if (axios.isAxiosError(error)) {
                    this.errorMessage =
                        error.response?.data?.detail || "An error occurred while saving the query.";
                } else {
                    this.errorMessage = "An unexpected error occurred.";
                }
            }
        },
    },
});
</script>

<style scoped>
.mt-4 {
    margin-top: 1.5rem;
}
</style>