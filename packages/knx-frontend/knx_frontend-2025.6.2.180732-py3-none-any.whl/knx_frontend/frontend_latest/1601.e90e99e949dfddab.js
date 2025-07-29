export const __webpack_ids__=["1601"];export const __webpack_modules__={67552:function(t,e,i){i.r(e),i.d(e,{HaFormOptionalActions:()=>n});var o=i(73742),a=i(59048),s=i(7616),d=i(28105),c=i(41806);i(91337),i(93795);const h=[];class n extends a.oi{async focus(){await this.updateComplete,this.renderRoot.querySelector("ha-form")?.focus()}updated(t){if(super.updated(t),t.has("data")){const t=this._displayActions??h,e=this._hiddenActions(this.schema.schema,t);this._displayActions=[...t,...e.filter((t=>t in this.data))]}}render(){const t=this._displayActions??h,e=this._displaySchema(this.schema.schema,this._displayActions??[]),i=this._hiddenActions(this.schema.schema,t),o=new Map(this.computeLabel?this.schema.schema.map((t=>[t.name,t])):[]);return a.dy`
      ${e.length>0?a.dy`
            <ha-form
              .hass=${this.hass}
              .data=${this.data}
              .schema=${e}
              .disabled=${this.disabled}
              .computeLabel=${this.computeLabel}
              .computeHelper=${this.computeHelper}
              .localizeValue=${this.localizeValue}
            ></ha-form>
          `:a.Ld}
      ${i.length>0?a.dy`
            <ha-button-menu
              @action=${this._handleAddAction}
              fixed
              @closed=${c.U}
            >
              <ha-button slot="trigger">
                ${this.localize?.("ui.components.form-optional-actions.add")||"Add interaction"}
              </ha-button>
              ${i.map((t=>{const e=o.get(t);return a.dy`
                  <ha-list-item>
                    ${this.computeLabel&&e?this.computeLabel(e):t}
                  </ha-list-item>
                `}))}
            </ha-button-menu>
          `:a.Ld}
    `}_handleAddAction(t){const e=this._hiddenActions(this.schema.schema,this._displayActions??h)[t.detail.index];this._displayActions=[...this._displayActions??[],e]}constructor(...t){super(...t),this.disabled=!1,this._hiddenActions=(0,d.Z)(((t,e)=>t.map((t=>t.name)).filter((t=>!e.includes(t))))),this._displaySchema=(0,d.Z)(((t,e)=>t.filter((t=>e.includes(t.name)))))}}n.styles=a.iv`
    :host {
      display: flex !important;
      flex-direction: column;
      gap: 24px;
    }
    :host ha-form {
      display: block;
    }
  `,(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"localize",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"data",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"schema",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],n.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],n.prototype,"localizeValue",void 0),(0,o.__decorate)([(0,s.SB)()],n.prototype,"_displayActions",void 0),n=(0,o.__decorate)([(0,s.Mo)("ha-form-optional_actions")],n)}};
//# sourceMappingURL=1601.e90e99e949dfddab.js.map