import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

interface Tribute {
  id: string;
  name: string;
  type: string;
  status: string;
  health: number;
  kills: number;
  elo: number;
  x?: number;
  y?: number;
  targetX?: number;
  targetY?: number;
  action?: string;
  actionTarget?: string;
}

@customElement('crucible-spectator')
export class CrucibleSpectator extends LitElement {
  static styles = css`
    :host {
      display: block;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, #0a0510 0%, #150a20 50%, #0a0a15 100%);
      z-index: 1000;
      overflow: hidden;
      font-family: 'Rajdhani', sans-serif;
    }

    .bg-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: 
        radial-gradient(ellipse at 20% 30%, rgba(255, 0, 100, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 70%, rgba(255, 200, 0, 0.06) 0%, transparent 50%);
      pointer-events: none;
    }

    .header {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 70px;
      background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, transparent 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 2rem;
      z-index: 100;
    }

    .title {
      font-family: 'Orbitron', monospace;
      font-size: 1.8rem;
      font-weight: 900;
      background: linear-gradient(90deg, #ffd700, #ff0064);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .phase-badge {
      padding: 0.4rem 1.2rem;
      font-family: 'Orbitron', monospace;
      font-size: 0.9rem;
      font-weight: 700;
      text-transform: uppercase;
      border: 2px solid currentColor;
      animation: pulse 2s ease-in-out infinite;
    }

    .phase-bloodbath { color: #ff3333; }
    .phase-hunt { color: #ff9500; }
    .phase-showdown { color: #ff0066; }
    .phase-complete { color: #00ff88; }

    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 15px currentColor; }
      50% { box-shadow: 0 0 30px currentColor; }
    }

    .exit-btn {
      font-family: 'Orbitron', monospace;
      padding: 0.4rem 1rem;
      background: transparent;
      border: 1px solid rgba(255, 215, 0, 0.4);
      color: #ffd700;
      cursor: pointer;
    }

    .prize {
      position: absolute;
      top: 75px;
      left: 50%;
      transform: translateX(-50%);
      text-align: center;
      z-index: 50;
    }

    .prize-amount {
      font-family: 'Orbitron', monospace;
      font-size: 2.5rem;
      font-weight: 900;
      color: #ffd700;
      text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }

    .prize-token {
      font-size: 1rem;
      color: #ff0064;
    }

    /* ARENA - Where action happens */
    .arena {
      position: absolute;
      top: 130px;
      left: 250px;
      right: 300px;
      bottom: 60px;
      background: radial-gradient(circle, rgba(255, 200, 0, 0.05) 0%, transparent 70%);
      border: 2px solid rgba(255, 200, 0, 0.2);
      border-radius: 20px;
      overflow: hidden;
    }

    .arena-grid {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: 
        linear-gradient(rgba(255, 200, 0, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 200, 0, 0.03) 1px, transparent 1px);
      background-size: 40px 40px;
    }

    /* TRIBUTE - Animated NPC */
    .tribute {
      position: absolute;
      width: 60px;
      height: 80px;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: left 0.8s ease-out, top 0.8s ease-out;
      z-index: 10;
    }

    .tribute.eliminated {
      opacity: 0.15;
      filter: grayscale(100%);
      z-index: 1;
    }

    .tribute.attacking {
      animation: attack-bounce 0.3s ease-out;
    }

    @keyframes attack-bounce {
      0% { transform: scale(1); }
      50% { transform: scale(1.3); }
      100% { transform: scale(1); }
    }

    .tribute.damaged {
      animation: damage-shake 0.3s ease-out;
    }

    @keyframes damage-shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-10px); }
      75% { transform: translateX(10px); }
    }

    .tribute.healing {
      animation: heal-glow 0.5s ease-out;
    }

    @keyframes heal-glow {
      0%, 100% { filter: brightness(1); }
      50% { filter: brightness(1.5) drop-shadow(0 0 15px #00ff88); }
    }

    .tribute.victor {
      animation: victor-glow 1s ease-in-out infinite alternate;
      z-index: 100;
    }

    @keyframes victor-glow {
      from { filter: drop-shadow(0 0 10px gold); transform: scale(1); }
      to { filter: drop-shadow(0 0 30px gold); transform: scale(1.15); }
    }

    .tribute-body {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: rgba(20, 10, 30, 0.9);
      border: 3px solid rgba(255, 200, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
    }

    .tribute-name {
      font-family: 'Orbitron', monospace;
      font-size: 0.55rem;
      margin-top: 4px;
      color: #fff;
      text-shadow: 0 0 5px black, 0 0 10px black;
      max-width: 70px;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .tribute-hp-bar {
      width: 45px;
      height: 5px;
      background: rgba(0, 0, 0, 0.7);
      border-radius: 3px;
      margin-top: 3px;
      overflow: hidden;
    }

    .tribute-hp-fill {
      height: 100%;
      background: linear-gradient(90deg, #ff3333, #ffcc00, #00ff88);
      transition: width 0.3s ease;
    }

    /* ATTACK LINE */
    .attack-line {
      position: absolute;
      height: 3px;
      background: linear-gradient(90deg, #ff0066, transparent);
      transform-origin: left center;
      animation: attack-line 0.4s ease-out forwards;
      z-index: 5;
      pointer-events: none;
    }

    @keyframes attack-line {
      0% { opacity: 1; width: 0; }
      50% { opacity: 1; width: 100%; }
      100% { opacity: 0; width: 100%; }
    }

    /* DAMAGE NUMBER */
    .damage-popup {
      position: absolute;
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      font-weight: 900;
      color: #ff3333;
      text-shadow: 0 0 10px #ff0000;
      animation: damage-float 1s ease-out forwards;
      pointer-events: none;
      z-index: 50;
    }

    .damage-popup.heal {
      color: #00ff88;
      text-shadow: 0 0 10px #00ff88;
    }

    @keyframes damage-float {
      0% { transform: translateY(0) scale(0.5); opacity: 1; }
      100% { transform: translateY(-50px) scale(1.2); opacity: 0; }
    }

    /* KILL EXPLOSION */
    .kill-explosion {
      position: absolute;
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255, 0, 0, 0.8) 0%, transparent 70%);
      animation: explode 0.6s ease-out forwards;
      pointer-events: none;
      z-index: 40;
    }

    @keyframes explode {
      0% { transform: scale(0.2); opacity: 1; }
      100% { transform: scale(3); opacity: 0; }
    }

    /* Panels */
    .panel-left {
      position: absolute;
      left: 0;
      top: 75px;
      bottom: 60px;
      width: 240px;
      background: linear-gradient(90deg, rgba(0,0,0,0.9), transparent);
      padding: 1rem;
      overflow-y: auto;
    }

    .panel-title {
      font-family: 'Orbitron', monospace;
      font-size: 0.7rem;
      letter-spacing: 2px;
      color: #ffd700;
      margin-bottom: 0.75rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid rgba(255, 215, 0, 0.2);
    }

    .tribute-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem;
      margin-bottom: 0.3rem;
      background: rgba(255, 255, 255, 0.03);
      border-left: 2px solid transparent;
      font-size: 0.75rem;
    }

    .tribute-row.alive { border-left-color: #00ff88; }
    .tribute-row.eliminated { opacity: 0.3; border-left-color: #ff3333; }

    .tribute-row-icon { font-size: 1.1rem; }
    .tribute-row-info { flex: 1; min-width: 0; }
    .tribute-row-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .tribute-row-stats { font-size: 0.6rem; opacity: 0.6; }
    .tribute-row-hp { font-family: 'Orbitron', monospace; font-size: 0.7rem; color: #00ff88; }
    .tribute-row-hp.low { color: #ff3333; }

    .panel-right {
      position: absolute;
      right: 0;
      top: 75px;
      bottom: 60px;
      width: 290px;
      background: linear-gradient(270deg, rgba(0,0,0,0.9), transparent);
      padding: 1rem;
      overflow-y: auto;
    }

    .event-item {
      padding: 0.5rem;
      margin-bottom: 0.3rem;
      background: rgba(255, 0, 100, 0.08);
      border-left: 2px solid #ff0066;
      font-size: 0.75rem;
      animation: slide-in 0.3s ease-out;
    }

    @keyframes slide-in {
      from { transform: translateX(20px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    .event-item.elimination { background: rgba(255, 0, 0, 0.15); border-left-color: #ff3333; }
    .event-item.heal { border-left-color: #00ff88; }

    .bottom-bar {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 55px;
      background: rgba(0, 0, 0, 0.9);
      border-top: 1px solid rgba(255, 215, 0, 0.2);
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 2.5rem;
    }

    .stat {
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .stat-label {
      color: rgba(255, 255, 255, 0.4);
      font-family: 'Orbitron', monospace;
      font-size: 0.6rem;
    }

    .stat-value {
      color: #ffd700;
      font-family: 'Orbitron', monospace;
      font-weight: 700;
      font-size: 0.85rem;
    }

    .alive-big {
      position: absolute;
      bottom: 70px;
      left: 1.5rem;
    }

    .alive-number {
      font-family: 'Orbitron', monospace;
      font-size: 2.5rem;
      font-weight: 900;
      color: #00ff88;
      text-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }

    .alive-label {
      font-size: 0.6rem;
      text-transform: uppercase;
      opacity: 0.6;
    }

    .announcement {
      position: absolute;
      top: 35%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-family: 'Orbitron', monospace;
      font-size: 2.5rem;
      font-weight: 900;
      text-align: center;
      color: #fff;
      text-shadow: 0 0 40px #ff0066;
      animation: announce 0.4s ease-out;
      z-index: 200;
      pointer-events: none;
    }

    @keyframes announce {
      from { transform: translate(-50%, -50%) scale(2); opacity: 0; }
      to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }

    .action-text {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-family: 'Orbitron', monospace;
      font-size: 1rem;
      color: #ff9500;
      text-shadow: 0 0 10px #ff9500;
      animation: action-fade 2s ease-out forwards;
      z-index: 30;
      pointer-events: none;
      white-space: nowrap;
    }

    @keyframes action-fade {
      0% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
      100% { opacity: 0; transform: translate(-50%, -70%) scale(0.8); }
    }
  `;

