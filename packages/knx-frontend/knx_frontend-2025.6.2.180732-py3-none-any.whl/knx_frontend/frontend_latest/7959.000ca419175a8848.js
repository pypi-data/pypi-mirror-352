/*! For license information please see 7959.000ca419175a8848.js.LICENSE.txt */
export const __webpack_ids__=["7959"];export const __webpack_modules__={75972:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{u:()=>n});var a=i(57900),r=i(28105),s=e([a]);a=(s.then?(await s)():s)[0];const n=(e,t)=>{try{return d(t)?.of(e)??e}catch{return e}},d=(0,r.Z)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));o()}catch(n){o(n)}}))},89395:function(e,t,i){i.d(t,{J:()=>a,_:()=>r});const o=/{%|{{/,a=e=>o.test(e),r=e=>{if(!e)return!1;if("string"==typeof e)return a(e);if("object"==typeof e){return(Array.isArray(e)?e:Object.values(e)).some((e=>e&&r(e)))}return!1}},24393:function(e,t,i){i.d(t,{v:()=>o});const o=async(e,t)=>{if(navigator.clipboard)try{return void(await navigator.clipboard.writeText(e))}catch{}const i=t??document.body,o=document.createElement("textarea");o.value=e,i.appendChild(o),o.select(),document.execCommand("copy"),i.removeChild(o)}},69187:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(73742),a=i(59048),r=i(7616),s=i(29740),n=i(41806),d=i(75972),l=i(32518),c=(i(93795),i(29490),e([d]));d=(c.then?(await c)():c)[0];const h="preferred",p="last_used";class u extends a.oi{get _default(){return this.includeLastUsed?p:h}render(){if(!this._pipelines)return a.Ld;const e=this.value??this._default;return a.dy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.pipeline-picker.pipeline")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${n.U}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.includeLastUsed?a.dy`
              <ha-list-item .value=${p}>
                ${this.hass.localize("ui.components.pipeline-picker.last_used")}
              </ha-list-item>
            `:null}
        <ha-list-item .value=${h}>
          ${this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:this._pipelines.find((e=>e.id===this._preferredPipeline))?.name})}
        </ha-list-item>
        ${this._pipelines.map((e=>a.dy`<ha-list-item .value=${e.id}>
              ${e.name}
              (${(0,d.u)(e.language,this.hass.locale)})
            </ha-list-item>`))}
      </ha-select>
    `}firstUpdated(e){super.firstUpdated(e),(0,l.listAssistPipelines)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,s.B)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}u.styles=a.iv`
    ha-select {
      width: 100%;
    }
  `,(0,o.__decorate)([(0,r.Cb)()],u.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)()],u.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],u.prototype,"required",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"includeLastUsed",void 0),(0,o.__decorate)([(0,r.SB)()],u.prototype,"_pipelines",void 0),(0,o.__decorate)([(0,r.SB)()],u.prototype,"_preferredPipeline",void 0),u=(0,o.__decorate)([(0,r.Mo)("ha-assist-pipeline-picker")],u),t()}catch(h){t(h)}}))},58762:function(e,t,i){var o=i(73742),a=i(59048),r=i(7616),s=i(28105),n=i(29740),d=i(41806);const l={key:"Mod-s",run:e=>((0,n.B)(e.dom,"editor-save"),!0)},c=e=>{const t=document.createElement("ha-icon");return t.icon=e.label,t};class h extends a.fl{set value(e){this._value=e}get value(){return this.codemirror?this.codemirror.state.doc.toString():this._value}get hasComments(){if(!this.codemirror||!this._loadedCodeMirror)return!1;const e=this._loadedCodeMirror.highlightingFor(this.codemirror.state,[this._loadedCodeMirror.tags.comment]);return!!this.renderRoot.querySelector(`span.${e}`)}connectedCallback(){super.connectedCallback(),this.hasUpdated&&this.requestUpdate(),this.addEventListener("keydown",d.U),this.codemirror&&!1!==this.autofocus&&this.codemirror.focus()}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",d.U),this.updateComplete.then((()=>{this.codemirror.destroy(),delete this.codemirror}))}async scheduleUpdate(){this._loadedCodeMirror??=await Promise.all([i.e("5192"),i.e("4547")]).then(i.bind(i,13618)),super.scheduleUpdate()}update(e){if(super.update(e),!this.codemirror)return void this._createCodeMirror();const t=[];e.has("mode")&&t.push({effects:[this._loadedCodeMirror.langCompartment.reconfigure(this._mode),this._loadedCodeMirror.foldingCompartment.reconfigure(this._getFoldingExtensions())]}),e.has("readOnly")&&t.push({effects:this._loadedCodeMirror.readonlyCompartment.reconfigure(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly))}),e.has("linewrap")&&t.push({effects:this._loadedCodeMirror.linewrapCompartment.reconfigure(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[])}),e.has("_value")&&this._value!==this.value&&t.push({changes:{from:0,to:this.codemirror.state.doc.length,insert:this._value}}),t.length>0&&this.codemirror.dispatch(...t),e.has("error")&&this.classList.toggle("error-state",this.error)}get _mode(){return this._loadedCodeMirror.langs[this.mode]}_createCodeMirror(){if(!this._loadedCodeMirror)throw new Error("Cannot create editor before CodeMirror is loaded");const e=[this._loadedCodeMirror.lineNumbers(),this._loadedCodeMirror.history(),this._loadedCodeMirror.drawSelection(),this._loadedCodeMirror.EditorState.allowMultipleSelections.of(!0),this._loadedCodeMirror.rectangularSelection(),this._loadedCodeMirror.crosshairCursor(),this._loadedCodeMirror.highlightSelectionMatches(),this._loadedCodeMirror.highlightActiveLine(),this._loadedCodeMirror.indentationMarkers({thickness:0,activeThickness:1,colors:{activeLight:"var(--secondary-text-color)",activeDark:"var(--secondary-text-color)"}}),this._loadedCodeMirror.keymap.of([...this._loadedCodeMirror.defaultKeymap,...this._loadedCodeMirror.searchKeymap,...this._loadedCodeMirror.historyKeymap,...this._loadedCodeMirror.tabKeyBindings,l]),this._loadedCodeMirror.langCompartment.of(this._mode),this._loadedCodeMirror.haTheme,this._loadedCodeMirror.haSyntaxHighlighting,this._loadedCodeMirror.readonlyCompartment.of(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly)),this._loadedCodeMirror.linewrapCompartment.of(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[]),this._loadedCodeMirror.EditorView.updateListener.of(this._onUpdate),this._loadedCodeMirror.foldingCompartment.of(this._getFoldingExtensions())];if(!this.readOnly){const t=[];this.autocompleteEntities&&this.hass&&t.push(this._entityCompletions.bind(this)),this.autocompleteIcons&&t.push(this._mdiCompletions.bind(this)),t.length>0&&e.push(this._loadedCodeMirror.autocompletion({override:t,maxRenderedOptions:10}))}this.codemirror=new this._loadedCodeMirror.EditorView({state:this._loadedCodeMirror.EditorState.create({doc:this._value,extensions:e}),parent:this.renderRoot})}_entityCompletions(e){const t=e.matchBefore(/[a-z_]{3,}\.\w*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=this._getStates(this.hass.states);return i&&i.length?{from:Number(t.from),options:i,validFor:/^[a-z_]{3,}\.\w*$/}:null}async _mdiCompletions(e){const t=e.matchBefore(/mdi:\S*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=await this._getIconItems();return{from:Number(t.from),options:i,validFor:/^mdi:\S*$/}}constructor(...e){super(...e),this.mode="yaml",this.autofocus=!1,this.readOnly=!1,this.linewrap=!1,this.autocompleteEntities=!1,this.autocompleteIcons=!1,this.error=!1,this._value="",this._getStates=(0,s.Z)((e=>{if(!e)return[];return Object.keys(e).map((t=>({type:"variable",label:t,detail:e[t].attributes.friendly_name,info:`State: ${e[t].state}`})))})),this._getIconItems=async()=>{if(!this._iconList){let e;e=(await i.e("4813").then(i.t.bind(i,81405,19))).default,this._iconList=e.map((e=>({type:"variable",label:`mdi:${e.name}`,detail:e.keywords.join(", "),info:c})))}return this._iconList},this._onUpdate=e=>{e.docChanged&&(this._value=e.state.doc.toString(),(0,n.B)(this,"value-changed",{value:this._value}))},this._getFoldingExtensions=()=>"yaml"===this.mode?[this._loadedCodeMirror.foldGutter(),this._loadedCodeMirror.foldingOnIndent]:[]}}h.styles=a.iv`
    :host(.error-state) .cm-gutters {
      border-color: var(--error-state-color, red);
    }
  `,(0,o.__decorate)([(0,r.Cb)()],h.prototype,"mode",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],h.prototype,"autofocus",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"read-only",type:Boolean})],h.prototype,"readOnly",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],h.prototype,"linewrap",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,attribute:"autocomplete-entities"})],h.prototype,"autocompleteEntities",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,attribute:"autocomplete-icons"})],h.prototype,"autocompleteIcons",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],h.prototype,"error",void 0),(0,o.__decorate)([(0,r.SB)()],h.prototype,"_value",void 0),h=(0,o.__decorate)([(0,r.Mo)("ha-code-editor")],h)},57027:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(73742),a=i(59048),r=i(7616),s=(i(40830),i(27341)),n=e([s]);s=(n.then?(await n)():n)[0];const d="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";class l extends a.oi{render(){return a.dy`
      <ha-tooltip .placement=${this.position} .content=${this.label}>
        <ha-svg-icon .path=${d}></ha-svg-icon>
      </ha-tooltip>
    `}constructor(...e){super(...e),this.position="top"}}l.styles=a.iv`
    ha-svg-icon {
      --mdc-icon-size: var(--ha-help-tooltip-size, 14px);
      color: var(--ha-help-tooltip-color, var(--disabled-text-color));
    }
  `,(0,o.__decorate)([(0,r.Cb)()],l.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)()],l.prototype,"position",void 0),l=(0,o.__decorate)([(0,r.Mo)("ha-help-tooltip")],l),t()}catch(d){t(d)}}))},91391:function(e,t,i){var o=i(73742),a=i(59048),r=i(7616),s=i(29740);const n=e=>e.replace(/^_*(.)|_+(.)/g,((e,t,i)=>t?t.toUpperCase():" "+i.toUpperCase()));i(90256),i(57264);const d=[],l=e=>a.dy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    <span slot="headline">${e.title||e.path}</span>
    ${e.title?a.dy`<span slot="supporting-text">${e.path}</span>`:a.Ld}
  </ha-combo-box-item>
`,c=(e,t,i)=>({path:`/${e}/${t.path??i}`,icon:t.icon??"mdi:view-compact",title:t.title??(t.path?n(t.path):`${i}`)}),h=(e,t)=>({path:`/${t.url_path}`,icon:t.icon??"mdi:view-dashboard",title:t.url_path===e.defaultPanel?e.localize("panel.states"):e.localize(`panel.${t.title}`)||t.title||(t.url_path?n(t.url_path):"")});class p extends a.oi{render(){return a.dy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="path"
        item-label-path="path"
        .value=${this._value}
        allow-custom-value
        .filteredItems=${this.navigationItems}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .renderer=${l}
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
        @filter-changed=${this._filterChanged}
      >
      </ha-combo-box>
    `}async _openedChanged(e){this._opened=e.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems()}async _loadNavigationItems(){this.navigationItemsLoaded=!0;const e=Object.entries(this.hass.panels).map((([e,t])=>({id:e,...t}))),t=e.filter((e=>"lovelace"===e.component_name)),i=await Promise.all(t.map((e=>{return(t=this.hass.connection,i="lovelace"===e.url_path?null:e.url_path,o=!0,t.sendMessagePromise({type:"lovelace/config",url_path:i,force:o})).then((t=>[e.id,t])).catch((t=>[e.id,void 0]));var t,i,o}))),o=new Map(i);this.navigationItems=[];for(const a of e){this.navigationItems.push(h(this.hass,a));const e=o.get(a.id);e&&"views"in e&&e.views.forEach(((e,t)=>this.navigationItems.push(c(a.url_path,e,t))))}this.comboBox.filteredItems=this.navigationItems}shouldUpdate(e){return!this._opened||e.has("_opened")}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,s.B)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}_filterChanged(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[];this.navigationItems.forEach((i=>{(i.path.toLowerCase().includes(t)||i.title.toLowerCase().includes(t))&&e.push(i)})),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._opened=!1,this.navigationItemsLoaded=!1,this.navigationItems=d}}p.styles=a.iv`
    ha-icon,
    ha-svg-icon {
      color: var(--primary-text-color);
      position: relative;
      bottom: 0px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `,(0,o.__decorate)([(0,r.Cb)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)()],p.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)()],p.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)()],p.prototype,"helper",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],p.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],p.prototype,"required",void 0),(0,o.__decorate)([(0,r.SB)()],p.prototype,"_opened",void 0),(0,o.__decorate)([(0,r.IO)("ha-combo-box",!0)],p.prototype,"comboBox",void 0),p=(0,o.__decorate)([(0,r.Mo)("ha-navigation-picker")],p)},53179:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaSelectorUiAction:()=>c});var a=i(73742),r=i(59048),s=i(7616),n=i(29740),d=i(18234),l=e([d]);d=(l.then?(await l)():l)[0];class c extends r.oi{render(){return r.dy`
      <hui-action-editor
        .label=${this.label}
        .hass=${this.hass}
        .config=${this.value}
        .actions=${this.selector.ui_action?.actions}
        .defaultAction=${this.selector.ui_action?.default_action}
        .tooltipText=${this.helper}
        @value-changed=${this._valueChanged}
      ></hui-action-editor>
    `}_valueChanged(e){(0,n.B)(this,"value-changed",{value:e.detail.value})}}(0,a.__decorate)([(0,s.Cb)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],c.prototype,"selector",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],c.prototype,"value",void 0),(0,a.__decorate)([(0,s.Cb)()],c.prototype,"label",void 0),(0,a.__decorate)([(0,s.Cb)()],c.prototype,"helper",void 0),c=(0,a.__decorate)([(0,s.Mo)("ha-selector-ui_action")],c),o()}catch(c){o(c)}}))},36344:function(e,t,i){var o=i(73742),a=i(24110),r=i(59048),s=i(7616),n=i(29740),d=i(77204),l=(i(58762),i(15606)),c=i(24393);i(30337);class h extends r.oi{setValue(e){try{this._yaml=(e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0})(e)?"":(0,a.$w)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?r.Ld:r.dy`
      ${this.label?r.dy`<p>${this.label}${this.required?" *":""}</p>`:r.Ld}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        dir="ltr"
      ></ha-code-editor>
      ${this.copyClipboard||this.hasExtraActions?r.dy`
            <div class="card-actions">
              ${this.copyClipboard?r.dy`
                    <ha-button @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:r.Ld}
              <slot name="extra-actions"></slot>
            </div>
          `:r.Ld}
    `}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,o=!0;if(this._yaml)try{t=(0,a.zD)(this._yaml,{schema:this.yamlSchema})}catch(r){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:r.reason})}${r.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:r.mark.line+1,column:r.mark.column+1})})`:""}`}else t={};this.value=t,this.isValid=o,(0,n.B)(this,"value-changed",{value:t,isValid:o,errorMsg:i})}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,c.v)(this.yaml),(0,l.C)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[d.Qx,r.iv`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            0px 0px var(--ha-card-border-radius, 12px)
              var(--ha-card-border-radius, 12px)
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
        }
      `]}constructor(...e){super(...e),this.yamlSchema=a.oW,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this._yaml=""}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],h.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"is-valid",type:Boolean})],h.prototype,"isValid",void 0),(0,o.__decorate)([(0,s.Cb)()],h.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"auto-update",type:Boolean})],h.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"read-only",type:Boolean})],h.prototype,"readOnly",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],h.prototype,"required",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"copy-clipboard",type:Boolean})],h.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"has-extra-actions",type:Boolean})],h.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,s.SB)()],h.prototype,"_yaml",void 0),(0,o.__decorate)([(0,s.IO)("ha-code-editor")],h.prototype,"_codeEditor",void 0),h=(0,o.__decorate)([(0,s.Mo)("ha-yaml-editor")],h)},32518:function(e,t,i){i.d(t,{PA:()=>s,Xp:()=>a,af:()=>d,eP:()=>o,fetchAssistPipelineLanguages:()=>l,jZ:()=>n,listAssistPipelines:()=>r});const o=(e,t,i)=>"run-start"===t.type?e={init_options:i,stage:"ready",run:t.data,events:[t]}:e?((e="wake_word-start"===t.type?{...e,stage:"wake_word",wake_word:{...t.data,done:!1}}:"wake_word-end"===t.type?{...e,wake_word:{...e.wake_word,...t.data,done:!0}}:"stt-start"===t.type?{...e,stage:"stt",stt:{...t.data,done:!1}}:"stt-end"===t.type?{...e,stt:{...e.stt,...t.data,done:!0}}:"intent-start"===t.type?{...e,stage:"intent",intent:{...t.data,done:!1}}:"intent-end"===t.type?{...e,intent:{...e.intent,...t.data,done:!0}}:"tts-start"===t.type?{...e,stage:"tts",tts:{...t.data,done:!1}}:"tts-end"===t.type?{...e,tts:{...e.tts,...t.data,done:!0}}:"run-end"===t.type?{...e,stage:"done"}:"error"===t.type?{...e,stage:"error",error:t.data}:{...e}).events=[...e.events,t],e):void console.warn("Received unexpected event before receiving session",t),a=(e,t,i)=>e.connection.subscribeMessage(t,{...i,type:"assist_pipeline/run"}),r=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),s=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),n=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/create",...t}),d=(e,t,i)=>e.callWS({type:"assist_pipeline/pipeline/update",pipeline_id:t,...i}),l=e=>e.callWS({type:"assist_pipeline/language/list"})},47469:function(e,t,i){i.d(t,{F3:()=>a,Lh:()=>o,t4:()=>r});const o=(e,t,i)=>e(`component.${t}.title`)||i?.name||t,a=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},r=(e,t)=>e.callWS({type:"manifest/get",integration:t})},18234:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(73742),a=i(59048),r=i(7616),s=i(28105),n=i(29740),d=i(41806),l=i(69187),c=i(57027),h=(i(93795),i(91391),i(45618)),p=e([l,c,h]);[l,c,h]=p.then?(await p)():p;const u=["more-info","toggle","navigate","url","perform-action","assist","none"],_=[{name:"navigation_path",selector:{navigation:{}}}],v=[{type:"grid",name:"",schema:[{name:"pipeline_id",selector:{assist_pipeline:{include_last_used:!0}}},{name:"start_listening",selector:{boolean:{}}}]}];class m extends a.oi{get _navigation_path(){const e=this.config;return e?.navigation_path||""}get _url_path(){const e=this.config;return e?.url_path||""}get _service(){const e=this.config;return e?.perform_action||e?.service||""}updated(e){super.updated(e),e.has("defaultAction")&&e.get("defaultAction")!==this.defaultAction&&this._select.layoutOptions()}render(){if(!this.hass)return a.Ld;const e=this.actions??u;let t=this.config?.action||"default";return"call-service"===t&&(t="perform-action"),a.dy`
      <div class="dropdown">
        <ha-select
          .label=${this.label}
          .configValue=${"action"}
          @selected=${this._actionPicked}
          .value=${t}
          @closed=${d.U}
          fixedMenuPosition
          naturalMenuWidt
        >
          <ha-list-item value="default">
            ${this.hass.localize("ui.panel.lovelace.editor.action-editor.actions.default_action")}
            ${this.defaultAction?` (${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${this.defaultAction}`).toLowerCase()})`:a.Ld}
          </ha-list-item>
          ${e.map((e=>a.dy`
              <ha-list-item .value=${e}>
                ${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${e}`)}
              </ha-list-item>
            `))}
        </ha-select>
        ${this.tooltipText?a.dy`
              <ha-help-tooltip .label=${this.tooltipText}></ha-help-tooltip>
            `:a.Ld}
      </div>
      ${"navigate"===this.config?.action?a.dy`
            <ha-form
              .hass=${this.hass}
              .schema=${_}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:a.Ld}
      ${"url"===this.config?.action?a.dy`
            <ha-textfield
              .label=${this.hass.localize("ui.panel.lovelace.editor.action-editor.url_path")}
              .value=${this._url_path}
              .configValue=${"url_path"}
              @input=${this._valueChanged}
            ></ha-textfield>
          `:a.Ld}
      ${"call-service"===this.config?.action||"perform-action"===this.config?.action?a.dy`
            <ha-service-control
              .hass=${this.hass}
              .value=${this._serviceAction(this.config)}
              .showAdvanced=${this.hass.userData?.showAdvanced}
              narrow
              @value-changed=${this._serviceValueChanged}
            ></ha-service-control>
          `:a.Ld}
      ${"assist"===this.config?.action?a.dy`
            <ha-form
              .hass=${this.hass}
              .schema=${v}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:a.Ld}
    `}_actionPicked(e){if(e.stopPropagation(),!this.hass)return;let t=this.config?.action;"call-service"===t&&(t="perform-action");const i=e.target.value;if(t===i)return;if("default"===i)return void(0,n.B)(this,"value-changed",{value:void 0});let o;switch(i){case"url":o={url_path:this._url_path};break;case"perform-action":o={perform_action:this._service};break;case"navigate":o={navigation_path:this._navigation_path}}(0,n.B)(this,"value-changed",{value:{action:i,...o}})}_valueChanged(e){if(e.stopPropagation(),!this.hass)return;const t=e.target,i=e.target.value??e.target.checked;this[`_${t.configValue}`]!==i&&t.configValue&&(0,n.B)(this,"value-changed",{value:{...this.config,[t.configValue]:i}})}_formValueChanged(e){e.stopPropagation();const t=e.detail.value;(0,n.B)(this,"value-changed",{value:t})}_computeFormLabel(e){return this.hass?.localize(`ui.panel.lovelace.editor.action-editor.${e.name}`)}_serviceValueChanged(e){e.stopPropagation();const t={...this.config,action:"perform-action",perform_action:e.detail.value.action||"",data:e.detail.value.data,target:e.detail.value.target||{}};e.detail.value.data||delete t.data,"service_data"in t&&delete t.service_data,"service"in t&&delete t.service,(0,n.B)(this,"value-changed",{value:t})}constructor(...e){super(...e),this._serviceAction=(0,s.Z)((e=>({action:this._service,...e.data||e.service_data?{data:e.data??e.service_data}:null,target:e.target})))}}m.styles=a.iv`
    .dropdown {
      position: relative;
    }
    ha-help-tooltip {
      position: absolute;
      right: 40px;
      top: 16px;
      inset-inline-start: initial;
      inset-inline-end: 40px;
      direction: var(--direction);
    }
    ha-select,
    ha-textfield {
      width: 100%;
    }
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      display: block;
    }
    ha-textfield,
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      margin-top: 8px;
    }
    ha-service-control {
      --service-control-padding: 0;
    }
  `,(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"config",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"actions",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"defaultAction",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"tooltipText",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"hass",void 0),(0,o.__decorate)([(0,r.IO)("ha-select")],m.prototype,"_select",void 0),m=(0,o.__decorate)([(0,r.Mo)("hui-action-editor")],m),t()}catch(u){t(u)}}))},15606:function(e,t,i){i.d(t,{C:()=>a});var o=i(29740);const a=(e,t)=>(0,o.B)(e,"hass-notification",t)},12790:function(e,t,i){i.d(t,{C:()=>p});var o=i(35340),a=i(5277),r=i(93847);class s{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class n{get(){return this.Y}pause(){this.Y??=new Promise((e=>this.Z=e))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var d=i(83522);const l=e=>!(0,a.pt)(e)&&"function"==typeof e.then,c=1073741823;class h extends r.sR{render(...e){return e.find((e=>!l(e)))??o.Jb}update(e,t){const i=this._$Cbt;let a=i.length;this._$Cbt=t;const r=this._$CK,s=this._$CX;this.isConnected||this.disconnected();for(let o=0;o<t.length&&!(o>this._$Cwt);o++){const e=t[o];if(!l(e))return this._$Cwt=o,e;o<a&&e===i[o]||(this._$Cwt=c,a=0,Promise.resolve(e).then((async t=>{for(;s.get();)await s.get();const i=r.deref();if(void 0!==i){const o=i._$Cbt.indexOf(e);o>-1&&o<i._$Cwt&&(i._$Cwt=o,i.setValue(t))}})))}return o.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new s(this),this._$CX=new n}}const p=(0,d.XM)(h)}};
//# sourceMappingURL=7959.000ca419175a8848.js.map