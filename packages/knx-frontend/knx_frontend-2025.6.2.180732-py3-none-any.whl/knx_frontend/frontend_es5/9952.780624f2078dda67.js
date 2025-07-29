"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9952"],{32751:function(e,t,s){s.d(t,{t:()=>o});s(40777),s(2394),s(81738),s(22960),s(21700),s(87799),s(64510);class a{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const s=this._listeners[e].indexOf(t);-1!==s&&this._listeners[e].splice(s,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const s=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(a){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(s,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const i={};function o(e){return(t,s)=>{if("object"==typeof s)throw new Error("This decorator does not support this compilation type.");const o=e.storage||"localStorage";let r;o&&o in i?r=i[o]:(r=new a(window[o]),i[o]=r);const n=e.key||String(s);r.addFromStorage(n);const l=!1!==e.subscribe?e=>r.subscribeChanges(n,((t,a)=>{e.requestUpdate(s,t)})):void 0,h=()=>r.hasKey(n)?e.deserializer?e.deserializer(r.getValue(n)):r.getValue(n):void 0,d=(t,a)=>{let i;e.state&&(i=h()),r.setValue(n,e.serializer?e.serializer(a):a),e.state&&t.requestUpdate(s,i)},c=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,c.call(this)},e.subscribe){const e=t.connectedCallback,s=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=null==l?void 0:l(this))},t.disconnectedCallback=function(){var e;s.call(this);const t=this;null===(e=t.__unbsubLocalStorage)||void 0===e||e.call(t),t.__unbsubLocalStorage=void 0}}const u=Object.getOwnPropertyDescriptor(t,s);let p;if(void 0===u)p={get(){return h()},set(e){(this.__initialized||void 0===h())&&(d(this,e),this.requestUpdate(s,void 0))},configurable:!0,enumerable:!0};else{const e=u.set;p=Object.assign(Object.assign({},u),{},{set(t){(this.__initialized||void 0===h())&&(d(this,t),this.requestUpdate(s,void 0)),null==e||e.call(this,t)}})}Object.defineProperty(t,s,p)}}},35993:function(e,t,s){s.a(e,(async function(e,t){try{s(26847),s(27530);var a=s(73742),i=s(59048),o=s(7616),r=(s(30337),s(97862)),n=(s(40830),e([r]));r=(n.then?(await n)():n)[0];let l,h,d,c,u,p,g=e=>e;const _="M2.2,16.06L3.88,12L2.2,7.94L6.26,6.26L7.94,2.2L12,3.88L16.06,2.2L17.74,6.26L21.8,7.94L20.12,12L21.8,16.06L17.74,17.74L16.06,21.8L12,20.12L7.94,21.8L6.26,17.74L2.2,16.06M13,17V15H11V17H13M13,13V7H11V13H13Z",v="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z";class b extends i.oi{render(){const e=this._result||this.progress;return(0,i.dy)(l||(l=g`
      <ha-button
        .raised=${0}
        .label=${0}
        .unelevated=${0}
        .disabled=${0}
        class=${0}
      >
        <slot name="icon" slot="icon"></slot>
        <slot></slot>
      </ha-button>
      ${0}
    `),this.raised,this.label,this.unelevated,this.disabled||this.progress,this._result||"",e?(0,i.dy)(h||(h=g`
            <div class="progress">
              ${0}
            </div>
          `),"success"===this._result?(0,i.dy)(d||(d=g`<ha-svg-icon .path=${0}></ha-svg-icon>`),v):"error"===this._result?(0,i.dy)(c||(c=g`<ha-svg-icon .path=${0}></ha-svg-icon>`),_):this.progress?(0,i.dy)(u||(u=g`<ha-spinner size="small"></ha-spinner>`)):i.Ld):i.Ld)}actionSuccess(){this._setResult("success")}actionError(){this._setResult("error")}_setResult(e){this._result=e,setTimeout((()=>{this._result=void 0}),2e3)}constructor(...e){super(...e),this.disabled=!1,this.progress=!1,this.raised=!1,this.unelevated=!1}}b.styles=(0,i.iv)(p||(p=g`
    :host {
      outline: none;
      display: inline-block;
      position: relative;
      pointer-events: none;
    }

    ha-button {
      transition: all 1s;
      pointer-events: initial;
    }

    ha-button.success {
      --mdc-theme-primary: white;
      background-color: var(--success-color);
      transition: none;
      border-radius: 4px;
      pointer-events: none;
    }

    ha-button[unelevated].success,
    ha-button[raised].success {
      --mdc-theme-primary: var(--success-color);
      --mdc-theme-on-primary: white;
    }

    ha-button.error {
      --mdc-theme-primary: white;
      background-color: var(--error-color);
      transition: none;
      border-radius: 4px;
      pointer-events: none;
    }

    ha-button[unelevated].error,
    ha-button[raised].error {
      --mdc-theme-primary: var(--error-color);
      --mdc-theme-on-primary: white;
    }

    .progress {
      bottom: 4px;
      position: absolute;
      text-align: center;
      top: 4px;
      width: 100%;
    }

    ha-svg-icon {
      color: white;
    }

    ha-button.success slot,
    ha-button.error slot {
      visibility: hidden;
    }
    :host([destructive]) {
      --mdc-theme-primary: var(--error-color);
    }
  `)),(0,a.__decorate)([(0,o.Cb)()],b.prototype,"label",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],b.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],b.prototype,"progress",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],b.prototype,"raised",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],b.prototype,"unelevated",void 0),(0,a.__decorate)([(0,o.SB)()],b.prototype,"_result",void 0),b=(0,a.__decorate)([(0,o.Mo)("ha-progress-button")],b),t()}catch(l){t(l)}}))},54695:function(e,t,s){s.a(e,(async function(e,a){try{s.r(t),s.d(t,{TTSTryDialog:()=>y});s(26847),s(87799),s(1455),s(27530);var i=s(73742),o=s(59048),r=s(7616),n=s(32751),l=s(29740),h=s(99298),d=(s(56719),s(75055)),c=s(81665),u=s(35993),p=e([u]);u=(p.then?(await p)():p)[0];let g,_,v=e=>e;const b="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M10,16.5L16,12L10,7.5V16.5Z";class y extends o.oi{showDialog(e){this._params=e,this._valid=Boolean(this._defaultMessage)}closeDialog(){this._params=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}get _defaultMessage(){var e,t;const s=null===(e=this._params.language)||void 0===e?void 0:e.substring(0,2),a=this.hass.locale.language.substring(0,2);return s&&null!==(t=this._messages)&&void 0!==t&&t[s]?this._messages[s]:s===a?this.hass.localize("ui.dialogs.tts-try.message_example"):""}render(){return this._params?(0,o.dy)(g||(g=v`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
      >
        <ha-textarea
          autogrow
          id="message"
          .label=${0}
          .placeholder=${0}
          .value=${0}
          @input=${0}
          ?dialogInitialFocus=${0}
        >
        </ha-textarea>

        <ha-progress-button
          .progress=${0}
          ?dialogInitialFocus=${0}
          slot="primaryAction"
          .label=${0}
          @click=${0}
          .disabled=${0}
        >
          <ha-svg-icon slot="icon" .path=${0}></ha-svg-icon>
        </ha-progress-button>
      </ha-dialog>
    `),this.closeDialog,(0,h.i)(this.hass,this.hass.localize("ui.dialogs.tts-try.header")),this.hass.localize("ui.dialogs.tts-try.message"),this.hass.localize("ui.dialogs.tts-try.message_placeholder"),this._defaultMessage,this._inputChanged,!this._defaultMessage,this._loadingExample,Boolean(this._defaultMessage),this.hass.localize("ui.dialogs.tts-try.play"),this._playExample,!this._valid,b):o.Ld}async _inputChanged(){var e;this._valid=Boolean(null===(e=this._messageInput)||void 0===e?void 0:e.value)}async _playExample(){var e;const t=null===(e=this._messageInput)||void 0===e?void 0:e.value;if(!t)return;const s=this._params.engine,a=this._params.language,i=this._params.voice;a&&(this._messages=Object.assign(Object.assign({},this._messages),{},{[a.substring(0,2)]:t})),this._loadingExample=!0;const o=new Audio;let r;o.play();try{r=(await(0,d.aT)(this.hass,{platform:s,message:t,language:a,options:{voice:i}})).path}catch(n){return this._loadingExample=!1,void(0,c.Ys)(this,{text:`Unable to load example. ${n.error||n.body||n}`,warning:!0})}o.src=r,o.addEventListener("canplaythrough",(()=>o.play())),o.addEventListener("playing",(()=>{this._loadingExample=!1})),o.addEventListener("error",(()=>{(0,c.Ys)(this,{title:"Error playing audio."}),this._loadingExample=!1}))}constructor(...e){super(...e),this._loadingExample=!1,this._valid=!1}}y.styles=(0,o.iv)(_||(_=v`
    ha-dialog {
      --mdc-dialog-max-width: 500px;
    }
    ha-textarea,
    ha-select {
      width: 100%;
    }
    ha-select {
      margin-top: 8px;
    }
    .loading {
      height: 36px;
    }
  `)),(0,i.__decorate)([(0,r.Cb)({attribute:!1})],y.prototype,"hass",void 0),(0,i.__decorate)([(0,r.SB)()],y.prototype,"_loadingExample",void 0),(0,i.__decorate)([(0,r.SB)()],y.prototype,"_params",void 0),(0,i.__decorate)([(0,r.SB)()],y.prototype,"_valid",void 0),(0,i.__decorate)([(0,r.IO)("#message")],y.prototype,"_messageInput",void 0),(0,i.__decorate)([(0,n.t)({key:"ttsTryMessages",state:!1,subscribe:!1})],y.prototype,"_messages",void 0),y=(0,i.__decorate)([(0,r.Mo)("dialog-tts-try")],y),a()}catch(g){a(g)}}))}}]);
//# sourceMappingURL=9952.780624f2078dda67.js.map