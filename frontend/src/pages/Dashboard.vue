<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"; import {useRouter} from "vue-router"
const router=useRouter(); const token=localStorage.token; const h={Authorization:`Bearer ${token}`}
const health=ref({}); const cap=ref({}); const xray=ref({}); const reality=ref({}); const error=ref("")
async function load(){
 if(!token){router.push('/login');return}
 try{health.value=(await axios.get('/api/health')).data}catch{}
 try{cap.value=(await axios.get('/api/system/capabilities',{headers:h})).data}catch(e){error.value=e.response?.data?.detail||'Authorization required'}
 try{xray.value=(await axios.get('/api/xray/status',{headers:h})).data}catch{}
 try{reality.value=(await axios.get('/api/xray/reality',{headers:h})).data}catch(e){reality.value={error:e.response?.data?.detail||'REALITY unavailable'}}
}
async function restart(){await axios.post('/api/xray/restart',{}, {headers:h});await load()}
onMounted(load)
</script>
<template><div>
<div class="card"><h1>Dashboard</h1><p>Health: {{health.status}}</p><p>Database: {{health.database}}</p><p>Xray: <b>{{xray.status || health.xray}}</b> <button @click="restart">Restart Xray</button></p><p v-if="error">{{error}}</p></div>
<div class="card"><h2>Railway</h2><p>Environment: {{cap.environment}}</p><p>Public HTTP: {{cap.public_domain||'—'}}</p><p>TCP Proxy: <b>{{cap.tcp_proxy ? cap.tcp_proxy_domain+':'+cap.tcp_proxy_port : 'Disabled'}}</b></p><p>TCP application port: {{cap.tcp_application_port||'—'}}</p><p>Volume: {{cap.volume_mount_path||'—'}}</p><p v-if="!cap.tcp_proxy">بدون TCP Proxy، HTTPS دامنه Railway در Edge خاتمه می‌یابد؛ برای XHTTP/WS از TLS لبه‌ای استفاده می‌شود. REALITY نیاز به مسیر TCP مستقیم دارد.</p></div>
<div class="card"><h2>REALITY</h2><p v-if="reality.error">{{reality.error}}</p><p v-else>Keypair: <b>ready</b></p><p v-if="reality.serverName">Server Name: {{reality.serverName}}</p><p v-if="reality.shortId">Short ID: {{reality.shortId}}</p><p v-if="reality.publicKey">Public Key: <code>{{reality.publicKey}}</code></p></div>
</div></template>
