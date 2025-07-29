/*! For license information please see 4940.ea4fc74cbfb329b8.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4940"],{75972:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{u:()=>n});var a=i(57900),s=i(28105),r=e([a]);a=(r.then?(await r)():r)[0];const n=(e,t)=>{try{var i,o;return null!==(i=null===(o=d(t))||void 0===o?void 0:o.of(e))&&void 0!==i?i:e}catch(a){return e}},d=(0,s.Z)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));o()}catch(n){o(n)}}))},89395:function(e,t,i){i.d(t,{J:()=>a,_:()=>s});i(81738),i(72489),i(64455),i(32192);const o=/{%|{{/,a=e=>o.test(e),s=e=>{if(!e)return!1;if("string"==typeof e)return a(e);if("object"==typeof e){return(Array.isArray(e)?e:Object.values(e)).some((e=>e&&s(e)))}return!1}},1893:function(e,t,i){i.d(t,{Q:()=>o});i(64455),i(6202);const o=e=>e.replace(/^_*(.)|_+(.)/g,((e,t,i)=>t?t.toUpperCase():" "+i.toUpperCase()))},24393:function(e,t,i){i.d(t,{v:()=>o});i(1455);const o=async(e,t)=>{if(navigator.clipboard)try{return void(await navigator.clipboard.writeText(e))}catch(a){}const i=null!=t?t:document.body,o=document.createElement("textarea");o.value=e,i.appendChild(o),o.select(),document.execCommand("copy"),i.removeChild(o)}},69187:function(e,t,i){i.a(e,(async function(e,t){try{i(26847),i(81738),i(29981),i(6989),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=i(29740),n=i(41806),d=i(75972),l=i(32518),c=(i(93795),i(29490),e([d]));d=(c.then?(await c)():c)[0];let h,p,u,v,_=e=>e;const g="preferred",m="last_used";class b extends a.oi{get _default(){return this.includeLastUsed?m:g}render(){var e,t;if(!this._pipelines)return a.Ld;const i=null!==(e=this.value)&&void 0!==e?e:this._default;return(0,a.dy)(h||(h=_`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        <ha-list-item .value=${0}>
          ${0}
        </ha-list-item>
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.pipeline-picker.pipeline"),i,this.required,this.disabled,this._changed,n.U,this.includeLastUsed?(0,a.dy)(p||(p=_`
              <ha-list-item .value=${0}>
                ${0}
              </ha-list-item>
            `),m,this.hass.localize("ui.components.pipeline-picker.last_used")):null,g,this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:null===(t=this._pipelines.find((e=>e.id===this._preferredPipeline)))||void 0===t?void 0:t.name}),this._pipelines.map((e=>(0,a.dy)(u||(u=_`<ha-list-item .value=${0}>
              ${0}
              (${0})
            </ha-list-item>`),e.id,e.name,(0,d.u)(e.language,this.hass.locale)))))}firstUpdated(e){super.firstUpdated(e),(0,l.listAssistPipelines)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,r.B)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}b.styles=(0,a.iv)(v||(v=_`
    ha-select {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,s.Cb)()],b.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)()],b.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],b.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,reflect:!0})],b.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],b.prototype,"required",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],b.prototype,"includeLastUsed",void 0),(0,o.__decorate)([(0,s.SB)()],b.prototype,"_pipelines",void 0),(0,o.__decorate)([(0,s.SB)()],b.prototype,"_preferredPipeline",void 0),b=(0,o.__decorate)([(0,s.Mo)("ha-assist-pipeline-picker")],b),t()}catch(h){t(h)}}))},58762:function(e,t,i){i(40777),i(26847),i(2394),i(81738),i(6989),i(1455),i(56303),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=i(28105),n=i(29740),d=i(41806);let l;const c={key:"Mod-s",run:e=>((0,n.B)(e.dom,"editor-save"),!0)},h=e=>{const t=document.createElement("ha-icon");return t.icon=e.label,t};class p extends a.fl{set value(e){this._value=e}get value(){return this.codemirror?this.codemirror.state.doc.toString():this._value}get hasComments(){if(!this.codemirror||!this._loadedCodeMirror)return!1;const e=this._loadedCodeMirror.highlightingFor(this.codemirror.state,[this._loadedCodeMirror.tags.comment]);return!!this.renderRoot.querySelector(`span.${e}`)}connectedCallback(){super.connectedCallback(),this.hasUpdated&&this.requestUpdate(),this.addEventListener("keydown",d.U),this.codemirror&&!1!==this.autofocus&&this.codemirror.focus()}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",d.U),this.updateComplete.then((()=>{this.codemirror.destroy(),delete this.codemirror}))}async scheduleUpdate(){var e;null!==(e=this._loadedCodeMirror)&&void 0!==e||(this._loadedCodeMirror=await Promise.all([i.e("6849"),i.e("4547")]).then(i.bind(i,13618))),super.scheduleUpdate()}update(e){if(super.update(e),!this.codemirror)return void this._createCodeMirror();const t=[];e.has("mode")&&t.push({effects:[this._loadedCodeMirror.langCompartment.reconfigure(this._mode),this._loadedCodeMirror.foldingCompartment.reconfigure(this._getFoldingExtensions())]}),e.has("readOnly")&&t.push({effects:this._loadedCodeMirror.readonlyCompartment.reconfigure(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly))}),e.has("linewrap")&&t.push({effects:this._loadedCodeMirror.linewrapCompartment.reconfigure(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[])}),e.has("_value")&&this._value!==this.value&&t.push({changes:{from:0,to:this.codemirror.state.doc.length,insert:this._value}}),t.length>0&&this.codemirror.dispatch(...t),e.has("error")&&this.classList.toggle("error-state",this.error)}get _mode(){return this._loadedCodeMirror.langs[this.mode]}_createCodeMirror(){if(!this._loadedCodeMirror)throw new Error("Cannot create editor before CodeMirror is loaded");const e=[this._loadedCodeMirror.lineNumbers(),this._loadedCodeMirror.history(),this._loadedCodeMirror.drawSelection(),this._loadedCodeMirror.EditorState.allowMultipleSelections.of(!0),this._loadedCodeMirror.rectangularSelection(),this._loadedCodeMirror.crosshairCursor(),this._loadedCodeMirror.highlightSelectionMatches(),this._loadedCodeMirror.highlightActiveLine(),this._loadedCodeMirror.indentationMarkers({thickness:0,activeThickness:1,colors:{activeLight:"var(--secondary-text-color)",activeDark:"var(--secondary-text-color)"}}),this._loadedCodeMirror.keymap.of([...this._loadedCodeMirror.defaultKeymap,...this._loadedCodeMirror.searchKeymap,...this._loadedCodeMirror.historyKeymap,...this._loadedCodeMirror.tabKeyBindings,c]),this._loadedCodeMirror.langCompartment.of(this._mode),this._loadedCodeMirror.haTheme,this._loadedCodeMirror.haSyntaxHighlighting,this._loadedCodeMirror.readonlyCompartment.of(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly)),this._loadedCodeMirror.linewrapCompartment.of(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[]),this._loadedCodeMirror.EditorView.updateListener.of(this._onUpdate),this._loadedCodeMirror.foldingCompartment.of(this._getFoldingExtensions())];if(!this.readOnly){const t=[];this.autocompleteEntities&&this.hass&&t.push(this._entityCompletions.bind(this)),this.autocompleteIcons&&t.push(this._mdiCompletions.bind(this)),t.length>0&&e.push(this._loadedCodeMirror.autocompletion({override:t,maxRenderedOptions:10}))}this.codemirror=new this._loadedCodeMirror.EditorView({state:this._loadedCodeMirror.EditorState.create({doc:this._value,extensions:e}),parent:this.renderRoot})}_entityCompletions(e){const t=e.matchBefore(/[a-z_]{3,}\.\w*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=this._getStates(this.hass.states);return i&&i.length?{from:Number(t.from),options:i,validFor:/^[a-z_]{3,}\.\w*$/}:null}async _mdiCompletions(e){const t=e.matchBefore(/mdi:\S*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=await this._getIconItems();return{from:Number(t.from),options:i,validFor:/^mdi:\S*$/}}constructor(...e){super(...e),this.mode="yaml",this.autofocus=!1,this.readOnly=!1,this.linewrap=!1,this.autocompleteEntities=!1,this.autocompleteIcons=!1,this.error=!1,this._value="",this._getStates=(0,r.Z)((e=>{if(!e)return[];return Object.keys(e).map((t=>({type:"variable",label:t,detail:e[t].attributes.friendly_name,info:`State: ${e[t].state}`})))})),this._getIconItems=async()=>{if(!this._iconList){let e;e=(await i.e("4813").then(i.t.bind(i,81405,19))).default,this._iconList=e.map((e=>({type:"variable",label:`mdi:${e.name}`,detail:e.keywords.join(", "),info:h})))}return this._iconList},this._onUpdate=e=>{e.docChanged&&(this._value=e.state.doc.toString(),(0,n.B)(this,"value-changed",{value:this._value}))},this._getFoldingExtensions=()=>"yaml"===this.mode?[this._loadedCodeMirror.foldGutter(),this._loadedCodeMirror.foldingOnIndent]:[]}}p.styles=(0,a.iv)(l||(l=(e=>e)`
    :host(.error-state) .cm-gutters {
      border-color: var(--error-state-color, red);
    }
  `)),(0,o.__decorate)([(0,s.Cb)()],p.prototype,"mode",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"autofocus",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:"read-only",type:Boolean})],p.prototype,"readOnly",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"linewrap",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,attribute:"autocomplete-entities"})],p.prototype,"autocompleteEntities",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,attribute:"autocomplete-icons"})],p.prototype,"autocompleteIcons",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"error",void 0),(0,o.__decorate)([(0,s.SB)()],p.prototype,"_value",void 0),p=(0,o.__decorate)([(0,s.Mo)("ha-code-editor")],p)},57027:function(e,t,i){i.a(e,(async function(e,t){try{i(26847),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=(i(40830),i(27341)),n=e([r]);r=(n.then?(await n)():n)[0];let d,l,c=e=>e;const h="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";class p extends a.oi{render(){return(0,a.dy)(d||(d=c`
      <ha-tooltip .placement=${0} .content=${0}>
        <ha-svg-icon .path=${0}></ha-svg-icon>
      </ha-tooltip>
    `),this.position,this.label,h)}constructor(...e){super(...e),this.position="top"}}p.styles=(0,a.iv)(l||(l=c`
    ha-svg-icon {
      --mdc-icon-size: var(--ha-help-tooltip-size, 14px);
      color: var(--ha-help-tooltip-color, var(--disabled-text-color));
    }
  `)),(0,o.__decorate)([(0,s.Cb)()],p.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)()],p.prototype,"position",void 0),p=(0,o.__decorate)([(0,s.Mo)("ha-help-tooltip")],p),t()}catch(d){t(d)}}))},20797:function(e,t,i){i.a(e,(async function(e,t){try{i(39710),i(26847),i(2394),i(81738),i(94814),i(22960),i(6989),i(87799),i(1455),i(56389),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=i(29740),n=i(1893),d=i(8265),l=i(54693),c=(i(57264),e([l]));l=(c.then?(await c)():c)[0];let h,p,u,v,_=e=>e;const g=[],m=e=>(0,a.dy)(h||(h=_`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    <span slot="headline">${0}</span>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.title||e.path,e.title?(0,a.dy)(p||(p=_`<span slot="supporting-text">${0}</span>`),e.path):a.Ld),b=(e,t,i)=>{var o,a,s;return{path:`/${e}/${null!==(o=t.path)&&void 0!==o?o:i}`,icon:null!==(a=t.icon)&&void 0!==a?a:"mdi:view-compact",title:null!==(s=t.title)&&void 0!==s?s:t.path?(0,n.Q)(t.path):`${i}`}},y=(e,t)=>{var i;return{path:`/${t.url_path}`,icon:null!==(i=t.icon)&&void 0!==i?i:"mdi:view-dashboard",title:t.url_path===e.defaultPanel?e.localize("panel.states"):e.localize(`panel.${t.title}`)||t.title||(t.url_path?(0,n.Q)(t.url_path):"")}};class f extends a.oi{render(){return(0,a.dy)(u||(u=_`
      <ha-combo-box
        .hass=${0}
        item-value-path="path"
        item-label-path="path"
        .value=${0}
        allow-custom-value
        .filteredItems=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .renderer=${0}
        @opened-changed=${0}
        @value-changed=${0}
        @filter-changed=${0}
      >
      </ha-combo-box>
    `),this.hass,this._value,this.navigationItems,this.label,this.helper,this.disabled,this.required,m,this._openedChanged,this._valueChanged,this._filterChanged)}async _openedChanged(e){this._opened=e.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems()}async _loadNavigationItems(){this.navigationItemsLoaded=!0;const e=Object.entries(this.hass.panels).map((([e,t])=>Object.assign({id:e},t))),t=e.filter((e=>"lovelace"===e.component_name)),i=await Promise.all(t.map((e=>(0,d.Q2)(this.hass.connection,"lovelace"===e.url_path?null:e.url_path,!0).then((t=>[e.id,t])).catch((t=>[e.id,void 0]))))),o=new Map(i);this.navigationItems=[];for(const a of e){this.navigationItems.push(y(this.hass,a));const e=o.get(a.id);e&&"views"in e&&e.views.forEach(((e,t)=>this.navigationItems.push(b(a.url_path,e,t))))}this.comboBox.filteredItems=this.navigationItems}shouldUpdate(e){return!this._opened||e.has("_opened")}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,r.B)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}_filterChanged(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[];this.navigationItems.forEach((i=>{(i.path.toLowerCase().includes(t)||i.title.toLowerCase().includes(t))&&e.push(i)})),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._opened=!1,this.navigationItemsLoaded=!1,this.navigationItems=g}}f.styles=(0,a.iv)(v||(v=_`
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
  `)),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)()],f.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)()],f.prototype,"value",void 0),(0,o.__decorate)([(0,s.Cb)()],f.prototype,"helper",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],f.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],f.prototype,"required",void 0),(0,o.__decorate)([(0,s.SB)()],f.prototype,"_opened",void 0),(0,o.__decorate)([(0,s.IO)("ha-combo-box",!0)],f.prototype,"comboBox",void 0),f=(0,o.__decorate)([(0,s.Mo)("ha-navigation-picker")],f),t()}catch(h){t(h)}}))},53179:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaSelectorUiAction:()=>p});var a=i(73742),s=i(59048),r=i(7616),n=i(29740),d=i(18234),l=e([d]);d=(l.then?(await l)():l)[0];let c,h=e=>e;class p extends s.oi{render(){var e,t;return(0,s.dy)(c||(c=h`
      <hui-action-editor
        .label=${0}
        .hass=${0}
        .config=${0}
        .actions=${0}
        .defaultAction=${0}
        .tooltipText=${0}
        @value-changed=${0}
      ></hui-action-editor>
    `),this.label,this.hass,this.value,null===(e=this.selector.ui_action)||void 0===e?void 0:e.actions,null===(t=this.selector.ui_action)||void 0===t?void 0:t.default_action,this.helper,this._valueChanged)}_valueChanged(e){(0,n.B)(this,"value-changed",{value:e.detail.value})}}(0,a.__decorate)([(0,r.Cb)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],p.prototype,"selector",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],p.prototype,"value",void 0),(0,a.__decorate)([(0,r.Cb)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,r.Cb)()],p.prototype,"helper",void 0),p=(0,a.__decorate)([(0,r.Mo)("ha-selector-ui_action")],p),o()}catch(c){o(c)}}))},36344:function(e,t,i){i(26847),i(1455),i(27530);var o=i(73742),a=i(24110),s=i(59048),r=i(7616),n=i(29740),d=i(77204),l=(i(58762),i(15606)),c=i(24393);i(30337);let h,p,u,v,_,g=e=>e;class m extends s.oi{setValue(e){try{this._yaml=(e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0})(e)?"":(0,a.$w)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){var e,t;null!==(e=this._codeEditor)&&void 0!==e&&e.codemirror&&(null===(t=this._codeEditor)||void 0===t||t.codemirror.focus())}render(){return void 0===this._yaml?s.Ld:(0,s.dy)(h||(h=g`
      ${0}
      <ha-code-editor
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${0}
        @value-changed=${0}
        dir="ltr"
      ></ha-code-editor>
      ${0}
    `),this.label?(0,s.dy)(p||(p=g`<p>${0}${0}</p>`),this.label,this.required?" *":""):s.Ld,this.hass,this._yaml,this.readOnly,!1===this.isValid,this._onChange,this.copyClipboard||this.hasExtraActions?(0,s.dy)(u||(u=g`
            <div class="card-actions">
              ${0}
              <slot name="extra-actions"></slot>
            </div>
          `),this.copyClipboard?(0,s.dy)(v||(v=g`
                    <ha-button @click=${0}>
                      ${0}
                    </ha-button>
                  `),this._copyYaml,this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")):s.Ld):s.Ld)}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,o=!0;if(this._yaml)try{t=(0,a.zD)(this._yaml,{schema:this.yamlSchema})}catch(s){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:s.reason})}${s.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:s.mark.line+1,column:s.mark.column+1})})`:""}`}else t={};this.value=t,this.isValid=o,(0,n.B)(this,"value-changed",{value:t,isValid:o,errorMsg:i})}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,c.v)(this.yaml),(0,l.C)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[d.Qx,(0,s.iv)(_||(_=g`
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
      `))]}constructor(...e){super(...e),this.yamlSchema=a.oW,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this._yaml=""}}(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)()],m.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],m.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"is-valid",type:Boolean})],m.prototype,"isValid",void 0),(0,o.__decorate)([(0,r.Cb)()],m.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"auto-update",type:Boolean})],m.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"read-only",type:Boolean})],m.prototype,"readOnly",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],m.prototype,"required",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"copy-clipboard",type:Boolean})],m.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"has-extra-actions",type:Boolean})],m.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,r.SB)()],m.prototype,"_yaml",void 0),(0,o.__decorate)([(0,r.IO)("ha-code-editor")],m.prototype,"_codeEditor",void 0),m=(0,o.__decorate)([(0,r.Mo)("ha-yaml-editor")],m)},32518:function(e,t,i){i.d(t,{PA:()=>r,Xp:()=>a,af:()=>d,eP:()=>o,fetchAssistPipelineLanguages:()=>l,jZ:()=>n,listAssistPipelines:()=>s});i(26847),i(87799),i(27530);const o=(e,t,i)=>"run-start"===t.type?e={init_options:i,stage:"ready",run:t.data,events:[t]}:e?((e="wake_word-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"wake_word",wake_word:Object.assign(Object.assign({},t.data),{},{done:!1})}):"wake_word-end"===t.type?Object.assign(Object.assign({},e),{},{wake_word:Object.assign(Object.assign(Object.assign({},e.wake_word),t.data),{},{done:!0})}):"stt-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"stt",stt:Object.assign(Object.assign({},t.data),{},{done:!1})}):"stt-end"===t.type?Object.assign(Object.assign({},e),{},{stt:Object.assign(Object.assign(Object.assign({},e.stt),t.data),{},{done:!0})}):"intent-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"intent",intent:Object.assign(Object.assign({},t.data),{},{done:!1})}):"intent-end"===t.type?Object.assign(Object.assign({},e),{},{intent:Object.assign(Object.assign(Object.assign({},e.intent),t.data),{},{done:!0})}):"tts-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"tts",tts:Object.assign(Object.assign({},t.data),{},{done:!1})}):"tts-end"===t.type?Object.assign(Object.assign({},e),{},{tts:Object.assign(Object.assign(Object.assign({},e.tts),t.data),{},{done:!0})}):"run-end"===t.type?Object.assign(Object.assign({},e),{},{stage:"done"}):"error"===t.type?Object.assign(Object.assign({},e),{},{stage:"error",error:t.data}):Object.assign({},e)).events=[...e.events,t],e):void console.warn("Received unexpected event before receiving session",t),a=(e,t,i)=>e.connection.subscribeMessage(t,Object.assign(Object.assign({},i),{},{type:"assist_pipeline/run"})),s=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),r=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),n=(e,t)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/create"},t)),d=(e,t,i)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/update",pipeline_id:t},i)),l=e=>e.callWS({type:"assist_pipeline/language/list"})},47469:function(e,t,i){i.d(t,{F3:()=>a,Lh:()=>o,t4:()=>s});i(16811);const o=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,a=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},s=(e,t)=>e.callWS({type:"manifest/get",integration:t})},8265:function(e,t,i){i.d(t,{Q2:()=>o});const o=(e,t,i)=>e.sendMessagePromise({type:"lovelace/config",url_path:t,force:i})},18234:function(e,t,i){i.a(e,(async function(e,t){try{i(26847),i(81738),i(6989),i(87799),i(27530);var o=i(73742),a=i(59048),s=i(7616),r=i(28105),n=i(29740),d=i(41806),l=i(69187),c=i(57027),h=(i(93795),i(20797)),p=i(45618),u=e([l,c,h,p]);[l,c,h,p]=u.then?(await u)():u;let v,_,g,m,b,y,f,C,$=e=>e;const w=["more-info","toggle","navigate","url","perform-action","assist","none"],O=[{name:"navigation_path",selector:{navigation:{}}}],x=[{type:"grid",name:"",schema:[{name:"pipeline_id",selector:{assist_pipeline:{include_last_used:!0}}},{name:"start_listening",selector:{boolean:{}}}]}];class M extends a.oi{get _navigation_path(){const e=this.config;return(null==e?void 0:e.navigation_path)||""}get _url_path(){const e=this.config;return(null==e?void 0:e.url_path)||""}get _service(){const e=this.config;return(null==e?void 0:e.perform_action)||(null==e?void 0:e.service)||""}updated(e){super.updated(e),e.has("defaultAction")&&e.get("defaultAction")!==this.defaultAction&&this._select.layoutOptions()}render(){var e,t,i,o,s,r,n,l;if(!this.hass)return a.Ld;const c=null!==(e=this.actions)&&void 0!==e?e:w;let h=(null===(t=this.config)||void 0===t?void 0:t.action)||"default";return"call-service"===h&&(h="perform-action"),(0,a.dy)(v||(v=$`
      <div class="dropdown">
        <ha-select
          .label=${0}
          .configValue=${0}
          @selected=${0}
          .value=${0}
          @closed=${0}
          fixedMenuPosition
          naturalMenuWidt
        >
          <ha-list-item value="default">
            ${0}
            ${0}
          </ha-list-item>
          ${0}
        </ha-select>
        ${0}
      </div>
      ${0}
      ${0}
      ${0}
      ${0}
    `),this.label,"action",this._actionPicked,h,d.U,this.hass.localize("ui.panel.lovelace.editor.action-editor.actions.default_action"),this.defaultAction?` (${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${this.defaultAction}`).toLowerCase()})`:a.Ld,c.map((e=>(0,a.dy)(_||(_=$`
              <ha-list-item .value=${0}>
                ${0}
              </ha-list-item>
            `),e,this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${e}`)))),this.tooltipText?(0,a.dy)(g||(g=$`
              <ha-help-tooltip .label=${0}></ha-help-tooltip>
            `),this.tooltipText):a.Ld,"navigate"===(null===(i=this.config)||void 0===i?void 0:i.action)?(0,a.dy)(m||(m=$`
            <ha-form
              .hass=${0}
              .schema=${0}
              .data=${0}
              .computeLabel=${0}
              @value-changed=${0}
            >
            </ha-form>
          `),this.hass,O,this.config,this._computeFormLabel,this._formValueChanged):a.Ld,"url"===(null===(o=this.config)||void 0===o?void 0:o.action)?(0,a.dy)(b||(b=$`
            <ha-textfield
              .label=${0}
              .value=${0}
              .configValue=${0}
              @input=${0}
            ></ha-textfield>
          `),this.hass.localize("ui.panel.lovelace.editor.action-editor.url_path"),this._url_path,"url_path",this._valueChanged):a.Ld,"call-service"===(null===(s=this.config)||void 0===s?void 0:s.action)||"perform-action"===(null===(r=this.config)||void 0===r?void 0:r.action)?(0,a.dy)(y||(y=$`
            <ha-service-control
              .hass=${0}
              .value=${0}
              .showAdvanced=${0}
              narrow
              @value-changed=${0}
            ></ha-service-control>
          `),this.hass,this._serviceAction(this.config),null===(n=this.hass.userData)||void 0===n?void 0:n.showAdvanced,this._serviceValueChanged):a.Ld,"assist"===(null===(l=this.config)||void 0===l?void 0:l.action)?(0,a.dy)(f||(f=$`
            <ha-form
              .hass=${0}
              .schema=${0}
              .data=${0}
              .computeLabel=${0}
              @value-changed=${0}
            >
            </ha-form>
          `),this.hass,x,this.config,this._computeFormLabel,this._formValueChanged):a.Ld)}_actionPicked(e){var t;if(e.stopPropagation(),!this.hass)return;let i=null===(t=this.config)||void 0===t?void 0:t.action;"call-service"===i&&(i="perform-action");const o=e.target.value;if(i===o)return;if("default"===o)return void(0,n.B)(this,"value-changed",{value:void 0});let a;switch(o){case"url":a={url_path:this._url_path};break;case"perform-action":a={perform_action:this._service};break;case"navigate":a={navigation_path:this._navigation_path}}(0,n.B)(this,"value-changed",{value:Object.assign({action:o},a)})}_valueChanged(e){var t;if(e.stopPropagation(),!this.hass)return;const i=e.target,o=null!==(t=e.target.value)&&void 0!==t?t:e.target.checked;this[`_${i.configValue}`]!==o&&i.configValue&&(0,n.B)(this,"value-changed",{value:Object.assign(Object.assign({},this.config),{},{[i.configValue]:o})})}_formValueChanged(e){e.stopPropagation();const t=e.detail.value;(0,n.B)(this,"value-changed",{value:t})}_computeFormLabel(e){var t;return null===(t=this.hass)||void 0===t?void 0:t.localize(`ui.panel.lovelace.editor.action-editor.${e.name}`)}_serviceValueChanged(e){e.stopPropagation();const t=Object.assign(Object.assign({},this.config),{},{action:"perform-action",perform_action:e.detail.value.action||"",data:e.detail.value.data,target:e.detail.value.target||{}});e.detail.value.data||delete t.data,"service_data"in t&&delete t.service_data,"service"in t&&delete t.service,(0,n.B)(this,"value-changed",{value:t})}constructor(...e){super(...e),this._serviceAction=(0,r.Z)((e=>{var t;return Object.assign(Object.assign({action:this._service},e.data||e.service_data?{data:null!==(t=e.data)&&void 0!==t?t:e.service_data}:null),{},{target:e.target})}))}}M.styles=(0,a.iv)(C||(C=$`
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
  `)),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"config",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"label",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"actions",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"defaultAction",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"tooltipText",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],M.prototype,"hass",void 0),(0,o.__decorate)([(0,s.IO)("ha-select")],M.prototype,"_select",void 0),M=(0,o.__decorate)([(0,s.Mo)("hui-action-editor")],M),t()}catch(v){t(v)}}))},15606:function(e,t,i){i.d(t,{C:()=>a});var o=i(29740);const a=(e,t)=>(0,o.B)(e,"hass-notification",t)},28177:function(e,t,i){i.d(t,{C:()=>p});i(26847),i(81738),i(29981),i(1455),i(27530);var o=i(31152),a=i(5277),s=i(93847);i(84730),i(15411),i(40777);class r{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class n{get(){return this.Y}pause(){var e;null!==(e=this.Y)&&void 0!==e||(this.Y=new Promise((e=>this.Z=e)))}resume(){var e;null!==(e=this.Z)&&void 0!==e&&e.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var d=i(83522);const l=e=>!(0,a.pt)(e)&&"function"==typeof e.then,c=1073741823;class h extends s.sR{render(...e){var t;return null!==(t=e.find((e=>!l(e))))&&void 0!==t?t:o.Jb}update(e,t){const i=this._$Cbt;let a=i.length;this._$Cbt=t;const s=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let o=0;o<t.length&&!(o>this._$Cwt);o++){const e=t[o];if(!l(e))return this._$Cwt=o,e;o<a&&e===i[o]||(this._$Cwt=c,a=0,Promise.resolve(e).then((async t=>{for(;r.get();)await r.get();const i=s.deref();if(void 0!==i){const o=i._$Cbt.indexOf(e);o>-1&&o<i._$Cwt&&(i._$Cwt=o,i.setValue(t))}})))}return o.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new r(this),this._$CX=new n}}const p=(0,d.XM)(h)}}]);
//# sourceMappingURL=4940.ea4fc74cbfb329b8.js.map