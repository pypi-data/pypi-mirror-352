"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["476"],{26440:function(e,t,i){i.r(t);i(26847),i(87799),i(27530);var s=i(73742),a=i(59048),o=i(7616),r=i(29740),l=(i(86776),i(74207),i(38573),i(77204));let n,h,d=e=>e;class c extends a.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._duration=e.duration||"00:00:00",this._restore=e.restore||!1):(this._name="",this._icon="",this._duration="00:00:00",this._restore=!1)}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,a.dy)(n||(n=d`
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
          .configValue=${0}
          .value=${0}
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-formfield
          .label=${0}
        >
          <ha-checkbox
            .configValue=${0}
            .checked=${0}
            @click=${0}
          >
          </ha-checkbox>
        </ha-formfield>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),"duration",this._duration,this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.timer.duration"),this.hass.localize("ui.dialogs.helper_settings.timer.restore"),"restore",this._restore,this._toggleRestore):a.Ld}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const i=e.target.configValue,s=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${i}`]===s)return;const a=Object.assign({},this._item);s?a[i]=s:delete a[i],(0,r.B)(this,"value-changed",{value:a})}_toggleRestore(){this._restore=!this._restore,(0,r.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{restore:this._restore})})}static get styles(){return[l.Qx,(0,a.iv)(h||(h=d`
        .form {
          color: var(--primary-text-color);
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,s.__decorate)([(0,o.Cb)({attribute:!1})],c.prototype,"hass",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],c.prototype,"new",void 0),(0,s.__decorate)([(0,o.SB)()],c.prototype,"_name",void 0),(0,s.__decorate)([(0,o.SB)()],c.prototype,"_icon",void 0),(0,s.__decorate)([(0,o.SB)()],c.prototype,"_duration",void 0),(0,s.__decorate)([(0,o.SB)()],c.prototype,"_restore",void 0),c=(0,s.__decorate)([(0,o.Mo)("ha-timer-form")],c)}}]);
//# sourceMappingURL=476.0cbeeb832b81c7c8.js.map