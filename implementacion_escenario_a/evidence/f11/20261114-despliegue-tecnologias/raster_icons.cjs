const path=require('path');
const fs=require('fs');
const sharp=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1111-570-0_26.1111.570.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/sharp');
(async()=>{
 for(const file of fs.readdirSync(path.join(__dirname,'icons')).filter(x=>x.endsWith('.svg'))){
  await sharp(path.join(__dirname,'icons',file),{density:300}).resize(180,180,{fit:'inside'}).png().toFile(path.join(__dirname,'icons',file.replace('.svg','.png')));
 }
})();
