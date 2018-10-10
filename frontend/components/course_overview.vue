<template lang="pug">
    div
        h1 Courses overview

        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .pull-right.input-group.form-inline
            span.input-group-addon Search
            input.form-control(type="text", v-model="search", @keyup="searchDebouncer()")

        table.table.table-striped.table-hover
            thead
                tr
                    th
                    th Name
                    th Description
            tbody(v-if="courses.length > 0")
                tr(v-for="course in courses")
                    td
                        label.form-checkbox

                            input(type="radio", v-bind:value="course.id", v-model="selectedCourseId")
                            i.form-icon
                    td {{ course.name }}
                    td {{ course.description }}

            tbody(v-if="courses.length === 0")
                tr
                    td
                    td No courses found
                    td

            tfoot
                tr
                    th
                    th Name
                    th Description

        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .btn-group
            a.btn.btn-success(@click="addCourseBtn")
                i.fa.fa-plus
                |  Add
            a.btn.btn-warning(@click="editCourseBtn")
                i.fa.fa-edit
                |  Edit
            a.btn.btn-danger(@click="removeCourseBtn")
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
    import {Course} from "../types/examination";

    @Component({name: 'course-overview', components: {Pagination}})
    export default class CourseOverview extends Vue {

        private courses: Course[] = [];
        private page: number = 1;
        private pageCount = 1;
        private search: string = "";
        private searchDebouncer = debounce(this.searchEvent, 300);
        private selectedCourseId: number | null = null;


        private async created() {
            await this.loadCourses();
        }


        private async searchEvent() {
            this.page = 1;
            await this.loadCourses();
        }

        private async loadCourses() {
            const resp = await instance.get(Flask.url_for("api.courses", {
                search: this.search,
                page: this.page
            }));

            this.courses = resp.data.data;
            this.pageCount = resp.data.page_count;
            this.page = resp.data.page;
        }

        private async removeCourseBtn() {
            if (this.selectedCourseId === null) {
                alert("No course selected");
                return;
            }

            if (!confirm("Are you sure you want to remove selected course?")) {
                return;
            }
            try {
                await instance.delete(Flask.url_for("api.course", {
                    course_id: this.selectedCourseId,
                }));
            } catch (error) {
                if (error.response.status === 409) {
                    alert("Error! Course still has examination coupled");
                }
            }

            this.selectedCourseId = null;
            await this.loadCourses();
        }

        private async pageSwitch(pageNew: number) {
            this.page = pageNew;
            await this.loadCourses();
        }

        private addCourseBtn() {
            location.href = Flask.url_for('course.add_course', {}) + "?redir=courses";
        }

        private editCourseBtn() {
            location.href = Flask.url_for('course.edit_course', {course_id: this.selectedCourseId});
        }

        private backBtn() {
            location.href = Flask.url_for("examination.view_examination", {});
        }
    }
</script>

<style lang="sass" scoped>
    .pull-right.input-group.form-inline
        width: 250px
</style>