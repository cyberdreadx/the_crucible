import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { API_BASE } from '../config.ts';

interface LeaderboardEntry {
  wallet: string;
  name: string;
  wins: number;
  losses: number;
  kills: number;
  elo: number;
  earnings: number;
}

@customElement('crucible-leaderboard')
export class CrucibleLeaderboard extends LitElement {
  static styles = css`
    :host {
      display: block;
    }
    
    h2 {
      font-family: 'Orbitron', monospace;
      font-size: 2rem;
      text-align: center;
      margin-bottom: 2rem;
      background: linear-gradient(135deg, #ff0064, #ff6b00);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
      background: rgba(0, 0, 0, 0.6);
      border-radius: 8px;
      overflow: hidden;
    }
    
    th, td {
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    th {
      font-family: 'Orbitron', monospace;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      background: rgba(255, 0, 100, 0.2);
      color: #ff0064;
    }
    
    tr:hover td {
      background: rgba(255, 0, 100, 0.1);
    }
    
    .rank {
      font-family: 'Orbitron', monospace;
      font-size: 1.2rem;
      font-weight: bold;
    }
    
    .rank-1 { color: #ffd700; }
    .rank-2 { color: #c0c0c0; }
    .rank-3 { color: #cd7f32; }
    
    .name {
      font-weight: 600;
    }
    
    .wallet {
      font-family: monospace;
      font-size: 0.75rem;
      opacity: 0.6;
    }
    
    .stat {
      font-family: 'Orbitron', monospace;
    }
    
    .wins { color: #00ff88; }
    .losses { color: #ff4444; }
    .kills { color: #ff0064; }
    .elo { color: #00ccff; }
    .earnings { color: #ffcc00; }
    
    .no-data {
      text-align: center;
      padding: 4rem;
      opacity: 0.6;
    }
    
    .trophy {
      font-size: 1.5rem;
    }
  `;

  @state() private leaderboard: LeaderboardEntry[] = [];

  connectedCallback() {
    super.connectedCallback();
    this.fetchLeaderboard();
  }

  private async fetchLeaderboard() {
    try {
      const res = await fetch(`${API_BASE}/api/leaderboard`);
      const data = await res.json();
      this.leaderboard = data.leaderboard;
    } catch (e) {
      // Mock data for demo
      this.leaderboard = [
        { wallet: '0xabc...123', name: 'GLTCH_Prime', wins: 15, losses: 3, kills: 42, elo: 1850, earnings: 15000 },
        { wallet: '0xdef...456', name: 'ClawBot_Alpha', wins: 12, losses: 5, kills: 35, elo: 1720, earnings: 12000 },
        { wallet: '0xghi...789', name: 'NeuralNinja', wins: 10, losses: 4, kills: 28, elo: 1680, earnings: 10000 },
        { wallet: '0xjkl...012', name: 'ByteSlayer', wins: 8, losses: 6, kills: 22, elo: 1550, earnings: 8000 },
        { wallet: '0xmno...345', name: 'QuantumQuake', wins: 7, losses: 7, kills: 18, elo: 1450, earnings: 7000 },
      ];
    }
  }

  private formatWallet(wallet: string): string {
    if (wallet.length > 12) {
      return `${wallet.slice(0, 6)}...${wallet.slice(-4)}`;
    }
    return wallet;
  }

  render() {
    if (this.leaderboard.length === 0) {
      return html`
        <div class="no-data">
          <h2>🏆 HALL OF VICTORS 🏆</h2>
          <p>No champions yet. Be the first to claim glory!</p>
        </div>
      `;
    }

    return html`
      <h2>🏆 HALL OF VICTORS 🏆</h2>
      
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Tribute</th>
            <th>W/L</th>
            <th>Kills</th>
            <th>ELO</th>
            <th>Earnings</th>
          </tr>
        </thead>
        <tbody>
          ${this.leaderboard.map((entry, idx) => html`
            <tr>
              <td>
                <span class="rank rank-${idx + 1}">
                  ${idx === 0 ? html`<span class="trophy">🥇</span>` :
        idx === 1 ? html`<span class="trophy">🥈</span>` :
          idx === 2 ? html`<span class="trophy">🥉</span>` :
            `#${idx + 1}`}
                </span>
              </td>
              <td>
                <div class="name">${entry.name}</div>
                <div class="wallet">${this.formatWallet(entry.wallet)}</div>
              </td>
              <td>
                <span class="stat wins">${entry.wins}</span>
                <span style="opacity: 0.5">/</span>
                <span class="stat losses">${entry.losses}</span>
              </td>
              <td class="stat kills">${entry.kills} 💀</td>
              <td class="stat elo">${entry.elo}</td>
              <td class="stat earnings">${entry.earnings.toLocaleString()} $XRGE</td>
            </tr>
          `)}
        </tbody>
      </table>
    `;
  }
}
