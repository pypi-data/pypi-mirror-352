"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5601"],{22543:function(o,t,e){e.r(t);e(26847),e(27530);var r=e(73742),a=e(59048),i=e(7616),n=e(31733),s=e(29740);e(78645),e(40830);let c,l,d,p,h=o=>o;const v={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class b extends a.oi{render(){return(0,a.dy)(c||(c=h`
      <div
        class="issue-type ${0}"
        role="alert"
      >
        <div class="icon ${0}">
          <slot name="icon">
            <ha-svg-icon .path=${0}></ha-svg-icon>
          </slot>
        </div>
        <div class=${0}>
          <div class="main-content">
            ${0}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${0}
            </slot>
          </div>
        </div>
      </div>
    `),(0,n.$)({[this.alertType]:!0}),this.title?"":"no-title",v[this.alertType],(0,n.$)({content:!0,narrow:this.narrow}),this.title?(0,a.dy)(l||(l=h`<div class="title">${0}</div>`),this.title):a.Ld,this.dismissable?(0,a.dy)(d||(d=h`<ha-icon-button
                    @click=${0}
                    label="Dismiss alert"
                    .path=${0}
                  ></ha-icon-button>`),this._dismissClicked,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):a.Ld)}_dismissClicked(){(0,s.B)(this,"alert-dismissed-clicked")}constructor(...o){super(...o),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}b.styles=(0,a.iv)(p||(p=h`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: 4px;
    }
    .icon {
      z-index: 1;
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 0;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action mwc-button,
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `)),(0,r.__decorate)([(0,i.Cb)()],b.prototype,"title",void 0),(0,r.__decorate)([(0,i.Cb)({attribute:"alert-type"})],b.prototype,"alertType",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean})],b.prototype,"dismissable",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean})],b.prototype,"narrow",void 0),b=(0,r.__decorate)([(0,i.Mo)("ha-alert")],b)},65706:function(o,t,e){e.r(t);e(26847),e(27530);var r=e(73742),a=(e(98334),e(59048)),i=e(7616);e(64218),e(38098),e(22543);let n,s,c,l,d,p=o=>o;class h extends a.oi{render(){var o,t;return(0,a.dy)(n||(n=p`
      ${0}
      <div class="content">
        <ha-alert alert-type="error">${0}</ha-alert>
        <slot>
          <mwc-button @click=${0}>
            ${0}
          </mwc-button>
        </slot>
      </div>
    `),this.toolbar?(0,a.dy)(s||(s=p`<div class="toolbar">
            ${0}
          </div>`),this.rootnav||null!==(o=history.state)&&void 0!==o&&o.root?(0,a.dy)(c||(c=p`
                  <ha-menu-button
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.hass,this.narrow):(0,a.dy)(l||(l=p`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._handleBack)):"",this.error,this._handleBack,null===(t=this.hass)||void 0===t?void 0:t.localize("ui.common.back"))}_handleBack(){history.back()}static get styles(){return[(0,a.iv)(d||(d=p`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          color: var(--primary-text-color);
          height: calc(100% - var(--header-height));
          display: flex;
          padding: 16px;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          box-sizing: border-box;
        }
        a {
          color: var(--primary-color);
        }
        ha-alert {
          margin-bottom: 16px;
        }
      `))]}constructor(...o){super(...o),this.toolbar=!0,this.rootnav=!1,this.narrow=!1}}(0,r.__decorate)([(0,i.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean})],h.prototype,"toolbar",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean})],h.prototype,"rootnav",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean})],h.prototype,"narrow",void 0),(0,r.__decorate)([(0,i.Cb)()],h.prototype,"error",void 0),h=(0,r.__decorate)([(0,i.Mo)("hass-error-screen")],h)},57694:function(o,t,e){e.r(t),e.d(t,{KNXError:()=>l});var r=e(73742),a=e(59048),i=e(7616),n=e(51597);e(62790),e(65706);let s,c=o=>o;class l extends a.oi{render(){var o,t;const e=null!==(o=null===(t=n.mainWindow.history.state)||void 0===t?void 0:t.message)&&void 0!==o?o:"Unknown error";return(0,a.dy)(s||(s=c`
      <hass-error-screen
        .hass=${0}
        .error=${0}
        .toolbar=${0}
        .rootnav=${0}
        .narrow=${0}
      ></hass-error-screen>
    `),this.hass,e,!0,!1,this.narrow)}}(0,r.__decorate)([(0,i.Cb)({type:Object})],l.prototype,"hass",void 0),(0,r.__decorate)([(0,i.Cb)({attribute:!1})],l.prototype,"knx",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean,reflect:!0})],l.prototype,"narrow",void 0),(0,r.__decorate)([(0,i.Cb)({type:Object})],l.prototype,"route",void 0),(0,r.__decorate)([(0,i.Cb)({type:Array,reflect:!1})],l.prototype,"tabs",void 0),l=(0,r.__decorate)([(0,i.Mo)("knx-error")],l)}}]);
//# sourceMappingURL=5601.a0278d94bf55b83b.js.map