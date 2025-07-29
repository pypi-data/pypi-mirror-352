export const __webpack_ids__=["601"];export const __webpack_modules__={91337:function(e,t,a){var o=a(73742),r=a(59048),i=a(7616),s=a(69342),l=a(29740);a(22543),a(32986);const n={boolean:()=>a.e("4852").then(a.bind(a,60751)),constant:()=>a.e("177").then(a.bind(a,85184)),float:()=>a.e("2369").then(a.bind(a,94980)),grid:()=>a.e("9219").then(a.bind(a,79998)),expandable:()=>a.e("4020").then(a.bind(a,71781)),integer:()=>a.e("3703").then(a.bind(a,12960)),multi_select:()=>Promise.all([a.e("4458"),a.e("514")]).then(a.bind(a,79298)),positive_time_period_dict:()=>a.e("2010").then(a.bind(a,49058)),select:()=>a.e("3162").then(a.bind(a,64324)),string:()=>a.e("2529").then(a.bind(a,72609)),optional_actions:()=>a.e("1601").then(a.bind(a,67552))},d=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class h extends r.oi{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof r.fl&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||n[e.type]?.()}))}render(){return r.dy`
      <div class="root" part="root">
        ${this.error&&this.error.base?r.dy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),a=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return r.dy`
            ${t?r.dy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:a?r.dy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(a,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?r.dy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${d(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?"":e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,s.h)(this.fieldElementName(e.type),{schema:e,data:d(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[a,o]of Object.entries(e.context))t[a]=this.data[o];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const a=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...a},(0,l.B)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?r.dy`<ul>
        ${e.map((e=>r.dy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}h.styles=r.iv`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,i.Cb)({type:Boolean})],h.prototype,"narrow",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"data",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"schema",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"error",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"warning",void 0),(0,o.__decorate)([(0,i.Cb)({type:Boolean})],h.prototype,"disabled",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"computeError",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"computeWarning",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"localizeValue",void 0),h=(0,o.__decorate)([(0,i.Mo)("ha-form")],h)},74069:function(e,t,a){a.r(t);var o=a(73742),r=a(59048),i=a(28105),s=a(7616),l=a(29740),n=a(99298),d=(a(91337),a(30337),a(77204));class h extends r.oi{showDialog(e){this._params=e,this._error=void 0,this._data=e.block,this._expand=!!e.block?.data}closeDialog(){this._params=void 0,this._data=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}render(){return this._params&&this._data?r.dy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,n.i)(this.hass,this.hass.localize("ui.dialogs.helper_settings.schedule.edit_schedule_block"))}
      >
        <div>
          <ha-form
            .hass=${this.hass}
            .schema=${this._schema(this._expand)}
            .data=${this._data}
            .error=${this._error}
            .computeLabel=${this._computeLabelCallback}
            @value-changed=${this._valueChanged}
          ></ha-form>
        </div>
        <ha-button
          slot="secondaryAction"
          class="warning"
          @click=${this._deleteBlock}
        >
          ${this.hass.localize("ui.common.delete")}
        </ha-button>
        <ha-button slot="primaryAction" @click=${this._updateBlock}>
          ${this.hass.localize("ui.common.save")}
        </ha-button>
      </ha-dialog>
    `:r.Ld}_valueChanged(e){this._error=void 0,this._data=e.detail.value}_updateBlock(){try{this._params.updateBlock(this._data),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}_deleteBlock(){try{this._params.deleteBlock(),this.closeDialog()}catch(e){this._error={base:e?e.message:"Unknown error"}}}static get styles(){return[d.yu]}constructor(...e){super(...e),this._expand=!1,this._schema=(0,i.Z)((e=>[{name:"from",required:!0,selector:{time:{no_second:!0}}},{name:"to",required:!0,selector:{time:{no_second:!0}}},{name:"advanced_settings",type:"expandable",flatten:!0,expanded:e,schema:[{name:"data",required:!1,selector:{object:{}}}]}])),this._computeLabelCallback=e=>{switch(e.name){case"from":return this.hass.localize("ui.dialogs.helper_settings.schedule.start");case"to":return this.hass.localize("ui.dialogs.helper_settings.schedule.end");case"data":return this.hass.localize("ui.dialogs.helper_settings.schedule.data");case"advanced_settings":return this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings")}return""}}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_error",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_data",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_params",void 0),customElements.define("dialog-schedule-block-info",h)}};
//# sourceMappingURL=601.b9d0638c4299301e.js.map