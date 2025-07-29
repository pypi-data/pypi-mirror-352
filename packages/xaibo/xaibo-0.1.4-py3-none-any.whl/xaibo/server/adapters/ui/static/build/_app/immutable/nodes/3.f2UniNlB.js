import{i as s,Q as o}from"../chunks/C-THBjys.js";import{L as k}from"../chunks/enI69Cz4.js";const u={name:"AgentConfig",kind:"HoudiniQuery",hash:"2898dd6394bb9de81ed3f8dd0644913d533e84cdb12786d0d118f7a0ccc8f1b7",raw:`query AgentConfig($agentId: String!) {
  agentConfig(agentId: $agentId) {
    id
    modules {
      id
      module
      config
      provides
      uses
    }
    exchange {
      module
      protocol
      provider
    }
  }
}
`,rootType:"Query",stripVariables:[],selection:{fields:{agentConfig:{type:"AgentConfig",keyRaw:"agentConfig(agentId: $agentId)",selection:{fields:{id:{type:"String",keyRaw:"id",visible:!0},modules:{type:"ModuleConfig",keyRaw:"modules",selection:{fields:{id:{type:"String",keyRaw:"id",visible:!0},module:{type:"String",keyRaw:"module",visible:!0},config:{type:"JSON",keyRaw:"config",nullable:!0,visible:!0},provides:{type:"String",keyRaw:"provides",nullable:!0,visible:!0},uses:{type:"String",keyRaw:"uses",nullable:!0,visible:!0}}},visible:!0},exchange:{type:"ExchangeConfig",keyRaw:"exchange",selection:{fields:{module:{type:"String",keyRaw:"module",visible:!0},protocol:{type:"String",keyRaw:"protocol",visible:!0},provider:{type:"JSON",keyRaw:"provider",visible:!0}}},visible:!0}}},visible:!0}}},pluginData:{"houdini-svelte":{}},input:{fields:{agentId:"String"},types:{},defaults:{},runtimeScalars:{}},policy:"CacheAndNetwork",partial:!1},d={name:"DebugTrace",kind:"HoudiniQuery",hash:"c2b17d8e392c9163f2da6110cd3807daa4dd6b0038b150755251093e966616d0",raw:`query DebugTrace($agentId: String!) {
  debugLog(agentId: $agentId) {
    agentId
    events {
      agent_id: agentId
      event_name: eventName
      event_type: eventType
      module_id: moduleId
      module_class: moduleClass
      method_name: methodName
      time
      call_id: callId
      caller_id: callerId
      arguments
      result
      exception
    }
  }
}
`,rootType:"Query",stripVariables:[],selection:{fields:{debugLog:{type:"DebugTrace",keyRaw:"debugLog(agentId: $agentId)",selection:{fields:{agentId:{type:"String",keyRaw:"agentId",visible:!0},events:{type:"Event",keyRaw:"events",selection:{fields:{agent_id:{type:"String",keyRaw:"agent_id",visible:!0},event_name:{type:"String",keyRaw:"event_name",visible:!0},event_type:{type:"String",keyRaw:"event_type",visible:!0},module_id:{type:"String",keyRaw:"module_id",visible:!0},module_class:{type:"String",keyRaw:"module_class",visible:!0},method_name:{type:"String",keyRaw:"method_name",visible:!0},time:{type:"Float",keyRaw:"time",visible:!0},call_id:{type:"String",keyRaw:"call_id",visible:!0},caller_id:{type:"String",keyRaw:"caller_id",visible:!0},arguments:{type:"JSON",keyRaw:"arguments",nullable:!0,visible:!0},result:{type:"JSON",keyRaw:"result",nullable:!0,visible:!0},exception:{type:"String",keyRaw:"exception",nullable:!0,visible:!0}}},visible:!0}}},visible:!0}}},pluginData:{"houdini-svelte":{}},input:{fields:{agentId:"String"},types:{},defaults:{},runtimeScalars:{}},policy:"CacheAndNetwork",partial:!1};class c extends o{constructor(){super({artifact:u,storeName:"AgentConfigStore",variables:!0})}}async function g(t){await s();const i=new c;return await i.fetch(t),{AgentConfig:i}}class y extends o{constructor(){super({artifact:d,storeName:"DebugTraceStore",variables:!0})}}async function p(t){await s();const i=new y;return await i.fetch(t),{DebugTrace:i}}async function b(...t){const i=[],a=e=>"then"in e&&"finally"in e&&"catch"in e;for(const e of t){if(!a(e)&&"then"in e)throw new Error("❌ `then` is not a valid key for an object passed to loadAll");if(a(e))i.push(e);else for(const[l,r]of Object.entries(e))if(a(r))i.push(r);else throw new Error(`❌ ${l} is not a valid value for an object passed to loadAll. You must pass the result of a load_Store function`)}await Promise.all(i);let n={};for(const e of t)a(e)?Object.assign(n,await e):Object.assign(n,Object.fromEntries(await Promise.all(Object.entries(e).map(async([l,r])=>[l,Object.values(await r)[0]]))));return n}const f=async t=>{let{parent:i,params:a}=t;return{breadcrumbs:(await i()).breadcrumbs.concat({name:a.id,href:`/agents/${a.id}`}),...await b(g({event:t,variables:{agentId:a.id}}),p({event:t,variables:{agentId:a.id}}))}},v=Object.freeze(Object.defineProperty({__proto__:null,load:f},Symbol.toStringTag,{value:"Module"}));export{k as component,v as universal};
