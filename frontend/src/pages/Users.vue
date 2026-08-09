<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"
import {useRouter} from "vue-router"
const router=useRouter()
const users=ref([]); const name=ref(""); const error=ref(""); const links=ref({})
const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
async function load(){if(!localStorage.token){router.push("/login");return};try{users.value=(await axios.get("/api/users",{headers:headers()})).data}catch(e){error.value=e.response?.data?.detail||"Load failed"}}
async function add(){try{await axios.post("/api/users",{username:name.value},{headers:headers()});name.value="";await load()}catch(e){error.value=e.response?.data?.detail||"Create failed"}}
async function remove(id){if(confirm("Delete user?")){await axios.delete(`/api/users/${id}`,{headers:headers()});await load()}}
async function showLinks(id){links.value=(await axios.get(`/api/users/${id}/links`,{headers:headers()})).data}
onMounted(load)
</script>
<template><div class="card"><h1>Users</h1><input v-model="name" placeholder="username"><button @click="add">Create</button><p v-if="error">{{error}}</p>
<table><tr><th>Username</th><th>UUID</th><th>Enabled</th><th>Actions</th></tr>
<tr v-for="u in users" :key="u.id"><td>{{u.username}}</td><td><code>{{u.uuid}}</code></td><td>{{u.enabled}}</td><td><button @click="showLinks(u.id)">Links</button><button @click="remove(u.id)">Delete</button></td></tr></table>
<div v-if="links.links"><h3>{{links.user.username}} links</h3><div v-for="l in links.links" :key="l.inbound_id"><b>{{l.name}}</b><br><textarea rows="3" style="width:100%">{{l.uri}}</textarea></div></div>
</div></template>
