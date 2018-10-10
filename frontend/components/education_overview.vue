<template lang="pug">
    div
        h1 Educations overview

        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .pull-right.input-group.form-inline
            span.input-group-addon Search
            input.form-control(type="text", v-model="search", @keyup="searchDebouncer()")

        table.table.table-striped.table-hover
            thead
                tr
                    th
                    th Name
            tbody(v-if="educations.length > 0")
                tr(v-for="education in educations")
                    td
                        label.form-checkbox

                            input(type="radio", v-bind:value="education.id", v-model="selectedEducationId")
                            i.form-icon
                    td {{ education.name }}

            tbody(v-if="educations.length === 0")
                tr
                    td
                    td No educations found
                    td

            tfoot
                tr
                    th
                    th Name

        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .btn-group
            a.btn.btn-success(@click="addEducationBtn")
                i.fa.fa-plus
                |  Add
            a.btn.btn-warning(@click="editEducationBtn")
                i.fa.fa-edit
                |  Edit
            a.btn.btn-danger(@click="removeEducationBtn")
                i.fa.fa-remove
                |  Remove
            a.btn.btn-primary(@click="backBtn")
                i.fa.fa-arrow-left
                |  Back


</template>

<script lang="ts">
    import Vue from "vue"
    import {Component} from "vue-property-decorator";
    import instance from "../utils/axios";
    import Flask from "../utils/flask";
    import Pagination from "../components/pagination";
    import debounce from "../utils/debounce";
    import {Education} from "../types/examination";

    @Component({name: 'education-overview', components: {Pagination}})
    export default class EducationOverview extends Vue {

        private educations: Education[] = [];
        private page: number = 1;
        private pageCount = 1;
        private search: string = "";
        private searchDebouncer = debounce(this.searchEvent, 300);
        private selectedEducationId: number | null = null;


        private async created() {
            await this.loadEducations();
        }


        private async searchEvent() {
            this.page = 1;
            await this.loadEducations();
        }

        private async loadEducations() {
            const resp = await instance.get(Flask.url_for("api.educations", {
                search: this.search,
                page: this.page
            }));

            this.educations = resp.data.data;
            this.pageCount = resp.data.page_count;
            this.page = resp.data.page;
        }

        private async removeEducationBtn() {
            if (this.selectedEducationId === null) {
                alert("No education selected");
                return;
            }

            if (!confirm("Are you sure you want to remove selected education?")) {
                return;
            }
            try {
                await instance.delete(Flask.url_for("api.education", {
                    education_id: this.selectedEducationId,
                }));
            } catch (error) {
                if (error.response.status === 409) {
                    alert("Error! Education still has examination coupled");
                }
            }

            this.selectedEducationId = null;
            await this.loadEducations();
        }

        private async pageSwitch(pageNew: number) {
            this.page = pageNew;
            await this.loadEducations();
        }

        private async addEducationBtn() {
            location.href = Flask.url_for('education.add_education', {}) + "?redir=educations";
        }

        private async editEducationBtn() {
            location.href = Flask.url_for('education.edit_education', {education_id: this.selectedEducationId});
        }

        private async backBtn() {
            location.href = Flask.url_for("examination.view_examination", {});
        }
    }
</script>

<style lang="sass" scoped>
    .pull-right.input-group.form-inline
        width: 250px
</style>