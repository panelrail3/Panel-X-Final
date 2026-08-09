<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"
import {useRouter} from "vue-router"
const router=useRouter()
const items=ref([]); const error=ref("")
const form=ref({name:"xhttp",protocol:"vless",transport:"xhttp",security:"reality",listen_port:443,path:"/xhttp",flow:null,settings:{}})
const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
async function load(){
  if(!localStorage.token){router.push("/login");return}
  try{items.value=(await axios.get("/api/inbounds",{headers:headers()})).data}catch(e){error.value=e.response?.data?.detail||"Load failed"}
}
async function add(){
  try{error.value="";await axios.post("/api/inbounds",form.value,{headers:headers()});await load()}
  catch(e){error.value=e.response?.data?.detail||"Create failed"}
}
async function remove(id){
  if(confirm("Delete inbound?")){await axios.delete(`/api/inbounds/${id}`,{headers:headers()});await load()}
}
onMounted(load)
</script>
<template><div class="card">
<h1>Inbounds</h1>
<p><b>Railway:</b> بدون TCP Proxy، HTTPS دامنه Railway در Edge خاتمه می‌یابد و برای XHTTP/WS می‌توان از TLS لبه‌ای استفاده کرد. REALITY فقط با TCP Proxy/VPS قابل استفاده است.</p>
<input v-model="form.name" placeholder="Name">
<select v-model="form.transport"><option value="xhttp">xhttp</option><option value="raw">raw</option><option value="websocket">websocket</option><option value="grpc">grpc</option><option value="httpupgrade">httpupgrade</option></select>
<select v-model="form.security"><option value="none">none</option><option value="tls">tls</option><option value="reality">reality</option></select>
<input v-model.number="form.listen_port" type="number" min="1" max="65535" placeholder="Internal port">
<input v-model="form.path" placeholder="/xhttp">
<button @click="add">Create</button>
<p v-if="error">{{error}}</p>
<table><tr><th>Name</th><th>Protocol</th><th>Transport</th><th>Security</th><th>Port</th><th></th></tr>
<tr v-for="i in items" :key="i.id"><td>{{i.name}}</td><td>{{i.protocol}}</td><td>{{i.transport}}</td><td>{{i.security}}</td><td>{{i.listen_port}}</td><td><button @click="remove(i.id)">Delete</button></td></tr></table>
</div></template>
