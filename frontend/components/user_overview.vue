<template lang="pug">
    div
        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount")
        
        .pull-right.input-group.form-inline
            span.input-group-addon Search
            input.form-control(type="text", v-model="search", @keyup="searchDebouncer()")

        table.table.table-striped.table-hover
            thead
                tr
                    th E-mail address
                    th First name
                    th Last name
                    th Student ID
                    th Member
                    th Favourer
            tbody
                tr(v-for="user in users", @click="viewProfile(user.id)")
                    td {{ user.email }}
                    td {{ user.first_name }}
                    td {{ user.last_name }}
                    td {{ user.student_id }}
                    td 
                        i.fa.fa-check(v-if="user.member")
                    td 
                        i.fa.fa-check(v-if="user.favourer")
        
            tfoot
                tr
                    th E-mail address
                    th First name
                    th Last name
                    th Student ID
                    th Member
                    th Favourer
    
        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount")


</template>

<script lang="ts">
    import Vue from "vue"
    import {Component} from "vue-property-decorator";
    import instance from "../utils/axios";
    import Flask from "../utils/flask";
    import Pagination from "../components/pagination";
    import debounce from "../utils/debounce";
    import {User} from "../types/user";

    @Component({name: 'user-overview', components: {Pagination}})
    export default class UserOverview extends Vue {
        
        private users: User[] = [];
        private page: number = 1;
        private pageCount = 1;
        private search: string = "";
        private searchDebouncer = debounce(this.searchEvent, 300);
        
        private async created() {
            await this.loadUsers();
        }
        
        private async searchEvent() {
            this.page = 1;
            await this.loadUsers();
        }
        
        private async loadUsers() {
            const resp = await instance.get(Flask.url_for("api.user", {
                search: this.search,
                page: this.page
            }));
            
            this.users = resp.data.data;
            this.pageCount = resp.data.page_count;
            this.page = resp.data.page;
        }
        
        private viewProfile(user_id: number) {
            location.href = Flask.url_for("user.view_single_user", 
                {user_id: user_id});
        }
        
        private async pageSwitch(pageNew: number) {
            this.page = pageNew;
            await this.loadUsers();
        }
    }
</script>

<style lang="sass" scoped>
    .pull-right.input-group.form-inline
        width: 250px

    tbody > tr
        cursor: pointer
</style>