  @property({ type: String }) matchId = '';
  @state() private match: any = null;
  @state() private announcement = '';
  @state() private tributePositions: Map<string, { x: number, y: number }> = new Map();
  @state() private activeEffects: Array<{ type: string, x: number, y: number, value?: number, id: string }> = [];
  @state() private tributeAnimations: Map<string, string> = new Map();
  @state() private actionText = '';
  @state() private attackLines: Array<{ fromX: number, fromY: number, toX: number, toY: number, id: string }> = [];

  private arenaWidth = 0;
  private arenaHeight = 0;
  private lastEventCount = 0;

  connectedCallback() {
    super.connectedCallback();
    this.fetchMatch();
    setInterval(() => this.fetchMatch(), 1200);
    setInterval(() => this.randomMovement(), 2000);
  }

  private async fetchMatch() {
    try {
      const res = await fetch(`http://localhost:8080/api/match/${this.matchId}`);
      const data = await res.json();

      // Check for phase change
      if (this.match && this.match.phase !== data.phase) {
        this.showAnnouncement(this.formatPhase(data.phase));
      }

      // Check for new events
      const events = data.events || [];
      if (events.length > this.lastEventCount) {
        const newEvents = events.slice(this.lastEventCount);
        for (const event of newEvents) {
          this.processEvent(event, data.tributes);
        }
        this.lastEventCount = events.length;
      }

      // Initialize positions for new tributes
      for (const tribute of data.tributes || []) {
        if (!this.tributePositions.has(tribute.id)) {
          this.tributePositions.set(tribute.id, {
            x: 100 + Math.random() * 400,
            y: 50 + Math.random() * 300
          });
        }
      }

      this.match = data;
    } catch (e) {
      console.error('Failed to fetch:', e);
    }
  }

