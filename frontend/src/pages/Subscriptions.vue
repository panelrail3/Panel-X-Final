<script setup>
import {ref,onMounted} from "vue"; import axios from "axios"
import {useRouter} from "vue-router"
const router=useRouter(); const users=ref([]), result=ref(null), error=ref("")
const h=()=>({Authorization:`Bearer ${localStorage.token}`})
onMounted(async()=>{if(!localStorage.token){router.push('/login');return}; try{users.value=(await axios.get('/api/users',{headers:h()})).data}catch(e){error.value=e.response?.data?.detail||'Load failed'}})
async function make(id){try{error.value="";result.value=(await axios.post('/api/subscriptions/'+id,{}, {headers:h()})).data}catch(e){result.value=null;error.value=e.response?.data?.detail||'Subscription failed'}}
</script>
<template><div class="card"><h1>Subscriptions</h1><p v-if="error">{{error}}</p><div v-for="u in users" :key="u.id" class="row"><b>{{u.username}}</b><button @click="make(u.id)">Create subscription</button></div><div v-if="result"><p><b>Subscription URL</b></p><textarea rows="3" style="width:100%">{{result.url}}</textarea><p><b>Links</b></p><div v-for="l in result.links" :key="l"><textarea rows="4" style="width:100%">{{l}}</textarea></div></div></div></template>
