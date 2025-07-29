"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5423"],{35859:function(e,t,i){i.d(t,{I:()=>o});i(39710),i(26847),i(56389),i(27530);const o=(e,t,i,o)=>{const[a,n,r]=e.split(".",3);return Number(a)>t||Number(a)===t&&(void 0===o?Number(n)>=i:Number(n)>i)||void 0!==o&&Number(a)===t&&Number(n)===i&&Number(r)>=o}},35505:function(e,t,i){i.d(t,{K:()=>o});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},34998:function(e,t,i){i.a(e,(async function(e,t){try{i(26847),i(81738),i(6989),i(27530);var o=i(73742),a=i(61611),n=i(59048),r=i(7616),s=i(31733),l=i(29740),d=(i(30337),i(78645),i(35505)),c=i(74608),p=i(57874),h=e([a]);a=(h.then?(await h)():h)[0];let u,v,f,g,_,b,x,m,k=e=>e;const y="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",$="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z";class w extends n.oi{firstUpdated(e){super.firstUpdated(e),this.autoOpenFileDialog&&this._openFilePicker()}get _name(){if(void 0===this.value)return"";if("string"==typeof this.value)return this.value;return(this.value instanceof FileList?Array.from(this.value):(0,c.r)(this.value)).map((e=>e.name)).join(", ")}render(){const e=this.localize||this.hass.localize;return(0,n.dy)(u||(u=k`
      ${0}
    `),this.uploading?(0,n.dy)(v||(v=k`<div class="container">
            <div class="uploading">
              <span class="header"
                >${0}</span
              >
              ${0}
            </div>
            <mwc-linear-progress
              .indeterminate=${0}
              .progress=${0}
            ></mwc-linear-progress>
          </div>`),this.uploadingLabel||this.value?e("ui.components.file-upload.uploading_name",{name:this._name}):e("ui.components.file-upload.uploading"),this.progress?(0,n.dy)(f||(f=k`<div class="progress">
                    ${0}${0}%
                  </div>`),this.progress,this.hass&&(0,d.K)(this.hass.locale)):n.Ld,!this.progress,this.progress?this.progress/100:void 0):(0,n.dy)(g||(g=k`<label
            for=${0}
            class="container ${0}"
            @drop=${0}
            @dragenter=${0}
            @dragover=${0}
            @dragleave=${0}
            @dragend=${0}
            >${0}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${0}
              .multiple=${0}
              @change=${0}
          /></label>`),this.value?"":"input",(0,s.$)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)}),this._handleDrop,this._handleDragStart,this._handleDragStart,this._handleDragEnd,this._handleDragEnd,this.value?"string"==typeof this.value?(0,n.dy)(b||(b=k`<div class="row">
                    <div class="value" @click=${0}>
                      <ha-svg-icon
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </div>
                    <ha-icon-button
                      @click=${0}
                      .label=${0}
                      .path=${0}
                    ></ha-icon-button>
                  </div>`),this._openFilePicker,this.icon||$,this.value,this._clearValue,this.deleteLabel||e("ui.common.delete"),y):(this.value instanceof FileList?Array.from(this.value):(0,c.r)(this.value)).map((t=>(0,n.dy)(x||(x=k`<div class="row">
                        <div class="value" @click=${0}>
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                          ${0} - ${0}
                        </div>
                        <ha-icon-button
                          @click=${0}
                          .label=${0}
                          .path=${0}
                        ></ha-icon-button>
                      </div>`),this._openFilePicker,this.icon||$,t.name,(0,p.d)(t.size),this._clearValue,this.deleteLabel||e("ui.common.delete"),y))):(0,n.dy)(_||(_=k`<ha-svg-icon
                    class="big-icon"
                    .path=${0}
                  ></ha-svg-icon>
                  <ha-button unelevated @click=${0}>
                    ${0}
                  </ha-button>
                  <span class="secondary"
                    >${0}</span
                  >
                  <span class="supports">${0}</span>`),this.icon||$,this._openFilePicker,this.label||e("ui.components.file-upload.label"),this.secondary||e("ui.components.file-upload.secondary"),this.supports),this.accept,this.multiple,this._handleFilePicked))}_openFilePicker(){var e;null===(e=this._input)||void 0===e||e.click()}_handleDrop(e){var t;e.preventDefault(),e.stopPropagation(),null!==(t=e.dataTransfer)&&void 0!==t&&t.files&&(0,l.B)(this,"file-picked",{files:this.multiple||1===e.dataTransfer.files.length?Array.from(e.dataTransfer.files):[e.dataTransfer.files[0]]}),this._drag=!1}_handleDragStart(e){e.preventDefault(),e.stopPropagation(),this._drag=!0}_handleDragEnd(e){e.preventDefault(),e.stopPropagation(),this._drag=!1}_handleFilePicked(e){0!==e.target.files.length&&(this.value=e.target.files,(0,l.B)(this,"file-picked",{files:e.target.files}))}_clearValue(e){e.preventDefault(),this._input.value="",this.value=void 0,(0,l.B)(this,"change"),(0,l.B)(this,"files-cleared")}constructor(...e){super(...e),this.multiple=!1,this.disabled=!1,this.uploading=!1,this.autoOpenFileDialog=!1,this._drag=!1}}w.styles=(0,n.iv)(m||(m=k`
    :host {
      display: block;
      height: 240px;
    }
    :host([disabled]) {
      pointer-events: none;
      color: var(--disabled-text-color);
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: solid 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      border-radius: var(--mdc-shape-small, 4px);
      height: 100%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    label.container {
      border: dashed 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      cursor: pointer;
    }
    .container .uploading {
      display: flex;
      flex-direction: column;
      width: 100%;
      align-items: flex-start;
      padding: 0 32px;
      box-sizing: border-box;
    }
    :host([disabled]) .container {
      border-color: var(--disabled-color);
    }
    label:hover,
    label.dragged {
      border-style: solid;
    }
    label.dragged {
      border-color: var(--primary-color);
    }
    .dragged:before {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-color: var(--primary-color);
      content: "";
      opacity: var(--dark-divider-opacity);
      pointer-events: none;
      border-radius: var(--mdc-shape-small, 4px);
    }
    label.value {
      cursor: default;
    }
    label.value.multiple {
      justify-content: unset;
      overflow: auto;
    }
    .highlight {
      color: var(--primary-color);
    }
    ha-button {
      margin-bottom: 4px;
    }
    .supports {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
    :host([disabled]) .secondary {
      color: var(--disabled-text-color);
    }
    input.file {
      display: none;
    }
    .value {
      cursor: pointer;
    }
    .value ha-svg-icon {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
    .big-icon {
      --mdc-icon-size: 48px;
      margin-bottom: 8px;
    }
    ha-button {
      --mdc-button-outline-color: var(--primary-color);
      --mdc-icon-button-size: 24px;
    }
    mwc-linear-progress {
      width: 100%;
      padding: 8px 32px;
      box-sizing: border-box;
    }
    .header {
      font-weight: var(--ha-font-weight-medium);
    }
    .progress {
      color: var(--secondary-text-color);
    }
    button.link {
      background: none;
      border: none;
      padding: 0;
      font-size: var(--ha-font-size-m);
      color: var(--primary-color);
      text-decoration: underline;
      cursor: pointer;
    }
  `)),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],w.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],w.prototype,"localize",void 0),(0,o.__decorate)([(0,r.Cb)()],w.prototype,"accept",void 0),(0,o.__decorate)([(0,r.Cb)()],w.prototype,"icon",void 0),(0,o.__decorate)([(0,r.Cb)()],w.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)()],w.prototype,"secondary",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"uploading-label"})],w.prototype,"uploadingLabel",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"delete-label"})],w.prototype,"deleteLabel",void 0),(0,o.__decorate)([(0,r.Cb)()],w.prototype,"supports",void 0),(0,o.__decorate)([(0,r.Cb)({type:Object})],w.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],w.prototype,"multiple",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],w.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],w.prototype,"uploading",void 0),(0,o.__decorate)([(0,r.Cb)({type:Number})],w.prototype,"progress",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,attribute:"auto-open-file-dialog"})],w.prototype,"autoOpenFileDialog",void 0),(0,o.__decorate)([(0,r.SB)()],w.prototype,"_drag",void 0),(0,o.__decorate)([(0,r.IO)("#input")],w.prototype,"_input",void 0),w=(0,o.__decorate)([(0,r.Mo)("ha-file-upload")],w),t()}catch(u){t(u)}}))},71268:function(e,t,i){i.d(t,{Y:()=>a,c:()=>o});i(40777),i(1455);const o=async(e,t)=>{const i=new FormData;i.append("file",t);const o=await e.fetchWithAuth("/api/file_upload",{method:"POST",body:i});if(413===o.status)throw new Error(`Uploaded file is too large (${t.name})`);if(200!==o.status)throw new Error("Unknown error");return(await o.json()).file_id},a=async(e,t)=>e.callApi("DELETE","file_upload",{file_id:t})},10840:function(e,t,i){i.d(t,{js:()=>a,rY:()=>o});i(39710),i(26847),i(1455),i(67886),i(65451),i(46015),i(38334),i(94880),i(75643),i(29761),i(56389),i(27530),i(35859);const o=e=>e.data,a=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])},81665:function(e,t,i){i.d(t,{D9:()=>l,Ys:()=>r,g7:()=>s});i(26847),i(87799),i(1455),i(27530);var o=i(29740);const a=()=>Promise.all([i.e("5055"),i.e("3214")]).then(i.bind(i,40460)),n=(e,t,i)=>new Promise((n=>{const r=t.cancel,s=t.confirm;(0,o.B)(e,"show-dialog",{dialogTag:"dialog-box",dialogImport:a,dialogParams:Object.assign(Object.assign(Object.assign({},t),i),{},{cancel:()=>{n(!(null==i||!i.prompt)&&null),r&&r()},confirm:e=>{n(null==i||!i.prompt||e),s&&s(e)}})})})),r=(e,t)=>n(e,t),s=(e,t)=>n(e,t,{confirmation:!0}),l=(e,t)=>n(e,t,{prompt:!0})},57874:function(e,t,i){i.d(t,{d:()=>o});i(25718),i(15519);const o=(e=0,t=2)=>{if(0===e)return"0 Bytes";t=t<0?0:t;const i=Math.floor(Math.log(e)/Math.log(1024));return`${parseFloat((e/1024**i).toFixed(t))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][i]}`}},26014:function(e,t,i){i.d(t,{q:()=>o});const o="2025.6.2.180732"},75681:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{KNXInfo:()=>w});i(26847),i(1455),i(27530);var a=i(73742),n=i(59048),r=i(7616),s=i(29740),l=(i(13965),i(62790),i(30337),i(34998)),d=(i(10667),i(71268)),c=i(10840),p=i(81665),h=i(63279),u=i(38059),v=i(26014),f=e([l]);l=(f.then?(await f)():f)[0];let g,_,b,x,m,k=e=>e;const y="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z",$=new u.r("info");class w extends n.oi{render(){return(0,n.dy)(g||(g=k`
      <hass-tabs-subpage
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
      >
        <div class="columns">
          ${0}
          ${0}
          ${0}
        </div>
      </hass-tabs-subpage>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this._renderInfoCard(),this.knx.info.project?this._renderProjectDataCard(this.knx.info.project):n.Ld,this._renderProjectUploadCard())}_renderInfoCard(){return(0,n.dy)(_||(_=k` <ha-card class="knx-info">
      <div class="card-content knx-info-section">
        <div class="knx-content-row header">${0}</div>

        <div class="knx-content-row">
          <div>XKNX Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>KNX-Frontend Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>
            ${0}
          </div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>${0}</div>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://github.com/XKNX/knx-integration" target="_blank">xknx/knx-integration</a>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://my.knx.org" target="_blank">my.knx.org</a>
        </div>
      </div>
    </ha-card>`),this.knx.localize("info_information_header"),this.knx.info.version,v.q,this.knx.localize("info_connected_to_bus"),this.hass.localize(this.knx.info.connected?"ui.common.yes":"ui.common.no"),this.knx.localize("info_individual_address"),this.knx.info.current_address,this.knx.localize("info_issue_tracker"),this.knx.localize("info_my_knx"))}_renderProjectDataCard(e){return(0,n.dy)(b||(b=k`
      <ha-card class="knx-info">
          <div class="card-content knx-content">
            <div class="header knx-content-row">
              ${0}
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-button-row">
              <ha-button
                class="knx-warning push-right"
                @click=${0}
                .disabled=${0}
                >
                ${0}
              </ha-button>
            </div>
          </div>
        </div>
      </ha-card>
    `),this.knx.localize("info_project_data_header"),this.knx.localize("info_project_data_name"),e.name,this.knx.localize("info_project_data_last_modified"),new Date(e.last_modified).toUTCString(),this.knx.localize("info_project_data_tool_version"),e.tool_version,this.knx.localize("info_project_data_xknxproject_version"),e.xknxproject_version,this._removeProject,this._uploading||!this.knx.info.project,this.knx.localize("info_project_delete"))}_renderProjectUploadCard(){var e;return(0,n.dy)(x||(x=k` <ha-card class="knx-info">
      <div class="card-content knx-content">
        <div class="knx-content-row header">${0}</div>
        <div class="knx-content-row">${0}</div>
        <div class="knx-content-row">
          <ha-file-upload
            .hass=${0}
            accept=".knxproj, .knxprojarchive"
            .icon=${0}
            .label=${0}
            .value=${0}
            .uploading=${0}
            @file-picked=${0}
          ></ha-file-upload>
        </div>
        <div class="knx-content-row">
          <ha-selector-text
            .hass=${0}
            .value=${0}
            .label=${0}
            .selector=${0}
            .required=${0}
            @value-changed=${0}
          >
          </ha-selector-text>
        </div>
        <div class="knx-button-row">
          <ha-button
            class="push-right"
            @click=${0}
            .disabled=${0}
            >${0}</ha-button
          >
        </div>
      </div>
    </ha-card>`),this.knx.localize("info_project_file_header"),this.knx.localize("info_project_upload_description"),this.hass,y,this.knx.localize("info_project_file"),null===(e=this._projectFile)||void 0===e?void 0:e.name,this._uploading,this._filePicked,this.hass,this._projectPassword||"",this.hass.localize("ui.login-form.password"),{text:{multiline:!1,type:"password"}},!1,this._passwordChanged,this._uploadFile,this._uploading||!this._projectFile,this.hass.localize("ui.common.submit"))}_filePicked(e){this._projectFile=e.detail.files[0]}_passwordChanged(e){this._projectPassword=e.detail.value}async _uploadFile(e){const t=this._projectFile;if(void 0===t)return;let i;this._uploading=!0;try{const e=await(0,d.c)(this.hass,t);await(0,h.cO)(this.hass,e,this._projectPassword||"")}catch(o){i=o,(0,p.Ys)(this,{title:"Upload failed",text:(0,c.js)(o)})}finally{i||(this._projectFile=void 0,this._projectPassword=void 0),this._uploading=!1,(0,s.B)(this,"knx-reload")}}async _removeProject(e){if(await(0,p.g7)(this,{text:this.knx.localize("info_project_delete")}))try{await(0,h.Hk)(this.hass)}catch(t){(0,p.Ys)(this,{title:"Deletion failed",text:(0,c.js)(t)})}finally{(0,s.B)(this,"knx-reload")}else $.debug("User cancelled deletion")}constructor(...e){super(...e),this._uploading=!1}}w.styles=(0,n.iv)(m||(m=k`
    .columns {
      display: flex;
      justify-content: center;
    }

    @media screen and (max-width: 1232px) {
      .columns {
        flex-direction: column;
      }

      .knx-button-row {
        margin-top: 20px;
      }

      .knx-info {
        margin-right: 8px;
      }
    }

    @media screen and (min-width: 1233px) {
      .knx-button-row {
        margin-top: auto;
      }

      .knx-info {
        width: 400px;
      }
    }

    .knx-info {
      margin-left: 8px;
      margin-top: 8px;
    }

    .knx-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      box-sizing: border-box;
    }

    .knx-content-row {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
    }

    .knx-content-row > div:nth-child(2) {
      margin-left: 1rem;
    }

    .knx-button-row {
      display: flex;
      flex-direction: row;
      vertical-align: bottom;
      padding-top: 16px;
    }

    .push-left {
      margin-right: auto;
    }

    .push-right {
      margin-left: auto;
    }

    .knx-warning {
      --mdc-theme-primary: var(--error-color);
    }

    .knx-project-description {
      margin-top: -8px;
      padding: 0px 16px 16px;
    }

    .knx-delete-project-button {
      position: absolute;
      bottom: 0;
      right: 0;
    }

    .knx-bug-report {
      margin-top: 20px;

      a {
        text-decoration: none;
      }
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, 24px);
      letter-spacing: -0.012em;
      line-height: 48px;
      padding: -4px 16px 16px;
      display: inline-block;
      margin-block-start: 0px;
      margin-block-end: 4px;
      font-weight: normal;
    }

    ha-file-upload,
    ha-selector-text {
      width: 100%;
      margin-top: 8px;
    }
  `)),(0,a.__decorate)([(0,r.Cb)({type:Object})],w.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],w.prototype,"knx",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],w.prototype,"narrow",void 0),(0,a.__decorate)([(0,r.Cb)({type:Object})],w.prototype,"route",void 0),(0,a.__decorate)([(0,r.Cb)({type:Array,reflect:!1})],w.prototype,"tabs",void 0),(0,a.__decorate)([(0,r.SB)()],w.prototype,"_projectPassword",void 0),(0,a.__decorate)([(0,r.SB)()],w.prototype,"_uploading",void 0),(0,a.__decorate)([(0,r.SB)()],w.prototype,"_projectFile",void 0),w=(0,a.__decorate)([(0,r.Mo)("knx-info")],w),o()}catch(g){o(g)}}))}}]);
//# sourceMappingURL=5423.8cb3837de83a2087.js.map