  private processEvent(event: any, tributes: Tribute[]) {
    const msg = event.message || '';

    if (msg.includes('hit') || msg.includes('attacked')) {
      // Extract attacker and victim names
      const match = msg.match(/(.+?) (?:hit|attacked) (.+?) for (\d+)/);
      if (match) {
        const [, attackerName, victimName, damage] = match;
        const attacker = tributes.find(t => t.name === attackerName);
        const victim = tributes.find(t => t.name === victimName);

        if (attacker && victim) {
          this.showCombat(attacker.id, victim.id, parseInt(damage));
        }
      }
    } else if (msg.includes('eliminated')) {
      const match = msg.match(/(.+?) eliminated (.+)/);
      if (match) {
        const victimName = match[2].replace('!', '');
        const victim = tributes.find(t => t.name === victimName);
        if (victim) {
          this.showKill(victim.id);
        }
      }
    } else if (msg.includes('found supplies') || msg.includes('HP')) {
      const match = msg.match(/(.+?) found supplies/);
      if (match) {
        const tributeName = match[1];
        const tribute = tributes.find(t => t.name === tributeName);
        const healMatch = msg.match(/\+(\d+)/);
        if (tribute && healMatch) {
          this.showHeal(tribute.id, parseInt(healMatch[1]));
        }
      }
    }

    // Show action text
    this.actionText = msg;
    setTimeout(() => this.actionText = '', 2500);
  }

