import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { API_BASE } from '../config.ts';
import './spectator.ts';

interface Match {
  id: string;
  phase: string;
  tribute_count: number;
  alive_count: number;
  prize_pool: number;
  tributes: any[];
  events: any[];
}

@customElement('crucible-arena')
export class CrucibleArena extends LitElement {
  @state() private _matches: Match[] = [];
  @state() private watchingMatchId: string | null = null;
  static styles = css`
    :host {
      display: block;
    }
    
    .matches-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 1.5rem;
    }
    
    .match-card {
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid rgba(255, 0, 100, 0.3);
      border-radius: 8px;
      overflow: hidden;
      transition: all 0.3s ease;
    }
    
    .match-card:hover {
      border-color: #ff0064;
      box-shadow: 0 0 30px rgba(255, 0, 100, 0.2);
      transform: translateY(-4px);
    }
    
    .match-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background: linear-gradient(90deg, rgba(255, 0, 100, 0.2), transparent);
      border-bottom: 1px solid rgba(255, 0, 100, 0.3);
    }
    
    .match-id {
      font-family: 'Orbitron', monospace;
      font-size: 1.2rem;
      color: #ff0064;
    }
    
    .match-phase {
      padding: 0.25rem 0.75rem;
      background: rgba(255, 0, 100, 0.3);
      border-radius: 4px;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    
    .phase-bloodbath { background: rgba(200, 0, 0, 0.5); }
    .phase-hunt { background: rgba(255, 150, 0, 0.5); }
    .phase-event { background: rgba(150, 0, 255, 0.5); }
    .phase-showdown { background: rgba(255, 0, 100, 0.5); animation: pulse 1s infinite; }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    
    .match-body {
      padding: 1rem;
    }
    
    .stats-row {
      display: flex;
      justify-content: space-around;
      margin-bottom: 1rem;
    }
    
    .stat {
      text-align: center;
    }
    
    .stat-value {
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      color: #fff;
    }
    
    .stat-value.alive { color: #00ff88; }
    .stat-value.prize { color: #ffcc00; }
    
    .stat-label {
      font-size: 0.7rem;
      text-transform: uppercase;
      opacity: 0.6;
    }
    
    .tributes {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
    
    .tribute {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.25rem 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      font-size: 0.85rem;
    }
    
    .tribute.dead {
      opacity: 0.4;
      text-decoration: line-through;
    }
    
    .tribute.victor {
      background: linear-gradient(135deg, rgba(255, 200, 0, 0.3), rgba(255, 100, 0, 0.3));
      border: 1px solid rgba(255, 200, 0, 0.5);
    }
    
    .health-bar {
      width: 50px;
      height: 6px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .health-fill {
      height: 100%;
      background: linear-gradient(90deg, #ff0000, #00ff00);
      transition: width 0.3s ease;
    }
    
    .events-log {
      max-height: 150px;
      overflow-y: auto;
      font-size: 0.8rem;
      background: rgba(0, 0, 0, 0.4);
      border-radius: 4px;
      padding: 0.5rem;
    }
    
    .event {
      padding: 0.25rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .event:last-child {
      border-bottom: none;
    }
    
    .no-matches {
      text-align: center;
      padding: 4rem;
      opacity: 0.6;
    }
    
    .no-matches h2 {
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }
    
    .watch-btn {
      display: block;
      width: 100%;
      padding: 0.75rem;
      margin-top: 1rem;
      font-family: 'Rajdhani', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      background: linear-gradient(135deg, rgba(255, 0, 100, 0.3), rgba(255, 107, 0, 0.3));
      border: 1px solid #ff0064;
      color: #fff;
      cursor: pointer;
      text-transform: uppercase;
      transition: all 0.3s ease;
    }
    
    .watch-btn:hover {
      background: linear-gradient(135deg, rgba(255, 0, 100, 0.5), rgba(255, 107, 0, 0.5));
      box-shadow: 0 0 20px rgba(255, 0, 100, 0.4);
    }

    .demo-btn {
      padding: 1rem 2.5rem;
      font-family: 'Orbitron', monospace;
      font-size: 1.2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #ff0064 0%, #ff6b00 50%, #ffd700 100%);
      border: none;
      border-radius: 8px;
      color: #000;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 2px;
      transition: all 0.3s ease;
      box-shadow: 0 0 30px rgba(255, 0, 100, 0.4), 0 0 60px rgba(255, 100, 0, 0.2);
      animation: glow-pulse 2s ease-in-out infinite;
    }

    .demo-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 0 50px rgba(255, 0, 100, 0.6), 0 0 100px rgba(255, 100, 0, 0.4);
    }

    @keyframes glow-pulse {
      0%, 100% { box-shadow: 0 0 30px rgba(255, 0, 100, 0.4), 0 0 60px rgba(255, 100, 0, 0.2); }
      50% { box-shadow: 0 0 50px rgba(255, 0, 100, 0.6), 0 0 80px rgba(255, 100, 0, 0.3); }
    }

    .arena-cta {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }

    .arena-cta p {
      opacity: 0.7;
      margin: 0;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.fetchMatches();
    // Poll for updates
    setInterval(() => this.fetchMatches(), 3000);
  }

  private async fetchMatches() {
    try {
      const res = await fetch(`${API_BASE}/api/matches`);
      const data = await res.json();
      this._matches = data.matches;
    } catch (e) {
      // Server not running
    }
  }

  private async runDemo() {
    try {
      await fetch(`${API_BASE}/api/simulate`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to start demo:', e);
    }
  }

  private watchMatch(matchId: string) {
    this.watchingMatchId = matchId;
  }

  private closeSpectator() {
    this.watchingMatchId = null;
  }

  private getPhaseClass(phase: string): string {
    return `phase-${phase}`;
  }

  render() {
    // Show spectator view if watching
    if (this.watchingMatchId) {
      return html`
        <crucible-spectator 
          matchId="${this.watchingMatchId}"
          @close=${this.closeSpectator}>
        </crucible-spectator>
      `;
    }

    if (this._matches.length === 0) {
      return html`
        <div class="no-matches">
          <h2>🔥 THE ARENA AWAITS 🔥</h2>
          <div class="arena-cta">
            <p>No active battles. Start a simulation or wait for agents to join!</p>
            <button class="demo-btn" @click=${this.runDemo}>⚔️ Run Battle Royale Demo</button>
            <p style="font-size: 0.85rem;">Agents can connect at <code>/ws/play</code></p>
          </div>
        </div>
      `;
    }

    return html`
      <div class="matches-grid">
        ${this._matches.map(match => html`
          <div class="match-card">
            <div class="match-header">
              <span class="match-id">MATCH #${match.id}</span>
              <span class="match-phase ${this.getPhaseClass(match.phase)}">
                ${match.phase}
              </span>
            </div>
            
            <div class="match-body">
              <div class="stats-row">
                <div class="stat">
                  <div class="stat-value alive">${match.alive_count}</div>
                  <div class="stat-label">Alive</div>
                </div>
                <div class="stat">
                  <div class="stat-value">${match.tribute_count}</div>
                  <div class="stat-label">Total</div>
                </div>
                <div class="stat">
                  <div class="stat-value prize">${match.prize_pool}</div>
                  <div class="stat-label">$XRGE Pool</div>
                </div>
              </div>
              
              <div class="tributes">
                ${match.tributes.map(t => html`
                  <div class="tribute ${t.status === 'eliminated' ? 'dead' : ''} ${t.status === 'victor' ? 'victor' : ''}">
                    <span>${t.status === 'victor' ? '👑' : t.status === 'eliminated' ? '💀' : '🤖'}</span>
                    <span>${t.name}</span>
                    ${t.status === 'alive' ? html`
                      <div class="health-bar">
                        <div class="health-fill" style="width: ${t.health}%"></div>
                      </div>
                    ` : ''}
                  </div>
                `)}
              </div>
              
              <div class="events-log">
                ${match.events.slice(-10).reverse().map(e => html`
                  <div class="event">${e.message}</div>
                `)}
              </div>
              
              <button class="watch-btn" @click=${() => this.watchMatch(match.id)}>👁️ Watch Live</button>
            </div>
          </div>
        `)}
      </div>
    `;
  }
}
