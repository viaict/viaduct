<template lang="pug">
    .btn-group
        input.btn.btn-primary(type="button", @click="pageSwitch(page - 1)", :disabled="page === 1", value="<")

        input.btn(type="button", v-if="page >= 3", @click="pageSwitch(1)", value="1", :class="classes(1)", :disabled="page === 1")
        input.btn.btn-default(type="button", v-if="page > 3", value="…", @click="promptPage")

        input.btn(type="button", v-for="pageNum in pageCount", 
        v-if="pageNum > page - 2 && pageNum < page + 2"
        @click="pageSwitch(pageNum)", :value="pageNum", :class="classes(pageNum)", :disabled="page === pageNum")

        input.btn.btn-default(type="button", v-if="page < pageCount - 2", value="…", @click="promptPage")
        input.btn(type="button", v-if="page <= pageCount - 2", @click="pageSwitch(pageCount)",
        :value="pageCount", :class="classes(pageCount)")

        input.btn.btn-primary(type="button", @click="pageSwitch(page + 1)", :disabled="page === pageCount", value=">")
</template>

<script lang="ts">
    import Vue from "vue"
    import {Component, Prop} from "vue-property-decorator"

    @Component
    export default class Pagination extends Vue {
        @Prop() page;
        @Prop() pageSwitch;
        @Prop() pageCount;

        private classes(page: number): { 'btn-primary': boolean, 'btn-default': boolean } {
            return {
                'btn-primary': page === this.page,
                'btn-default': page !== this.page,
            }
        }

        private promptPage() {
            const input = prompt("Page?");
            if (input === null) {
                return
            }

            const page = Math.max(1, Math.min(this.pageCount, parseInt(input)));
            if (!isNaN(page)) {
                this.pageSwitch(page)
            }
        }
    }
</script>

<style lang="sass" scoped>

</style>