  private showCombat(attackerId: string, victimId: string, damage: number) {
    const attackerPos = this.tributePositions.get(attackerId);
    const victimPos = this.tributePositions.get(victimId);

    if (!attackerPos || !victimPos) return;

    // Move attacker toward victim
    const dx = victimPos.x - attackerPos.x;
    const dy = victimPos.y - attackerPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const moveX = attackerPos.x + (dx / dist) * Math.min(dist - 60, 80);
    const moveY = attackerPos.y + (dy / dist) * Math.min(dist - 60, 80);

    this.tributePositions.set(attackerId, { x: moveX, y: moveY });
    this.tributePositions = new Map(this.tributePositions);

    // Attack animation
    this.tributeAnimations.set(attackerId, 'attacking');
    setTimeout(() => {
      this.tributeAnimations.set(victimId, 'damaged');
      this.tributeAnimations = new Map(this.tributeAnimations);
    }, 150);

    setTimeout(() => {
      this.tributeAnimations.delete(attackerId);
      this.tributeAnimations.delete(victimId);
      this.tributeAnimations = new Map(this.tributeAnimations);
    }, 500);

    // Attack line
    const lineId = `line-${Date.now()}`;
    this.attackLines = [...this.attackLines, {
      fromX: attackerPos.x + 25,
      fromY: attackerPos.y + 25,
      toX: victimPos.x + 25,
      toY: victimPos.y + 25,
      id: lineId
    }];
    setTimeout(() => {
      this.attackLines = this.attackLines.filter(l => l.id !== lineId);
    }, 400);

    // Damage popup
    const effectId = `effect-${Date.now()}`;
    this.activeEffects = [...this.activeEffects, {
      type: 'damage',
      x: victimPos.x + 20,
      y: victimPos.y,
      value: damage,
      id: effectId
    }];
    setTimeout(() => {
      this.activeEffects = this.activeEffects.filter(e => e.id !== effectId);
    }, 1000);
  }

  private showKill(victimId: string) {
    const pos = this.tributePositions.get(victimId);
    if (!pos) return;

    const effectId = `kill-${Date.now()}`;
    this.activeEffects = [...this.activeEffects, {
      type: 'kill',
      x: pos.x - 20,
      y: pos.y - 20,
      id: effectId
    }];
    setTimeout(() => {
      this.activeEffects = this.activeEffects.filter(e => e.id !== effectId);
    }, 600);
  }

  private showHeal(tributeId: string, amount: number) {
    const pos = this.tributePositions.get(tributeId);
    if (!pos) return;

    this.tributeAnimations.set(tributeId, 'healing');
    setTimeout(() => {
      this.tributeAnimations.delete(tributeId);
      this.tributeAnimations = new Map(this.tributeAnimations);
    }, 500);

    const effectId = `heal-${Date.now()}`;
    this.activeEffects = [...this.activeEffects, {
      type: 'heal',
      x: pos.x + 20,
      y: pos.y,
      value: amount,
      id: effectId
    }];
    setTimeout(() => {
      this.activeEffects = this.activeEffects.filter(e => e.id !== effectId);
    }, 1000);
  }

  private randomMovement() {
    if (!this.match) return;

    const alive = (this.match.tributes || []).filter((t: Tribute) => t.status === 'alive');

    // Each alive tribute wanders randomly
    for (const tribute of alive) {
      const pos = this.tributePositions.get(tribute.id);
      if (pos) {
        const newX = Math.max(20, Math.min(550, pos.x + (Math.random() - 0.5) * 80));
        const newY = Math.max(20, Math.min(350, pos.y + (Math.random() - 0.5) * 60));
        this.tributePositions.set(tribute.id, { x: newX, y: newY });
      }
    }
    this.tributePositions = new Map(this.tributePositions);
  }

  private formatPhase(phase: string): string {
    const map: Record<string, string> = {
      bloodbath: '🩸 BLOODBATH',
      hunt: '🎯 HUNT PHASE',
      showdown: '⚔️ SHOWDOWN',
      complete: '🏆 VICTOR CROWNED',
    };
    return map[phase] || phase.toUpperCase();
  }

  private showAnnouncement(text: string) {
    this.announcement = text;
    setTimeout(() => this.announcement = '', 3000);
  }

  private getIcon(type: string, status: string): string {
    if (status === 'victor') return '👑';
    if (status === 'eliminated') return '💀';
    if (type === 'gltch') return '🤖';
    if (type === 'openclaw') return '🦀';
    return '🎮';
  }

  private close() {
    this.dispatchEvent(new CustomEvent('close'));
  }

