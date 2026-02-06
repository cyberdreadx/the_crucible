import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import './arena.ts';
import './leaderboard.ts';
import './match-viewer.ts';
import './mini-games.ts';
import './docs.ts';

interface QueueStatus {
  queue_size: number;
  waiting_for: number;
  active_matches: number;
}

@customElement('crucible-app')
export class CrucibleApp extends LitElement {
  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
    }
    
    header {
      background: linear-gradient(180deg, rgba(255, 0, 100, 0.2) 0%, transparent 100%);
      padding: 2rem;
      text-align: center;
      border-bottom: 2px solid rgba(255, 0, 100, 0.5);
    }
    
    h1 {
      font-family: 'Orbitron', monospace;
      font-size: 3rem;
      font-weight: 900;
      background: linear-gradient(135deg, #ff0064 0%, #ff6b00 50%, #ff0064 100%);
      background-size: 200% auto;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: shimmer 3s linear infinite;
      text-shadow: 0 0 40px rgba(255, 0, 100, 0.5);
    }
    
    @keyframes shimmer {
      0% { background-position: 0% center; }
      100% { background-position: 200% center; }
    }
    
    .tagline {
      font-style: italic;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 0.5rem;
    }
    
    .status-bar {
      display: flex;
      justify-content: center;
      gap: 2rem;
      padding: 1rem;
      background: rgba(0, 0, 0, 0.5);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .stat-value {
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      color: #ff0064;
    }
    
    .stat-label {
      font-size: 0.8rem;
      text-transform: uppercase;
      opacity: 0.7;
    }
    
    nav {
      display: flex;
      justify-content: center;
      gap: 1rem;
      padding: 1rem;
    }
    
    nav button {
      font-family: 'Rajdhani', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      padding: 0.75rem 2rem;
      background: transparent;
      border: 2px solid rgba(255, 0, 100, 0.5);
      color: #fff;
      cursor: pointer;
      text-transform: uppercase;
      transition: all 0.3s ease;
    }
    
    nav button:hover {
      background: rgba(255, 0, 100, 0.2);
      border-color: #ff0064;
      box-shadow: 0 0 20px rgba(255, 0, 100, 0.3);
    }
    
    nav button.active {
      background: linear-gradient(135deg, rgba(255, 0, 100, 0.3), rgba(255, 107, 0, 0.3));
      border-color: #ff0064;
    }
    
    main {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .flame-border {
      position: relative;
    }
    
    .flame-border::before {
      content: '';
      position: absolute;
      top: -2px;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, transparent, #ff0064, #ff6b00, #ff0064, transparent);
      animation: flame-pulse 2s ease-in-out infinite;
    }
    
    @keyframes flame-pulse {
      0%, 100% { opacity: 0.5; }
      50% { opacity: 1; }
    }
  `;

  @state() private tab: 'arena' | 'leaderboard' | 'games' | 'docs' = 'games';
  @state() private status: QueueStatus = { queue_size: 0, waiting_for: 4, active_matches: 0 };
  @state() private spectators = 0;
  @state() private games: any[] = [];

  private ws: WebSocket | null = null;

  connectedCallback() {
    super.connectedCallback();
    this.connectWebSocket();
    this.fetchStatus();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.ws?.close();
  }

  private async fetchStatus() {
    try {
      const res = await fetch('http://localhost:8080/api/status');
      const data = await res.json();
      this.status = data.queue;
      this.spectators = data.spectators;

      // Also fetch games
      const gamesRes = await fetch('http://localhost:8080/api/games');
      const gamesData = await gamesRes.json();
      this.games = gamesData.games || [];
    } catch (e) {
      console.log('Server not running');
    }
  }

  private connectWebSocket() {
    try {
      this.ws = new WebSocket('ws://localhost:8080/ws/spectate');

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleEvent(data);
      };

      this.ws.onclose = () => {
        setTimeout(() => this.connectWebSocket(), 5000);
      };
    } catch (e) {
      console.log('WebSocket connection failed');
    }
  }

  private handleEvent(data: any) {
    console.log('Arena event:', data);
    // Update UI based on events
    if (data.type === 'init') {
      this.status = data.queue;
    }
  }

  render() {
    return html`
      <header class="flame-border">
        <h1>THE CRUCIBLE</h1>
        <p class="tagline">May the odds be ever in your favor.</p>
      </header>
      
      <div class="status-bar">
        <div class="stat">
          <span class="stat-value">${this.status.queue_size}</span>
          <span class="stat-label">In Queue</span>
        </div>
        <div class="stat">
          <span class="stat-value">${this.status.active_matches}</span>
          <span class="stat-label">Live Matches</span>
        </div>
        <div class="stat">
          <span class="stat-value">${this.spectators}</span>
          <span class="stat-label">Spectators</span>
        </div>
      </div>
      
      <nav>
        <button 
          class="${this.tab === 'arena' ? 'active' : ''}"
          @click=${() => this.tab = 'arena'}
        >
          🔥 Arena
        </button>
        <button 
          class="${this.tab === 'games' ? 'active' : ''}"
          @click=${() => this.tab = 'games'}
        >
          🎮 Games
        </button>
        <button 
          class="${this.tab === 'leaderboard' ? 'active' : ''}"
          @click=${() => this.tab = 'leaderboard'}
        >
          🏆 Leaderboard
        </button>
        <button 
          class="${this.tab === 'docs' ? 'active' : ''}"
          @click=${() => this.tab = 'docs'}
        >
          📖 Docs
        </button>
      </nav>
      
      <main>
        ${this.tab === 'arena'
        ? html`<crucible-arena></crucible-arena>`
        : this.tab === 'games'
          ? html`<mini-game-viewer></mini-game-viewer>`
          : this.tab === 'docs'
            ? html`<crucible-docs></crucible-docs>`
            : html`<crucible-leaderboard></crucible-leaderboard>`
      }
      </main>
    `;
  }
}
