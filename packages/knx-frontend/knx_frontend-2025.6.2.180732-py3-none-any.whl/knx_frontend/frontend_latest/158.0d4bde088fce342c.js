export const __webpack_ids__=["158"];export const __webpack_modules__={35505:function(e,t,i){i.d(t,{K:()=>o});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},76137:function(e,t,i){var o=i(73742),a=(i(1051),i(59048)),r=i(7616),n=i(31733),s=i(29740),l=(i(30337),i(78645),i(35505)),d=i(74608);const c="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",p="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z";class h extends a.oi{firstUpdated(e){super.firstUpdated(e),this.autoOpenFileDialog&&this._openFilePicker()}get _name(){if(void 0===this.value)return"";if("string"==typeof this.value)return this.value;return(this.value instanceof FileList?Array.from(this.value):(0,d.r)(this.value)).map((e=>e.name)).join(", ")}render(){const e=this.localize||this.hass.localize;return a.dy`
      ${this.uploading?a.dy`<div class="container">
            <div class="uploading">
              <span class="header"
                >${this.uploadingLabel||this.value?e("ui.components.file-upload.uploading_name",{name:this._name}):e("ui.components.file-upload.uploading")}</span
              >
              ${this.progress?a.dy`<div class="progress">
                    ${this.progress}${this.hass&&(0,l.K)(this.hass.locale)}%
                  </div>`:a.Ld}
            </div>
            <mwc-linear-progress
              .indeterminate=${!this.progress}
              .progress=${this.progress?this.progress/100:void 0}
            ></mwc-linear-progress>
          </div>`:a.dy`<label
            for=${this.value?"":"input"}
            class="container ${(0,n.$)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)})}"
            @drop=${this._handleDrop}
            @dragenter=${this._handleDragStart}
            @dragover=${this._handleDragStart}
            @dragleave=${this._handleDragEnd}
            @dragend=${this._handleDragEnd}
            >${this.value?"string"==typeof this.value?a.dy`<div class="row">
                    <div class="value" @click=${this._openFilePicker}>
                      <ha-svg-icon
                        .path=${this.icon||p}
                      ></ha-svg-icon>
                      ${this.value}
                    </div>
                    <ha-icon-button
                      @click=${this._clearValue}
                      .label=${this.deleteLabel||e("ui.common.delete")}
                      .path=${c}
                    ></ha-icon-button>
                  </div>`:(this.value instanceof FileList?Array.from(this.value):(0,d.r)(this.value)).map((t=>a.dy`<div class="row">
                        <div class="value" @click=${this._openFilePicker}>
                          <ha-svg-icon
                            .path=${this.icon||p}
                          ></ha-svg-icon>
                          ${t.name} - ${((e=0,t=2)=>{if(0===e)return"0 Bytes";t=t<0?0:t;const i=Math.floor(Math.log(e)/Math.log(1024));return`${parseFloat((e/1024**i).toFixed(t))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][i]}`})(t.size)}
                        </div>
                        <ha-icon-button
                          @click=${this._clearValue}
                          .label=${this.deleteLabel||e("ui.common.delete")}
                          .path=${c}
                        ></ha-icon-button>
                      </div>`)):a.dy`<ha-svg-icon
                    class="big-icon"
                    .path=${this.icon||p}
                  ></ha-svg-icon>
                  <ha-button unelevated @click=${this._openFilePicker}>
                    ${this.label||e("ui.components.file-upload.label")}
                  </ha-button>
                  <span class="secondary"
                    >${this.secondary||e("ui.components.file-upload.secondary")}</span
                  >
                  <span class="supports">${this.supports}</span>`}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${this.accept}
              .multiple=${this.multiple}
              @change=${this._handleFilePicked}
          /></label>`}
    `}_openFilePicker(){this._input?.click()}_handleDrop(e){e.preventDefault(),e.stopPropagation(),e.dataTransfer?.files&&(0,s.B)(this,"file-picked",{files:this.multiple||1===e.dataTransfer.files.length?Array.from(e.dataTransfer.files):[e.dataTransfer.files[0]]}),this._drag=!1}_handleDragStart(e){e.preventDefault(),e.stopPropagation(),this._drag=!0}_handleDragEnd(e){e.preventDefault(),e.stopPropagation(),this._drag=!1}_handleFilePicked(e){0!==e.target.files.length&&(this.value=e.target.files,(0,s.B)(this,"file-picked",{files:e.target.files}))}_clearValue(e){e.preventDefault(),this._input.value="",this.value=void 0,(0,s.B)(this,"change"),(0,s.B)(this,"files-cleared")}constructor(...e){super(...e),this.multiple=!1,this.disabled=!1,this.uploading=!1,this.autoOpenFileDialog=!1,this._drag=!1}}h.styles=a.iv`
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
  `,(0,o.__decorate)([(0,r.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],h.prototype,"localize",void 0),(0,o.__decorate)([(0,r.Cb)()],h.prototype,"accept",void 0),(0,o.__decorate)([(0,r.Cb)()],h.prototype,"icon",void 0),(0,o.__decorate)([(0,r.Cb)()],h.prototype,"label",void 0),(0,o.__decorate)([(0,r.Cb)()],h.prototype,"secondary",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"uploading-label"})],h.prototype,"uploadingLabel",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:"delete-label"})],h.prototype,"deleteLabel",void 0),(0,o.__decorate)([(0,r.Cb)()],h.prototype,"supports",void 0),(0,o.__decorate)([(0,r.Cb)({type:Object})],h.prototype,"value",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],h.prototype,"multiple",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],h.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean})],h.prototype,"uploading",void 0),(0,o.__decorate)([(0,r.Cb)({type:Number})],h.prototype,"progress",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,attribute:"auto-open-file-dialog"})],h.prototype,"autoOpenFileDialog",void 0),(0,o.__decorate)([(0,r.SB)()],h.prototype,"_drag",void 0),(0,o.__decorate)([(0,r.IO)("#input")],h.prototype,"_input",void 0),h=(0,o.__decorate)([(0,r.Mo)("ha-file-upload")],h)},71268:function(e,t,i){i.d(t,{Y:()=>a,c:()=>o});const o=async(e,t)=>{const i=new FormData;i.append("file",t);const o=await e.fetchWithAuth("/api/file_upload",{method:"POST",body:i});if(413===o.status)throw new Error(`Uploaded file is too large (${t.name})`);if(200!==o.status)throw new Error("Unknown error");return(await o.json()).file_id},a=async(e,t)=>e.callApi("DELETE","file_upload",{file_id:t})},10840:function(e,t,i){i.d(t,{js:()=>a,rY:()=>o});const o=e=>e.data,a=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])},81665:function(e,t,i){i.d(t,{D9:()=>l,Ys:()=>n,g7:()=>s});var o=i(29740);const a=()=>Promise.all([i.e("5055"),i.e("3214")]).then(i.bind(i,40460)),r=(e,t,i)=>new Promise((r=>{const n=t.cancel,s=t.confirm;(0,o.B)(e,"show-dialog",{dialogTag:"dialog-box",dialogImport:a,dialogParams:{...t,...i,cancel:()=>{r(!!i?.prompt&&null),n&&n()},confirm:e=>{r(!i?.prompt||e),s&&s(e)}}})})),n=(e,t)=>r(e,t),s=(e,t)=>r(e,t,{confirmation:!0}),l=(e,t)=>r(e,t,{prompt:!0})},63079:function(e,t,i){i.r(t),i.d(t,{KNXInfo:()=>u});var o=i(73742),a=i(59048),r=i(7616),n=i(29740),s=(i(13965),i(62790),i(30337),i(76137),i(10667),i(71268)),l=i(10840),d=i(81665),c=i(63279),p=i(38059);const h=new p.r("info");class u extends a.oi{render(){return a.dy`
      <hass-tabs-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        .route=${this.route}
        .tabs=${this.tabs}
        .localizeFunc=${this.knx.localize}
      >
        <div class="columns">
          ${this._renderInfoCard()}
          ${this.knx.info.project?this._renderProjectDataCard(this.knx.info.project):a.Ld}
          ${this._renderProjectUploadCard()}
        </div>
      </hass-tabs-subpage>
    `}_renderInfoCard(){return a.dy` <ha-card class="knx-info">
      <div class="card-content knx-info-section">
        <div class="knx-content-row header">${this.knx.localize("info_information_header")}</div>

        <div class="knx-content-row">
          <div>XKNX Version</div>
          <div>${this.knx.info.version}</div>
        </div>

        <div class="knx-content-row">
          <div>KNX-Frontend Version</div>
          <div>${"2025.6.2.180732"}</div>
        </div>

        <div class="knx-content-row">
          <div>${this.knx.localize("info_connected_to_bus")}</div>
          <div>
            ${this.hass.localize(this.knx.info.connected?"ui.common.yes":"ui.common.no")}
          </div>
        </div>

        <div class="knx-content-row">
          <div>${this.knx.localize("info_individual_address")}</div>
          <div>${this.knx.info.current_address}</div>
        </div>

        <div class="knx-bug-report">
          ${this.knx.localize("info_issue_tracker")}
          <a href="https://github.com/XKNX/knx-integration" target="_blank">xknx/knx-integration</a>
        </div>

        <div class="knx-bug-report">
          ${this.knx.localize("info_my_knx")}
          <a href="https://my.knx.org" target="_blank">my.knx.org</a>
        </div>
      </div>
    </ha-card>`}_renderProjectDataCard(e){return a.dy`
      <ha-card class="knx-info">
          <div class="card-content knx-content">
            <div class="header knx-content-row">
              ${this.knx.localize("info_project_data_header")}
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_name")}</div>
              <div>${e.name}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_last_modified")}</div>
              <div>${new Date(e.last_modified).toUTCString()}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_tool_version")}</div>
              <div>${e.tool_version}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_xknxproject_version")}</div>
              <div>${e.xknxproject_version}</div>
            </div>
            <div class="knx-button-row">
              <ha-button
                class="knx-warning push-right"
                @click=${this._removeProject}
                .disabled=${this._uploading||!this.knx.info.project}
                >
                ${this.knx.localize("info_project_delete")}
              </ha-button>
            </div>
          </div>
        </div>
      </ha-card>
    `}_renderProjectUploadCard(){return a.dy` <ha-card class="knx-info">
      <div class="card-content knx-content">
        <div class="knx-content-row header">${this.knx.localize("info_project_file_header")}</div>
        <div class="knx-content-row">${this.knx.localize("info_project_upload_description")}</div>
        <div class="knx-content-row">
          <ha-file-upload
            .hass=${this.hass}
            accept=".knxproj, .knxprojarchive"
            .icon=${"M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z"}
            .label=${this.knx.localize("info_project_file")}
            .value=${this._projectFile?.name}
            .uploading=${this._uploading}
            @file-picked=${this._filePicked}
          ></ha-file-upload>
        </div>
        <div class="knx-content-row">
          <ha-selector-text
            .hass=${this.hass}
            .value=${this._projectPassword||""}
            .label=${this.hass.localize("ui.login-form.password")}
            .selector=${{text:{multiline:!1,type:"password"}}}
            .required=${!1}
            @value-changed=${this._passwordChanged}
          >
          </ha-selector-text>
        </div>
        <div class="knx-button-row">
          <ha-button
            class="push-right"
            @click=${this._uploadFile}
            .disabled=${this._uploading||!this._projectFile}
            >${this.hass.localize("ui.common.submit")}</ha-button
          >
        </div>
      </div>
    </ha-card>`}_filePicked(e){this._projectFile=e.detail.files[0]}_passwordChanged(e){this._projectPassword=e.detail.value}async _uploadFile(e){const t=this._projectFile;if(void 0===t)return;let i;this._uploading=!0;try{const e=await(0,s.c)(this.hass,t);await(0,c.cO)(this.hass,e,this._projectPassword||"")}catch(o){i=o,(0,d.Ys)(this,{title:"Upload failed",text:(0,l.js)(o)})}finally{i||(this._projectFile=void 0,this._projectPassword=void 0),this._uploading=!1,(0,n.B)(this,"knx-reload")}}async _removeProject(e){if(await(0,d.g7)(this,{text:this.knx.localize("info_project_delete")}))try{await(0,c.Hk)(this.hass)}catch(t){(0,d.Ys)(this,{title:"Deletion failed",text:(0,l.js)(t)})}finally{(0,n.B)(this,"knx-reload")}else h.debug("User cancelled deletion")}constructor(...e){super(...e),this._uploading=!1}}u.styles=a.iv`
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
  `,(0,o.__decorate)([(0,r.Cb)({type:Object})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,r.Cb)({attribute:!1})],u.prototype,"knx",void 0),(0,o.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],u.prototype,"narrow",void 0),(0,o.__decorate)([(0,r.Cb)({type:Object})],u.prototype,"route",void 0),(0,o.__decorate)([(0,r.Cb)({type:Array,reflect:!1})],u.prototype,"tabs",void 0),(0,o.__decorate)([(0,r.SB)()],u.prototype,"_projectPassword",void 0),(0,o.__decorate)([(0,r.SB)()],u.prototype,"_uploading",void 0),(0,o.__decorate)([(0,r.SB)()],u.prototype,"_projectFile",void 0),u=(0,o.__decorate)([(0,r.Mo)("knx-info")],u)}};
//# sourceMappingURL=158.0d4bde088fce342c.js.map