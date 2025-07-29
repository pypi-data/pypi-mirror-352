"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2296"],{6184:function(e,i,t){t.r(i);t(26847),t(87799),t(27530);var a=t(73742),s=t(59048),o=t(7616),l=t(29740),n=(t(86932),t(4820),t(38573),t(77204));let r,h,u=e=>e;class d extends s.oi{set item(e){var i,t,a,s,o;(this._item=e,e)?(this._name=e.name||"",this._icon=e.icon||"",this._maximum=null!==(i=e.maximum)&&void 0!==i?i:void 0,this._minimum=null!==(t=e.minimum)&&void 0!==t?t:void 0,this._restore=null===(a=e.restore)||void 0===a||a,this._step=null!==(s=e.step)&&void 0!==s?s:1,this._initial=null!==(o=e.initial)&&void 0!==o?o:0):(this._name="",this._icon="",this._maximum=void 0,this._minimum=void 0,this._restore=!0,this._step=1,this._initial=0)}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,s.dy)(r||(r=u`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-expansion-panel
          header=${0}
          outlined
        >
          <ha-textfield
            .value=${0}
            .configValue=${0}
            type="number"
            @input=${0}
            .label=${0}
          ></ha-textfield>
          <div class="row">
            <ha-switch
              .checked=${0}
              .configValue=${0}
              @change=${0}
            >
            </ha-switch>
            <div>
              ${0}
            </div>
          </div>
        </ha-expansion-panel>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this._minimum,"minimum",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.minimum"),this._maximum,"maximum",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.maximum"),this._initial,"initial",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.initial"),this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings"),this._step,"step",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.step"),this._restore,"restore",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.restore")):s.Ld}_valueChanged(e){var i;if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target,a=t.configValue,s="number"===t.type?""!==t.value?Number(t.value):void 0:"ha-switch"===t.localName?e.target.checked:(null===(i=e.detail)||void 0===i?void 0:i.value)||t.value;if(this[`_${a}`]===s)return;const o=Object.assign({},this._item);void 0===s||""===s?delete o[a]:o[a]=s,(0,l.B)(this,"value-changed",{value:o})}static get styles(){return[n.Qx,(0,s.iv)(h||(h=u`
        .form {
          color: var(--primary-text-color);
        }
        .row {
          margin-top: 12px;
          margin-bottom: 12px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .row div {
          margin-left: 16px;
          margin-inline-start: 16px;
          margin-inline-end: initial;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],d.prototype,"new",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_name",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_icon",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_maximum",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_minimum",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_restore",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_initial",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_step",void 0),d=(0,a.__decorate)([(0,o.Mo)("ha-counter-form")],d)}}]);
//# sourceMappingURL=2296.bd6043c28d65f53f.js.map