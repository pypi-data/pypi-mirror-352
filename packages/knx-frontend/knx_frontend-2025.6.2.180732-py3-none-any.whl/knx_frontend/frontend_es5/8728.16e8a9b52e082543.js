"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8728"],{13539:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{Bt:()=>d});a(39710);var o=a(57900),n=a(3574),s=a(43956),i=e([o]);o=(i.then?(await i)():i)[0];const l=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],d=e=>e.first_weekday===s.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,n.L)(e.language)%7:l.includes(e.first_weekday)?l.indexOf(e.first_weekday):1;r()}catch(l){r(l)}}))},60495:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{G:()=>d});var o=a(57900),n=a(28105),s=a(58713),i=e([o,s]);[o,s]=i.then?(await i)():i;const l=(0,n.Z)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),d=(e,t,a,r=!0)=>{const o=(0,s.W)(e,a,t);return r?l(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};r()}catch(l){r(l)}}))},58713:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{W:()=>h});a(87799);var o=a(7722),n=a(66233),s=a(41238),i=a(13539),l=e([i]);i=(l.then?(await l)():l)[0];const c=1e3,p=60,u=60*p;function h(e,t=Date.now(),a,r={}){const l=Object.assign(Object.assign({},g),r||{}),d=(+e-+t)/c;if(Math.abs(d)<l.second)return{value:Math.round(d),unit:"second"};const h=d/p;if(Math.abs(h)<l.minute)return{value:Math.round(h),unit:"minute"};const b=d/u;if(Math.abs(b)<l.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),y=new Date(t);v.setHours(0,0,0,0),y.setHours(0,0,0,0);const m=(0,o.j)(v,y);if(0===m)return{value:Math.round(b),unit:"hour"};if(Math.abs(m)<l.day)return{value:m,unit:"day"};const _=(0,i.Bt)(a),f=(0,n.z)(v,{weekStartsOn:_}),x=(0,n.z)(y,{weekStartsOn:_}),w=(0,s.p)(f,x);if(0===w)return{value:m,unit:"day"};if(Math.abs(w)<l.week)return{value:w,unit:"week"};const k=v.getFullYear()-y.getFullYear(),$=12*k+v.getMonth()-y.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<l.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const g={second:45,minute:45,hour:22,day:5,week:4,month:11};r()}catch(d){r(d)}}))},13965:function(e,t,a){a(26847),a(27530);var r=a(73742),o=a(59048),n=a(7616);let s,i,l,d=e=>e;class c extends o.oi{render(){return(0,o.dy)(s||(s=d`
      ${0}
      <slot></slot>
    `),this.header?(0,o.dy)(i||(i=d`<h1 class="card-header">${0}</h1>`),this.header):o.Ld)}constructor(...e){super(...e),this.raised=!1}}c.styles=(0,o.iv)(l||(l=d`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, 12px);
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: 12px 16px 16px;
      display: block;
      margin-block-start: 0px;
      margin-block-end: 0px;
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: 0px;
      margin-top: -8px;
    }

    :host ::slotted(.card-content) {
      padding: 16px;
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: 5px 16px;
    }
  `)),(0,r.__decorate)([(0,n.Cb)()],c.prototype,"header",void 0),(0,r.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0})],c.prototype,"raised",void 0),c=(0,r.__decorate)([(0,n.Mo)("ha-card")],c)},83379:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:()=>x});a(26847),a(81738),a(6989),a(27530);var o=a(73742),n=a(59048),s=a(7616),i=a(31733),l=a(77204),d=(a(51431),a(78645),a(40830),a(27341)),c=(a(72633),a(1963),e([d]));d=(c.then?(await c)():c)[0];let p,u,h,g,b,v,y,m,_=e=>e;const f="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class x extends n.oi{render(){return(0,n.dy)(p||(p=_`
      ${0}
    `),this.narrow?(0,n.dy)(u||(u=_` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),f,this.items.map((e=>e.divider?(0,n.dy)(h||(h=_`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,n.dy)(g||(g=_`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item> `),e.disabled,e.action,(0,i.$)({warning:Boolean(e.warning)}),(0,i.$)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,n.dy)(b||(b=_`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?n.Ld:e.divider?(0,n.dy)(v||(v=_`<div role="separator"></div>`)):(0,n.dy)(y||(y=_`<ha-tooltip
                      .disabled=${0}
                      .content=${0}
                    >
                      <ha-icon-button
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button>
                    </ha-tooltip>`),!e.tooltip,null!==(t=e.tooltip)&&void 0!==t?t:"",e.action,e.label,e.path,e.disabled)}))))}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[l.Qx,(0,n.iv)(m||(m=_`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,s.Cb)({attribute:!1})],x.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({type:Array})],x.prototype,"items",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean})],x.prototype,"narrow",void 0),x=(0,o.__decorate)([(0,s.Mo)("ha-icon-overflow-menu")],x),r()}catch(p){r(p)}}))},27341:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(73742),o=a(52634),n=a(62685),s=a(59048),i=a(7616),l=a(75535),d=e([o]);o=(d.then?(await d)():d)[0];let c,p=e=>e;(0,l.jx)("tooltip.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:150,easing:"ease"}}),(0,l.jx)("tooltip.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:400,easing:"ease"}});class u extends o.Z{}u.styles=[n.Z,(0,s.iv)(c||(c=p`
      :host {
        --sl-tooltip-background-color: var(--secondary-background-color);
        --sl-tooltip-color: var(--primary-text-color);
        --sl-tooltip-font-family: var(
          --ha-tooltip-font-family,
          var(--ha-font-family-body)
        );
        --sl-tooltip-font-size: var(
          --ha-tooltip-font-size,
          var(--ha-font-size-s)
        );
        --sl-tooltip-font-weight: var(
          --ha-tooltip-font-weight,
          var(--ha-font-weight-normal)
        );
        --sl-tooltip-line-height: var(
          --ha-tooltip-line-height,
          var(--ha-line-height-condensed)
        );
        --sl-tooltip-padding: 8px;
        --sl-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
        --sl-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
        --sl-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
      }
    `))],u=(0,r.__decorate)([(0,i.Mo)("ha-tooltip")],u),t()}catch(c){t(c)}}))},43956:function(e,t,a){a.d(t,{zt:()=>o,c_:()=>n,t6:()=>s,FS:()=>i,y4:()=>r});a(1455);var r=function(e){return e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none",e}({}),o=function(e){return e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24",e}({}),n=function(e){return e.local="local",e.server="server",e}({}),s=function(e){return e.language="language",e.system="system",e.DMY="DMY",e.MDY="MDY",e.YMD="YMD",e}({}),i=function(e){return e.language="language",e.monday="monday",e.tuesday="tuesday",e.wednesday="wednesday",e.thursday="thursday",e.friday="friday",e.saturday="saturday",e.sunday="sunday",e}({})},15724:function(e,t,a){a.d(t,{q:()=>d});a(40777),a(39710),a(56389),a(26847),a(70820),a(64455),a(40005),a(27530);const r=/^[v^~<>=]*?(\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+))?(?:-([\da-z\-]+(?:\.[\da-z\-]+)*))?(?:\+[\da-z\-]+(?:\.[\da-z\-]+)*)?)?)?$/i,o=e=>{if("string"!=typeof e)throw new TypeError("Invalid argument expected string");const t=e.match(r);if(!t)throw new Error(`Invalid argument not valid semver ('${e}' received)`);return t.shift(),t},n=e=>"*"===e||"x"===e||"X"===e,s=e=>{const t=parseInt(e,10);return isNaN(t)?e:t},i=(e,t)=>{if(n(e)||n(t))return 0;const[a,r]=((e,t)=>typeof e!=typeof t?[String(e),String(t)]:[e,t])(s(e),s(t));return a>r?1:a<r?-1:0},l=(e,t)=>{for(let a=0;a<Math.max(e.length,t.length);a++){const r=i(e[a]||"0",t[a]||"0");if(0!==r)return r}return 0},d=(e,t,a)=>{u(a);const r=((e,t)=>{const a=o(e),r=o(t),n=a.pop(),s=r.pop(),i=l(a,r);return 0!==i?i:n&&s?l(n.split("."),s.split(".")):n||s?n?-1:1:0})(e,t);return c[a].includes(r)},c={">":[1],">=":[0,1],"=":[0],"<=":[-1,0],"<":[-1],"!=":[-1,1]},p=Object.keys(c),u=e=>{if("string"!=typeof e)throw new TypeError("Invalid operator type, expected string but got "+typeof e);if(-1===p.indexOf(e))throw new Error(`Invalid operator, expected one of ${p.join("|")}`)}},92799:function(e,t,a){a(26847),a(44438),a(81738),a(22960),a(6989),a(93190),a(27530);var r=a(73742),o=a(59048),n=a(7616),s=a(31733),i=a(29740),l=a(38059);let d,c,p,u,h,g,b=e=>e;const v=new l.r("knx-project-tree-view");class y extends o.oi{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,a])=>{a.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:a.group_addresses}),e(a.group_ranges)}))};e(this.data.group_ranges),v.debug("ranges",this._selectableRanges)}render(){return(0,o.dy)(d||(d=b`<div class="ha-tree-view">${0}</div>`),this._recurseData(this.data.group_ranges))}_recurseData(e,t=0){const a=Object.entries(e).map((([e,a])=>{const r=Object.keys(a.group_ranges).length>0;if(!(r||a.group_addresses.length>0))return o.Ld;const n=e in this._selectableRanges,i=!!n&&this._selectableRanges[e].selected,l={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:n,"selected-range":i,"non-selected-range":n&&!i},d=(0,o.dy)(c||(c=b`<div
        class=${0}
        toggle-range=${0}
        @click=${0}
      >
        <span class="range-key">${0}</span>
        <span class="range-text">${0}</span>
      </div>`),(0,s.$)(l),n?e:o.Ld,n?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.Ld,e,a.name);if(r){const e={"root-group":0===t,"sub-group":0!==t};return(0,o.dy)(p||(p=b`<div class=${0}>
          ${0} ${0}
        </div>`),(0,s.$)(e),d,this._recurseData(a.group_ranges,t+1))}return(0,o.dy)(u||(u=b`${0}`),d)}));return(0,o.dy)(h||(h=b`${0}`),a)}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);v.debug("selection changed",e),(0,i.B)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}y.styles=(0,o.iv)(g||(g=b`
    :host {
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--card-background-color);
    }

    .ha-tree-view {
      cursor: default;
    }

    .root-group {
      margin-bottom: 8px;
    }

    .root-group > * {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .range-item {
      display: block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-size: 0.875rem;
    }

    .range-item > * {
      vertical-align: middle;
      pointer-events: none;
    }

    .range-key {
      color: var(--text-primary-color);
      font-size: 0.75rem;
      font-weight: 700;
      background-color: var(--label-badge-grey);
      border-radius: 4px;
      padding: 1px 4px;
      margin-right: 2px;
    }

    .root-range {
      padding-left: 8px;
      font-weight: 500;
      background-color: var(--secondary-background-color);

      & .range-key {
        color: var(--primary-text-color);
        background-color: var(--card-background-color);
      }
    }

    .sub-range {
      padding-left: 13px;
    }

    .selectable {
      cursor: pointer;
    }

    .selectable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    .selected-range {
      background-color: rgba(var(--rgb-primary-color), 0.12);

      & .range-key {
        background-color: var(--primary-color);
      }
    }

    .selected-range:hover {
      background-color: rgba(var(--rgb-primary-color), 0.07);
    }

    .non-selected-range {
      background-color: var(--card-background-color);
    }
  `)),(0,r.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"data",void 0),(0,r.__decorate)([(0,n.Cb)({attribute:!1})],y.prototype,"multiselect",void 0),(0,r.__decorate)([(0,n.SB)()],y.prototype,"_selectableRanges",void 0),y=(0,r.__decorate)([(0,n.Mo)("knx-project-tree-view")],y)},65793:function(e,t,a){a.d(t,{W:()=>n,f:()=>o});a(44438),a(81738),a(93190),a(56303);var r=a(24110);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,r.$w)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},n=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):"")},18988:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:()=>I});a(39710),a(26847),a(2394),a(44438),a(81738),a(93190),a(87799),a(1455),a(56303),a(56389),a(27530);var o=a(73742),n=a(59048),s=a(7616),i=a(28105),l=a(29173),d=a(86829),c=(a(62790),a(13965),a(78645),a(83379)),p=(a(32780),a(60495)),u=(a(92799),a(15724)),h=a(63279),g=a(38059),b=a(65793),v=e([d,c,p]);[d,c,p]=v.then?(await v)():v;let y,m,_,f,x,w,k,$,j,M,A,S,z=e=>e;const R="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",C="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",O=new g.r("knx-project-view"),D="3.3.0";class I extends n.oi{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){this.knx.project?this._isGroupRangeAvailable():this.knx.loadProject().then((()=>{this._isGroupRangeAvailable(),this.requestUpdate()})),(0,h.ze)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{O.error("getGroupTelegrams",e),(0,l.c)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,h.IP)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){var e,t;const a=null!==(e=null===(t=this.knx.project)||void 0===t?void 0:t.knxproject.info.xknxproject_version)&&void 0!==e?e:"0.0.0";O.debug("project version: "+a),this._groupRangeAvailable=(0,u.q)(a,D,">=")}telegram_callback(e){this._lastTelegrams=Object.assign(Object.assign({},this._lastTelegrams),{},{[e.destination]:e})}_groupAddressMenu(e){var t;const a=[];return 1===(null===(t=e.dpt)||void 0===t?void 0:t.main)&&a.push({path:C,label:"Create binary sensor",action:()=>{(0,l.c)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),a.length?(0,n.dy)(y||(y=z`
          <ha-icon-overflow-menu .hass=${0} narrow .items=${0}> </ha-icon-overflow-menu>
        `),this.hass,a):n.Ld}_getRows(e){return e.length?Object.entries(this.knx.project.knxproject.group_addresses).reduce(((t,[a,r])=>(e.includes(a)&&t.push(r),t)),[]):Object.values(this.knx.project.knxproject.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){if(!this.hass||!this.knx.project)return(0,n.dy)(m||(m=z` <hass-loading-screen></hass-loading-screen> `));const e=this._getRows(this._visibleGroupAddresses);return(0,n.dy)(_||(_=z`
      <hass-tabs-subpage
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
      >
        ${0}
      </hass-tabs-subpage>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this.knx.project.project_loaded?(0,n.dy)(f||(f=z`${0}
              <div class="sections">
                ${0}
                <ha-data-table
                  class="ga-table"
                  .hass=${0}
                  .columns=${0}
                  .data=${0}
                  .hasFab=${0}
                  .searchLabel=${0}
                  .clickable=${0}
                ></ha-data-table>
              </div>`),this.narrow&&this._groupRangeAvailable?(0,n.dy)(x||(x=z`<ha-icon-button
                    slot="toolbar-icon"
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),this.hass.localize("ui.components.related-filter-menu.filter"),R,this._toggleRangeSelector):n.Ld,this._groupRangeAvailable?(0,n.dy)(w||(w=z`
                      <knx-project-tree-view
                        .data=${0}
                        @knx-group-range-selection-changed=${0}
                      ></knx-project-tree-view>
                    `),this.knx.project.knxproject,this._visibleAddressesChanged):n.Ld,this.hass,this._columns(this.narrow,this.hass.language),e,!1,this.hass.localize("ui.components.data-table.search"),!1):(0,n.dy)(k||(k=z` <ha-card .header=${0}>
              <div class="card-content">
                <p>${0}</p>
              </div>
            </ha-card>`),this.knx.localize("attention"),this.knx.localize("project_view_upload")))}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._columns=(0,i.Z)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?(0,n.dy)($||($=z`<span style="display:inline-block;width:24px;text-align:right;"
                  >${0}</span
                >${0} `),e.dpt.main,e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""):""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=b.f.payload(t);return null==t.value?(0,n.dy)(j||(j=z`<code>${0}</code>`),a):(0,n.dy)(M||(M=z`<div title=${0}>
            ${0}
          </div>`),a,b.f.valueWithUnit(this._lastTelegrams[e.address]))}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=`${b.f.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return(0,n.dy)(A||(A=z`<div title=${0}>
            ${0}
          </div>`),a,(0,p.G)(new Date(t.timestamp),this.hass.locale))}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}I.styles=(0,n.iv)(S||(S=z`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
    .sections {
      display: flex;
      flex-direction: row;
      height: 100%;
    }

    :host([narrow]) knx-project-tree-view {
      position: absolute;
      max-width: calc(100% - 60px); /* 100% -> max 871px before not narrow */
      z-index: 1;
      right: 0;
      transition: 0.5s;
      border-left: 1px solid var(--divider-color);
    }

    :host([narrow][range-selector-hidden]) knx-project-tree-view {
      width: 0;
    }

    :host(:not([narrow])) knx-project-tree-view {
      max-width: 255px; /* min 616px - 816px for tree-view + ga-table (depending on side menu) */
    }

    .ga-table {
      flex: 1;
    }
  `)),(0,o.__decorate)([(0,s.Cb)({type:Object})],I.prototype,"hass",void 0),(0,o.__decorate)([(0,s.Cb)({attribute:!1})],I.prototype,"knx",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,reflect:!0})],I.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.Cb)({type:Object})],I.prototype,"route",void 0),(0,o.__decorate)([(0,s.Cb)({type:Array,reflect:!1})],I.prototype,"tabs",void 0),(0,o.__decorate)([(0,s.Cb)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],I.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,s.SB)()],I.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,s.SB)()],I.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,s.SB)()],I.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,s.SB)()],I.prototype,"_lastTelegrams",void 0),I=(0,o.__decorate)([(0,s.Mo)("knx-project-view")],I),r()}catch(y){r(y)}}))},33480:function(e,t,a){var r=a(77341),o=a(87494),n=a(45249),s=a(65085),i=a(36539),l=a(24894),d=a(64043),c=a(41402)("every",TypeError);r({target:"Iterator",proto:!0,real:!0,forced:c},{every:function(e){i(this);try{s(e)}catch(r){d(this,"throw",r)}if(c)return o(c,this,e);var t=l(this),a=0;return!n(t,(function(t,r){if(!e(t,a++))return r()}),{IS_RECORD:!0,INTERRUPTED:!0}).stopped}})}}]);
//# sourceMappingURL=8728.16e8a9b52e082543.js.map