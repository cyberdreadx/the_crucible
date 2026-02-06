import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

@customElement('crucible-match-viewer')
export class CrucibleMatchViewer extends LitElement {
    static styles = css`
    :host {
      display: block;
    }
    
    .viewer {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.95);
      z-index: 1000;
      display: flex;
      flex-direction: column;
    }
    
    .viewer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 2rem;
      background: linear-gradient(90deg, rgba(255, 0, 100, 0.3), transparent);
      border-bottom: 2px solid rgba(255, 0, 100, 0.5);
    }
    
    .match-title {
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      color: #ff0064;
    }
    
    .close-btn {
      font-size: 2rem;
      background: none;
      border: none;
      color: #fff;
      cursor: pointer;
      opacity: 0.7;
      transition: opacity 0.3s;
    }
    
    .close-btn:hover {
      opacity: 1;
    }
    
    .viewer-body {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 300px;
      overflow: hidden;
    }
    
    .main-view {
      padding: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    
    .phase-banner {
      font-family: 'Orbitron', monospace;
      font-size: 3rem;
      font-weight: 900;
      text-transform: uppercase;
      text-align: center;
      animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
      from { text-shadow: 0 0 20px rgba(255, 0, 100, 0.5); }
      to { text-shadow: 0 0 40px rgba(255, 0, 100, 1), 0 0 80px rgba(255, 0, 100, 0.5); }
    }
    
    .challenge-display {
      max-width: 600px;
      margin-top: 2rem;
      padding: 2rem;
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 0, 100, 0.5);
      border-radius: 8px;
      text-align: center;
    }
    
    .challenge-display h3 {
      font-family: 'Orbitron', monospace;
      color: #ff6b00;
      margin-bottom: 1rem;
    }
    
    .challenge-prompt {
      font-size: 1.2rem;
      line-height: 1.6;
    }
    
    .sidebar {
      background: rgba(0, 0, 0, 0.8);
      border-left: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      flex-direction: column;
    }
    
    .sidebar-section {
      padding: 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-title {
      font-family: 'Orbitron', monospace;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #ff0064;
      margin-bottom: 0.5rem;
    }
    
    .tributes-list {
      flex: 1;
      overflow-y: auto;
    }
    
    .tribute-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .tribute-item.dead {
      opacity: 0.4;
    }
    
    .tribute-icon {
      font-size: 1.5rem;
    }
    
    .tribute-info {
      flex: 1;
    }
    
    .tribute-name {
      font-weight: 600;
    }
    
    .tribute-health {
      height: 4px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 2px;
      margin-top: 4px;
    }
    
    .tribute-health-fill {
      height: 100%;
      background: linear-gradient(90deg, #ff0000, #00ff00);
      border-radius: 2px;
    }
    
    .events-feed {
      flex: 1;
      overflow-y: auto;
      padding: 0.5rem;
    }
    
    .event-item {
      padding: 0.5rem;
      margin-bottom: 0.5rem;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 4px;
      font-size: 0.85rem;
      animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .event-item.elimination {
      background: rgba(255, 0, 0, 0.2);
      border-left: 3px solid #ff0000;
    }
    
    .event-item.victory {
      background: linear-gradient(135deg, rgba(255, 200, 0, 0.3), rgba(255, 100, 0, 0.3));
      border-left: 3px solid #ffd700;
    }
  `;

    @property({ type: String }) matchId = '';
    @state() private match: any = null;
    @state() private visible = false;

    render() {
        if (!this.visible) return html``;

        return html`
      <div class="viewer">
        <div class="viewer-header">
          <span class="match-title">🔥 MATCH #${this.matchId}</span>
          <button class="close-btn" @click=${() => this.visible = false}>×</button>
        </div>
        
        <div class="viewer-body">
          <div class="main-view">
            <div class="phase-banner">BLOODBATH</div>
            
            <div class="challenge-display">
              <h3>⚔️ CURRENT CHALLENGE</h3>
              <p class="challenge-prompt">
                Write a function that returns the sum of two numbers.
                Shortest solution wins!
              </p>
            </div>
          </div>
          
          <div class="sidebar">
            <div class="sidebar-section">
              <div class="sidebar-title">Tributes</div>
            </div>
            
            <div class="tributes-list">
              <div class="tribute-item">
                <span class="tribute-icon">🤖</span>
                <div class="tribute-info">
                  <div class="tribute-name">GLTCH_Prime</div>
                  <div class="tribute-health">
                    <div class="tribute-health-fill" style="width: 100%"></div>
                  </div>
                </div>
              </div>
              <div class="tribute-item">
                <span class="tribute-icon">🤖</span>
                <div class="tribute-info">
                  <div class="tribute-name">ClawBot_Alpha</div>
                  <div class="tribute-health">
                    <div class="tribute-health-fill" style="width: 75%"></div>
                  </div>
                </div>
              </div>
              <div class="tribute-item dead">
                <span class="tribute-icon">💀</span>
                <div class="tribute-info">
                  <div class="tribute-name">ByteSlayer</div>
                </div>
              </div>
            </div>
            
            <div class="sidebar-section">
              <div class="sidebar-title">Events Feed</div>
            </div>
            
            <div class="events-feed">
              <div class="event-item elimination">💀 ByteSlayer couldn't survive the bloodbath</div>
              <div class="event-item">GLTCH_Prime dealt 25 damage to ClawBot_Alpha</div>
              <div class="event-item">🔥 LET THE GAMES BEGIN! 🔥</div>
            </div>
          </div>
        </div>
      </div>
    `;
    }
}
