<template lang="pug">
    div
        h1 {{ header }}
        
        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .pull-right.input-group.form-inline
            span.input-group-addon Search
            input.form-control(type="text", v-model="search", @keyup="searchDebouncer()")

        table.table.table-striped.table-hover
            thead
                tr
                    th 
                        label.form-checkbox
                            input(type="checkbox", v-model="selectedUsersAll", @click="select")
                            i.form-icon
                    th E-mail address
                    th First name
                    th Last name
                    th Student ID
                    th Member
                    th Favourer
            tbody(v-if="users.length > 0")
                tr(v-for="user in users")
                    td
                        label.form-checkbox
                            input(type="checkbox", :value="user.id", v-model="selectedUsers")
                            i.form-icon
                    td {{ user.email }}
                    td {{ user.first_name }}
                    td {{ user.last_name }}
                    td {{ user.student_id }}
                    td
                        i.fa.fa-check(v-if="user.member")
                    td
                        i.fa.fa-check(v-if="user.favourer")
                        
            tbody(v-if="users.length === 0")
                tr
                    td
                    td No users found
                    - for (var x = 0; x < 5; x++)
                      td

            tfoot
                tr
                    th
                        label.form-checkbox
                            input(type="checkbox", v-model="selectedUsersAll", @click="select")
                            i.form-icon
                    th E-mail address
                    th First name
                    th Last name
                    th Student ID
                    th Member
                    th Favourer

        pagination(:page="page", :page-switch="pageSwitch", :page-count="pageCount", v-if="pageCount > 1")

        .btn-group
            a.btn.btn-success(@click="addUsersBtn")
                i.fa.fa-plus
                |  Add
            a.btn.btn-danger(@click="removeUser", v-if="!addingUsers")
                i.fa.fa-remove
                |  Remove 
            a.btn.btn-primary(@click="backBtn")
                i.fa.fa-arrow-left
                |  Back


</template>

<script lang="ts">
    import Vue from "vue"
    import {Component, Prop} from "vue-property-decorator";
    import instance from "../utils/axios";
    import Flask from "../utils/flask";
    import Pagination from "../components/pagination";
    import debounce from "../utils/debounce";
    import {User} from "../types/user";

    @Component({name: 'group-user-overview', components: {Pagination}})
    export default class GroupUserOverview extends Vue {

        @Prop() private groupId: number;
        @Prop() private groupName: string;
        private usersInGroup: User[] = [];
        private usersAvailable: User[] = [];
        private page: number = 1;
        private pageCount = 1;
        private search: string = "";
        private searchDebouncer = debounce(this.searchEvent, 300);
        private endpoint: string = "api.groups.users";

        private selectedUsersAll: boolean = false;
        private selectedUsers: number[] = [];
        private addingUsers: boolean = false;


        private async created() {
            await this.loadCurrentUsers();
        }
        
        private async updateUsers() {
            if (this.addingUsers)
                await this.loadAvailableUsers();
            else
                await this.loadCurrentUsers();
        }

        private async searchEvent() {
            this.page = 1;
            await this.updateUsers();
        }

        private async loadCurrentUsers() {
            const resp = await instance.get(Flask.url_for(this.endpoint, {
                group_id: this.groupId,
                search: this.search,
                page: this.page
            }));

            this.usersInGroup = resp.data.data;
            this.pageCount = resp.data.page_count;
            this.page = resp.data.page;
        }
        
        private async loadAvailableUsers() {
            const resp = await instance.get(Flask.url_for("api.user", {
                search: this.search,
                page: this.page
            }));

            this.usersAvailable = resp.data.data.filter(
                user => this.usersInGroup.indexOf(user) === -1);
            this.pageCount = resp.data.page_count;
            this.page = resp.data.page;
        }

        private async addUsersToGroup() {
            if (this.selectedUsers.length === 0) {
                alert("No users selected");
                return
            }
            
            if (!confirm("Add selected users to group?")) {
                return
            }
            const body = {
                'user_ids': this.selectedUsers
            };
            const resp = await instance.post(Flask.url_for(this.endpoint, {
                group_id: this.groupId,
            }), body );
        }
        
        private async removeUser() {
            if (this.selectedUsers.length === 0) {
                alert("No users selected");
                return;
            }
            
            if (!confirm("Are you sure you want to remove selected users?")) {
                return;
            }
            
            const body = {
                'user_ids': this.selectedUsers
            };
            const resp = await instance.delete(Flask.url_for(this.endpoint, {
                group_id: this.groupId,
            }), {data: body} );
            
            this.selectedUsers = [];
            await this.loadCurrentUsers();
        }

        private async pageSwitch(pageNew: number) {
            this.page = pageNew;
            await this.updateUsers();
        }
        
        private select() {
            this.selectedUsers = [];
            if (!this.selectedUsersAll) {
                for (let i in this.users) {
                    this.selectedUsers.push(this.users[i].id);
                }
            }
        }
        
        private async addUsersBtn() {
            this.search = "";
            this.page = 1;
            
            if (this.addingUsers) {
                await this.addUsersToGroup();
                await this.loadCurrentUsers();
            } else {
                await this.loadAvailableUsers();
            }
            this.selectedUsers = [];
            this.addingUsers = !this.addingUsers;
        }
        
        private async backBtn() {
            if (this.addingUsers) {
                this.addingUsers = false;
                await this.loadCurrentUsers();
            } else {
                location.href = Flask.url_for("group.view", {});
            }
        }
        
        get users() {
            if (this.addingUsers) 
                return this.usersAvailable;
            else
                return this.usersInGroup;
        }
        
        get header(): string {
            if (this.addingUsers)
                return `Add users to ${this.groupName}`;
            else
                return `${this.groupName} Users`;
        }
    }
</script>

<style lang="sass" scoped>
    .pull-right.input-group.form-inline
        width: 250px

        tbody > tr
            cursor: pointer
</style>