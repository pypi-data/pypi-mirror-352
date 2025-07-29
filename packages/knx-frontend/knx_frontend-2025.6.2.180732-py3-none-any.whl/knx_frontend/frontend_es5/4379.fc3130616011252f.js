"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4379"],{13539:function(e,t,a){a.a(e,(async function(e,s){try{a.d(t,{Bt:()=>c});a(39710);var i=a(57900),o=a(3574),n=a(43956),r=e([i]);i=(r.then?(await r)():r)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],c=e=>e.first_weekday===n.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,o.L)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;s()}catch(l){s(l)}}))},9131:function(e,t,a){a.a(e,(async function(e,s){try{a.d(t,{Vu:()=>h,Zs:()=>g,mr:()=>c,xO:()=>_});var i=a(57900),o=a(28105),n=a(36641),r=a(13819),l=e([i,n]);[i,n]=l.then?(await l)():l;const c=(e,t,a)=>d(t,a.time_zone).format(e),d=(0,o.Z)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,r.y)(e)?"h12":"h23",timeZone:(0,n.f)(e.time_zone,t)}))),h=(e,t,a)=>u(t,a.time_zone).format(e),u=(0,o.Z)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,r.y)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,r.y)(e)?"h12":"h23",timeZone:(0,n.f)(e.time_zone,t)}))),_=(e,t,a)=>m(t,a.time_zone).format(e),m=(0,o.Z)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,r.y)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,r.y)(e)?"h12":"h23",timeZone:(0,n.f)(e.time_zone,t)}))),g=(e,t,a)=>v(t,a.time_zone).format(e),v=(0,o.Z)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,n.f)(e.time_zone,t)})));s()}catch(c){s(c)}}))},36641:function(e,t,a){a.a(e,(async function(e,s){try{a.d(t,{f:()=>u});var i,o,n,r=a(57900),l=a(43956),c=e([r]);r=(c.then?(await c)():c)[0];const d=null===(i=Intl.DateTimeFormat)||void 0===i||null===(o=(n=i.call(Intl)).resolvedOptions)||void 0===o?void 0:o.call(n).timeZone,h=null!=d?d:"UTC",u=(e,t)=>e===l.c_.local&&d?h:t;s()}catch(d){s(d)}}))},13819:function(e,t,a){a.d(t,{y:()=>o});a(39710),a(56389);var s=a(28105),i=a(43956);const o=(0,s.Z)((e=>{if(e.time_format===i.zt.language||e.time_format===i.zt.system){const t=e.time_format===i.zt.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===i.zt.am_pm}))},44516:function(e,t,a){a.a(e,(async function(e,s){try{a.r(t);a(26847),a(2394),a(81738),a(22960),a(87799),a(70820),a(1455),a(27530);var i=a(73742),o=a(65650),n=a(77704),r=a(4939),l=a(50789),c=a(57766),d=a(68226),h=a(21343),u=a(31007),_=a(59048),m=a(7616),g=a(13539),v=a(9131),y=a(13819),p=a(29740),f=(a(38573),a(9488)),b=a(43956),w=a(41631),k=a(77204),B=e([l,r,o,g,v]);[l,r,o,g,v]=B.then?(await B)():B;let O,$,S=e=>e;const z={plugins:[l.Z,r.ZP],headerToolbar:!1,initialView:"timeGridWeek",editable:!0,selectable:!0,selectMirror:!0,selectOverlap:!1,eventOverlap:!1,allDaySlot:!1,height:"parent",locales:n.Z,firstDay:1,dayHeaderFormat:{weekday:"short",month:void 0,day:void 0}};class C extends _.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._monday=e.monday||[],this._tuesday=e.tuesday||[],this._wednesday=e.wednesday||[],this._thursday=e.thursday||[],this._friday=e.friday||[],this._saturday=e.saturday||[],this._sunday=e.sunday||[]):(this._name="",this._icon="",this._monday=[],this._tuesday=[],this._wednesday=[],this._thursday=[],this._friday=[],this._saturday=[],this._sunday=[])}disconnectedCallback(){var e,t;super.disconnectedCallback(),null===(e=this.calendar)||void 0===e||e.destroy(),this.calendar=void 0,null===(t=this.renderRoot.querySelector("style[data-fullcalendar]"))||void 0===t||t.remove()}connectedCallback(){super.connectedCallback(),this.hasUpdated&&!this.calendar&&this._setupCalendar()}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,_.dy)(O||(O=S`
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
        <div id="calendar"></div>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon")):_.Ld}willUpdate(e){if(super.willUpdate(e),!this.calendar)return;(e.has("_sunday")||e.has("_monday")||e.has("_tuesday")||e.has("_wednesday")||e.has("_thursday")||e.has("_friday")||e.has("_saturday")||e.has("calendar"))&&(this.calendar.removeAllEventSources(),this.calendar.addEventSource(this._events));const t=e.get("hass");t&&t.language!==this.hass.language&&this.calendar.setOption("locale",this.hass.language)}firstUpdated(){this._setupCalendar()}_setupCalendar(){const e=Object.assign(Object.assign({},z),{},{locale:this.hass.language,firstDay:(0,g.Bt)(this.hass.locale),slotLabelFormat:{hour:"numeric",minute:void 0,hour12:(0,y.y)(this.hass.locale),meridiem:!!(0,y.y)(this.hass.locale)&&"narrow"},eventTimeFormat:{hour:(0,y.y)(this.hass.locale)?"numeric":"2-digit",minute:(0,y.y)(this.hass.locale)?"numeric":"2-digit",hour12:(0,y.y)(this.hass.locale),meridiem:!!(0,y.y)(this.hass.locale)&&"narrow"}});e.eventClick=e=>this._handleEventClick(e),e.select=e=>this._handleSelect(e),e.eventResize=e=>this._handleEventResize(e),e.eventDrop=e=>this._handleEventDrop(e),this.calendar=new o.f(this.shadowRoot.getElementById("calendar"),e),this.calendar.render()}get _events(){const e=[];for(const[t,a]of f.KY.entries())this[`_${a}`].length&&this[`_${a}`].forEach(((s,i)=>{let o=(0,c.O)(new Date,t);(0,d.x)(o,new Date,{weekStartsOn:(0,g.Bt)(this.hass.locale)})||(o=(0,h.E)(o,-7));const n=new Date(o),r=s.from.split(":");n.setHours(parseInt(r[0]),parseInt(r[1]),0,0);const l=new Date(o),u=s.to.split(":");l.setHours(parseInt(u[0]),parseInt(u[1]),0,0),e.push({id:`${a}-${i}`,start:n.toISOString(),end:l.toISOString()})}));return e}_handleSelect(e){const{start:t,end:a}=e,s=f.KY[t.getDay()],i=[...this[`_${s}`]],o=Object.assign({},this._item),n=(0,v.Zs)(a,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:b.c_.local}),this.hass.config);i.push({from:(0,v.Zs)(t,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:b.c_.local}),this.hass.config),to:(0,u.K)(t,a)&&"0:00"!==n?n:"24:00"}),o[s]=i,(0,p.B)(this,"value-changed",{value:o}),(0,u.K)(t,a)||this.calendar.unselect()}_handleEventResize(e){const{id:t,start:a,end:s}=e.event,[i,o]=t.split("-"),n=this[`_${i}`][parseInt(o)],r=Object.assign({},this._item),l=(0,v.Zs)(s,this.hass.locale,this.hass.config);r[i][o]=Object.assign(Object.assign({},r[i][o]),{},{from:n.from,to:(0,u.K)(a,s)&&"0:00"!==l?l:"24:00"}),(0,p.B)(this,"value-changed",{value:r}),(0,u.K)(a,s)||(this.requestUpdate(`_${i}`),e.revert())}_handleEventDrop(e){const{id:t,start:a,end:s}=e.event,[i,o]=t.split("-"),n=f.KY[a.getDay()],r=Object.assign({},this._item),l=(0,v.Zs)(s,this.hass.locale,this.hass.config),c=Object.assign(Object.assign({},r[i][o]),{},{from:(0,v.Zs)(a,this.hass.locale,this.hass.config),to:(0,u.K)(a,s)&&"0:00"!==l?l:"24:00"});if(n===i)r[i][o]=c;else{r[i].splice(o,1);const e=[...this[`_${n}`]];e.push(c),r[n]=e}(0,p.B)(this,"value-changed",{value:r}),(0,u.K)(a,s)||(this.requestUpdate(`_${i}`),e.revert())}async _handleEventClick(e){const[t,a]=e.event.id.split("-"),s=[...this[`_${t}`]][a];(0,w.F)(this,{block:s,updateBlock:e=>this._updateBlock(t,a,e),deleteBlock:()=>this._deleteBlock(t,a)})}_updateBlock(e,t,a){const[s,i,o]=a.from.split(":");a.from=`${s}:${i}`;const[n,r,l]=a.to.split(":");a.to=`${n}:${r}`,0===Number(n)&&0===Number(r)&&(a.to="24:00");const c=Object.assign({},this._item);c[e]=[...this._item[e]],c[e][t]=a,(0,p.B)(this,"value-changed",{value:c})}_deleteBlock(e,t){const a=[...this[`_${e}`]],s=Object.assign({},this._item);a.splice(parseInt(t),1),s[e]=a,(0,p.B)(this,"value-changed",{value:s})}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const a=e.target.configValue,s=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${a}`]===s)return;const i=Object.assign({},this._item);s?i[a]=s:delete i[a],(0,p.B)(this,"value-changed",{value:i})}static get styles(){return[k.Qx,(0,_.iv)($||($=S`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin: 8px 0;
        }

        #calendar {
          margin: 8px 0;
          height: 450px;
          width: 100%;
          -webkit-user-select: none;
          -ms-user-select: none;
          user-select: none;
          --fc-border-color: var(--divider-color);
          --fc-event-border-color: var(--divider-color);
        }

        .fc-v-event .fc-event-time {
          white-space: inherit;
        }
        .fc-theme-standard .fc-scrollgrid {
          border: 1px solid var(--divider-color);
          border-radius: var(--mdc-shape-small, 4px);
        }

        .fc-scrollgrid-section-header td {
          border: none;
        }
        :host([narrow]) .fc-scrollgrid-sync-table {
          overflow: hidden;
        }
        table.fc-scrollgrid-sync-table
          tbody
          tr:first-child
          .fc-daygrid-day-top {
          padding-top: 0;
        }
        .fc-scroller::-webkit-scrollbar {
          width: 0.4rem;
          height: 0.4rem;
        }
        .fc-scroller::-webkit-scrollbar-thumb {
          -webkit-border-radius: 4px;
          border-radius: 4px;
          background: var(--scrollbar-thumb-color);
        }
        .fc-scroller {
          overflow-y: auto;
          scrollbar-color: var(--scrollbar-thumb-color) transparent;
          scrollbar-width: thin;
        }

        .fc-timegrid-event-short .fc-event-time:after {
          content: ""; /* prevent trailing dash in half hour events since we do not have event titles */
        }

        a {
          color: inherit !important;
        }

        th.fc-col-header-cell.fc-day {
          background-color: var(--table-header-background-color);
          color: var(--primary-text-color);
          font-size: var(--ha-font-size-xs);
          font-weight: var(--ha-font-weight-bold);
          text-transform: uppercase;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,i.__decorate)([(0,m.Cb)({attribute:!1})],C.prototype,"hass",void 0),(0,i.__decorate)([(0,m.Cb)({type:Boolean})],C.prototype,"new",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_name",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_icon",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_monday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_tuesday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_wednesday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_thursday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_friday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_saturday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"_sunday",void 0),(0,i.__decorate)([(0,m.SB)()],C.prototype,"calendar",void 0),C=(0,i.__decorate)([(0,m.Mo)("ha-schedule-form")],C),s()}catch(O){s(O)}}))},41631:function(e,t,a){a.d(t,{F:()=>o});a(26847),a(1455),a(27530);var s=a(29740);const i=()=>a.e("601").then(a.bind(a,74069)),o=(e,t)=>{(0,s.B)(e,"show-dialog",{dialogTag:"dialog-schedule-block-info",dialogImport:i,dialogParams:t})}}}]);
//# sourceMappingURL=4379.fc3130616011252f.js.map