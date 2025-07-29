export const __webpack_ids__=["9952"];export const __webpack_modules__={32751:function(e,t,s){s.d(t,{t:()=>o});class a{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const s=this._listeners[e].indexOf(t);-1!==s&&this._listeners[e].splice(s,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const s=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(a){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(s,t)))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}}const i={};function o(e){return(t,s)=>{if("object"==typeof s)throw new Error("This decorator does not support this compilation type.");const o=e.storage||"localStorage";let r;o&&o in i?r=i[o]:(r=new a(window[o]),i[o]=r);const n=e.key||String(s);r.addFromStorage(n);const l=!1!==e.subscribe?e=>r.subscribeChanges(n,((t,a)=>{e.requestUpdate(s,t)})):void 0,h=()=>r.hasKey(n)?e.deserializer?e.deserializer(r.getValue(n)):r.getValue(n):void 0,d=(t,a)=>{let i;e.state&&(i=h()),r.setValue(n,e.serializer?e.serializer(a):a),e.state&&t.requestUpdate(s,i)},c=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,c.call(this)},e.subscribe){const e=t.connectedCallback,s=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=l?.(this))},t.disconnectedCallback=function(){s.call(this);this.__unbsubLocalStorage?.(),this.__unbsubLocalStorage=void 0}}const u=Object.getOwnPropertyDescriptor(t,s);let p;if(void 0===u)p={get(){return h()},set(e){(this.__initialized||void 0===h())&&(d(this,e),this.requestUpdate(s,void 0))},configurable:!0,enumerable:!0};else{const e=u.set;p={...u,set(t){(this.__initialized||void 0===h())&&(d(this,t),this.requestUpdate(s,void 0)),e?.call(this,t)}}}Object.defineProperty(t,s,p)}}},35993:function(e,t,s){s.a(e,(async function(e,t){try{var a=s(73742),i=s(59048),o=s(7616),r=(s(30337),s(97862)),n=(s(40830),e([r]));r=(n.then?(await n)():n)[0];const l="M2.2,16.06L3.88,12L2.2,7.94L6.26,6.26L7.94,2.2L12,3.88L16.06,2.2L17.74,6.26L21.8,7.94L20.12,12L21.8,16.06L17.74,17.74L16.06,21.8L12,20.12L7.94,21.8L6.26,17.74L2.2,16.06M13,17V15H11V17H13M13,13V7H11V13H13Z",h="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z";class d extends i.oi{render(){const e=this._result||this.progress;return i.dy`
      <ha-button
        .raised=${this.raised}
        .label=${this.label}
        .unelevated=${this.unelevated}
        .disabled=${this.disabled||this.progress}
        class=${this._result||""}
      >
        <slot name="icon" slot="icon"></slot>
        <slot></slot>
      </ha-button>
      ${e?i.dy`
            <div class="progress">
              ${"success"===this._result?i.dy`<ha-svg-icon .path=${h}></ha-svg-icon>`:"error"===this._result?i.dy`<ha-svg-icon .path=${l}></ha-svg-icon>`:this.progress?i.dy`<ha-spinner size="small"></ha-spinner>`:i.Ld}
            </div>
          `:i.Ld}
    `}actionSuccess(){this._setResult("success")}actionError(){this._setResult("error")}_setResult(e){this._result=e,setTimeout((()=>{this._result=void 0}),2e3)}constructor(...e){super(...e),this.disabled=!1,this.progress=!1,this.raised=!1,this.unelevated=!1}}d.styles=i.iv`
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
  `,(0,a.__decorate)([(0,o.Cb)()],d.prototype,"label",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"progress",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"raised",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"unelevated",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_result",void 0),d=(0,a.__decorate)([(0,o.Mo)("ha-progress-button")],d),t()}catch(l){t(l)}}))},54695:function(e,t,s){s.a(e,(async function(e,a){try{s.r(t),s.d(t,{TTSTryDialog:()=>_});var i=s(73742),o=s(59048),r=s(7616),n=s(32751),l=s(29740),h=s(99298),d=(s(56719),s(75055)),c=s(81665),u=s(35993),p=e([u]);u=(p.then?(await p)():p)[0];const g="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M10,16.5L16,12L10,7.5V16.5Z";class _ extends o.oi{showDialog(e){this._params=e,this._valid=Boolean(this._defaultMessage)}closeDialog(){this._params=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}get _defaultMessage(){const e=this._params.language?.substring(0,2),t=this.hass.locale.language.substring(0,2);return e&&this._messages?.[e]?this._messages[e]:e===t?this.hass.localize("ui.dialogs.tts-try.message_example"):""}render(){return this._params?o.dy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,h.i)(this.hass,this.hass.localize("ui.dialogs.tts-try.header"))}
      >
        <ha-textarea
          autogrow
          id="message"
          .label=${this.hass.localize("ui.dialogs.tts-try.message")}
          .placeholder=${this.hass.localize("ui.dialogs.tts-try.message_placeholder")}
          .value=${this._defaultMessage}
          @input=${this._inputChanged}
          ?dialogInitialFocus=${!this._defaultMessage}
        >
        </ha-textarea>

        <ha-progress-button
          .progress=${this._loadingExample}
          ?dialogInitialFocus=${Boolean(this._defaultMessage)}
          slot="primaryAction"
          .label=${this.hass.localize("ui.dialogs.tts-try.play")}
          @click=${this._playExample}
          .disabled=${!this._valid}
        >
          <ha-svg-icon slot="icon" .path=${g}></ha-svg-icon>
        </ha-progress-button>
      </ha-dialog>
    `:o.Ld}async _inputChanged(){this._valid=Boolean(this._messageInput?.value)}async _playExample(){const e=this._messageInput?.value;if(!e)return;const t=this._params.engine,s=this._params.language,a=this._params.voice;s&&(this._messages={...this._messages,[s.substring(0,2)]:e}),this._loadingExample=!0;const i=new Audio;let o;i.play();try{o=(await(0,d.aT)(this.hass,{platform:t,message:e,language:s,options:{voice:a}})).path}catch(r){return this._loadingExample=!1,void(0,c.Ys)(this,{text:`Unable to load example. ${r.error||r.body||r}`,warning:!0})}i.src=o,i.addEventListener("canplaythrough",(()=>i.play())),i.addEventListener("playing",(()=>{this._loadingExample=!1})),i.addEventListener("error",(()=>{(0,c.Ys)(this,{title:"Error playing audio."}),this._loadingExample=!1}))}constructor(...e){super(...e),this._loadingExample=!1,this._valid=!1}}_.styles=o.iv`
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
  `,(0,i.__decorate)([(0,r.Cb)({attribute:!1})],_.prototype,"hass",void 0),(0,i.__decorate)([(0,r.SB)()],_.prototype,"_loadingExample",void 0),(0,i.__decorate)([(0,r.SB)()],_.prototype,"_params",void 0),(0,i.__decorate)([(0,r.SB)()],_.prototype,"_valid",void 0),(0,i.__decorate)([(0,r.IO)("#message")],_.prototype,"_messageInput",void 0),(0,i.__decorate)([(0,n.t)({key:"ttsTryMessages",state:!1,subscribe:!1})],_.prototype,"_messages",void 0),_=(0,i.__decorate)([(0,r.Mo)("dialog-tts-try")],_),a()}catch(g){a(g)}}))}};
//# sourceMappingURL=9952.18779d82f00b7af1.js.map