  render() {
    if (!this.match) {
      return html`<div style="display:flex;align-items:center;justify-content:center;height:100vh;color:#ffd700;font-family:Orbitron;">LOADING...</div>`;
    }

    const tributes = this.match.tributes || [];
    const events = (this.match.events || []).slice(-12).reverse();

    return html`
      <div class="bg-overlay"></div>

      <div class="header">
        <div class="title">THE CRUCIBLE</div>
        <span class="phase-badge phase-${this.match.phase}">${this.match.phase?.replace('_', ' ') || 'LOBBY'}</span>
        <button class="exit-btn" @click=${this.close}>EXIT</button>
      </div>

      <div class="prize">
        <div class="prize-amount">${this.match.prize_pool?.toLocaleString() || 0}<span class="prize-token"> $XRGE</span></div>
      </div>

      <!-- ARENA with moving tributes -->
      <div class="arena">
        <div class="arena-grid"></div>
        
        <!-- Attack lines -->
        ${this.attackLines.map(line => {
      const dx = line.toX - line.fromX;
      const dy = line.toY - line.fromY;
      const length = Math.sqrt(dx * dx + dy * dy);
      const angle = Math.atan2(dy, dx) * 180 / Math.PI;
      return html`
            <div class="attack-line" style="
              left: ${line.fromX}px;
              top: ${line.fromY}px;
              width: ${length}px;
              transform: rotate(${angle}deg);
            "></div>
          `;
    })}
        
        <!-- Tributes that move! -->
        ${tributes.map((t: Tribute) => {
      const pos = this.tributePositions.get(t.id) || { x: 200, y: 150 };
      const anim = this.tributeAnimations.get(t.id) || '';
      return html`
            <div class="tribute ${t.status} ${anim}" style="left: ${pos.x}px; top: ${pos.y}px;">
              <div class="tribute-body">${this.getIcon(t.type, t.status)}</div>
              <span class="tribute-name">${t.name}</span>
              ${t.status === 'alive' ? html`
                <div class="tribute-hp-bar">
                  <div class="tribute-hp-fill" style="width: ${t.health}%"></div>
                </div>
              ` : ''}
            </div>
          `;
    })}
        
        <!-- Effects (damage numbers, explosions) -->
        ${this.activeEffects.map(effect => {
      if (effect.type === 'damage') {
        return html`<div class="damage-popup" style="left: ${effect.x}px; top: ${effect.y}px;">-${effect.value}</div>`;
      } else if (effect.type === 'heal') {
        return html`<div class="damage-popup heal" style="left: ${effect.x}px; top: ${effect.y}px;">+${effect.value}</div>`;
      } else if (effect.type === 'kill') {
        return html`<div class="kill-explosion" style="left: ${effect.x}px; top: ${effect.y}px;"></div>`;
      }
      return '';
    })}
        
        <!-- Action text -->
        ${this.actionText ? html`<div class="action-text">${this.actionText}</div>` : ''}
      </div>

      <div class="panel-left">
        <div class="panel-title">⚔️ TRIBUTES</div>
        ${tributes.map((t: Tribute) => html`
          <div class="tribute-row ${t.status}">
            <span class="tribute-row-icon">${this.getIcon(t.type, t.status)}</span>
            <div class="tribute-row-info">
              <div class="tribute-row-name">${t.name}</div>
              <div class="tribute-row-stats">Kills: ${t.kills || 0}</div>
            </div>
            ${t.status === 'alive' ? html`
              <span class="tribute-row-hp ${t.health < 30 ? 'low' : ''}">${t.health}%</span>
            ` : ''}
          </div>
        `)}
      </div>

      <div class="panel-right">
        <div class="panel-title">💀 COMBAT LOG</div>
        ${events.map((e: any) => html`
          <div class="event-item ${e.type}">${e.message}</div>
        `)}
      </div>

      <div class="alive-big">
        <div class="alive-number">${this.match.alive_count || 0}</div>
        <div class="alive-label">REMAINING</div>
      </div>

      <div class="bottom-bar">
        <div class="stat"><span class="stat-label">MATCH</span><span class="stat-value">#${this.match.id}</span></div>
        <div class="stat"><span class="stat-label">POOL</span><span class="stat-value">${this.match.prize_pool} $XRGE</span></div>
        <div class="stat"><span class="stat-label">TRIBUTES</span><span class="stat-value">${tributes.length}</span></div>
        <div class="stat"><span class="stat-label">FALLEN</span><span class="stat-value" style="color:#ff3333">${tributes.length - (this.match.alive_count || 0)}</span></div>
      </div>

      ${this.announcement ? html`<div class="announcement">${this.announcement}</div>` : ''}
    `;
  }
}
