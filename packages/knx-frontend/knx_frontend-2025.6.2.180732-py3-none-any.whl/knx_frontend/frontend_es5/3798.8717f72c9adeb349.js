"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3798"],{87268:function(t,e,o){o.r(e),o.d(e,{HaButtonToggleSelector:()=>y});o(26847),o(18574),o(81738),o(22960),o(6989),o(27530);var i=o(73742),a=o(59048),l=o(7616),r=o(29740),n=o(92949),c=(o(1455),o(98334),o(20480));o(78645);let d,u,s,p,b=t=>t;class h extends a.oi{render(){return(0,a.dy)(d||(d=b`
      <div>
        ${0}
      </div>
    `),this.buttons.map((t=>t.iconPath?(0,a.dy)(u||(u=b`<ha-icon-button
                .label=${0}
                .path=${0}
                .value=${0}
                ?active=${0}
                @click=${0}
              ></ha-icon-button>`),t.label,t.iconPath,t.value,this.active===t.value,this._handleClick):(0,a.dy)(s||(s=b`<mwc-button
                style=${0}
                outlined
                .dense=${0}
                .value=${0}
                ?active=${0}
                @click=${0}
                >${0}</mwc-button
              >`),(0,c.V)({width:this.fullWidth?100/this.buttons.length+"%":"initial"}),this.dense,t.value,this.active===t.value,this._handleClick,t.label))))}updated(){var t;null===(t=this._buttons)||void 0===t||t.forEach((async t=>{await t.updateComplete,t.shadowRoot.querySelector("button").style.margin="0"}))}_handleClick(t){this.active=t.currentTarget.value,(0,r.B)(this,"value-changed",{value:this.active})}constructor(...t){super(...t),this.fullWidth=!1,this.dense=!1}}h.styles=(0,a.iv)(p||(p=b`
    div {
      display: flex;
      --mdc-icon-button-size: var(--button-toggle-size, 36px);
      --mdc-icon-size: var(--button-toggle-icon-size, 20px);
      direction: ltr;
    }
    mwc-button {
      flex: 1;
      --mdc-shape-small: 0;
      --mdc-button-outline-width: 1px 0 1px 1px;
      --mdc-button-outline-color: var(--primary-color);
    }
    ha-icon-button {
      border: 1px solid var(--primary-color);
      border-right-width: 0px;
    }
    ha-icon-button,
    mwc-button {
      position: relative;
      cursor: pointer;
    }
    ha-icon-button::before,
    mwc-button::before {
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      position: absolute;
      background-color: var(--primary-color);
      opacity: 0;
      pointer-events: none;
      content: "";
      transition:
        opacity 15ms linear,
        background-color 15ms linear;
    }
    ha-icon-button[active]::before,
    mwc-button[active]::before {
      opacity: 1;
    }
    ha-icon-button[active] {
      --icon-primary-color: var(--text-primary-color);
    }
    mwc-button[active] {
      --mdc-theme-primary: var(--text-primary-color);
    }
    ha-icon-button:first-child,
    mwc-button:first-child {
      --mdc-shape-small: 4px 0 0 4px;
      border-radius: 4px 0 0 4px;
      --mdc-button-outline-width: 1px;
    }
    mwc-button:first-child::before {
      border-radius: 4px 0 0 4px;
    }
    ha-icon-button:last-child,
    mwc-button:last-child {
      border-radius: 0 4px 4px 0;
      border-right-width: 1px;
      --mdc-shape-small: 0 4px 4px 0;
      --mdc-button-outline-width: 1px;
    }
    mwc-button:last-child::before {
      border-radius: 0 4px 4px 0;
    }
    ha-icon-button:only-child,
    mwc-button:only-child {
      --mdc-shape-small: 4px;
      border-right-width: 1px;
    }
  `)),(0,i.__decorate)([(0,l.Cb)({attribute:!1})],h.prototype,"buttons",void 0),(0,i.__decorate)([(0,l.Cb)()],h.prototype,"active",void 0),(0,i.__decorate)([(0,l.Cb)({attribute:"full-width",type:Boolean})],h.prototype,"fullWidth",void 0),(0,i.__decorate)([(0,l.Cb)({type:Boolean})],h.prototype,"dense",void 0),(0,i.__decorate)([(0,l.Kt)("mwc-button")],h.prototype,"_buttons",void 0),h=(0,i.__decorate)([(0,l.Mo)("ha-button-toggle-group")],h);let v,g,m=t=>t;class y extends a.oi{render(){var t,e,o;const i=(null===(t=this.selector.button_toggle)||void 0===t||null===(t=t.options)||void 0===t?void 0:t.map((t=>"object"==typeof t?t:{value:t,label:t})))||[],l=null===(e=this.selector.button_toggle)||void 0===e?void 0:e.translation_key;this.localizeValue&&l&&i.forEach((t=>{const e=this.localizeValue(`${l}.options.${t.value}`);e&&(t.label=e)})),null!==(o=this.selector.button_toggle)&&void 0!==o&&o.sort&&i.sort(((t,e)=>(0,n.fe)(t.label,e.label,this.hass.locale.language)));const r=i.map((t=>({label:t.label,value:t.value})));return(0,a.dy)(v||(v=m`
      ${0}
      <ha-button-toggle-group
        .buttons=${0}
        .active=${0}
        @value-changed=${0}
      ></ha-button-toggle-group>
    `),this.label,r,this.value,this._valueChanged)}_valueChanged(t){var e,o;t.stopPropagation();const i=(null===(e=t.detail)||void 0===e?void 0:e.value)||t.target.value;this.disabled||void 0===i||i===(null!==(o=this.value)&&void 0!==o?o:"")||(0,r.B)(this,"value-changed",{value:i})}constructor(...t){super(...t),this.disabled=!1,this.required=!0}}y.styles=(0,a.iv)(g||(g=m`
    :host {
      position: relative;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    @media all and (max-width: 600px) {
      ha-button-toggle-group {
        flex: 1;
      }
    }
  `)),(0,i.__decorate)([(0,l.Cb)({attribute:!1})],y.prototype,"hass",void 0),(0,i.__decorate)([(0,l.Cb)({attribute:!1})],y.prototype,"selector",void 0),(0,i.__decorate)([(0,l.Cb)()],y.prototype,"value",void 0),(0,i.__decorate)([(0,l.Cb)()],y.prototype,"label",void 0),(0,i.__decorate)([(0,l.Cb)()],y.prototype,"helper",void 0),(0,i.__decorate)([(0,l.Cb)({attribute:!1})],y.prototype,"localizeValue",void 0),(0,i.__decorate)([(0,l.Cb)({type:Boolean})],y.prototype,"disabled",void 0),(0,i.__decorate)([(0,l.Cb)({type:Boolean})],y.prototype,"required",void 0),y=(0,i.__decorate)([(0,l.Mo)("ha-selector-button_toggle")],y)}}]);
//# sourceMappingURL=3798.8717f72c9adeb349.js.map