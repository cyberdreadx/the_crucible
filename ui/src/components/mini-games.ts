import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { API_BASE } from '../config.ts';

interface MiniGame {
  id: string;
  game_type: string;
  bot1: string;
  bot2: string;
  state: any;
  moves: number;
  result: any;
}

@customElement('mini-game-viewer')
export class MiniGameViewer extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding: 1rem;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    h2 {
      font-family: 'Orbitron', monospace;
      color: #ffd700;
      margin: 0;
    }

    .controls {
      display: flex;
      gap: 0.5rem;
    }

    button {
      font-family: 'Rajdhani', sans-serif;
      padding: 0.5rem 1rem;
      background: linear-gradient(135deg, rgba(255, 0, 100, 0.2), rgba(255, 107, 0, 0.2));
      border: 1px solid #ff0064;
      color: #fff;
      cursor: pointer;
      transition: all 0.3s;
    }

    button:hover {
      background: rgba(255, 0, 100, 0.4);
      box-shadow: 0 0 15px rgba(255, 0, 100, 0.3);
    }

    .games-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 1.5rem;
    }

    .game-card {
      background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(30, 20, 40, 0.8));
      border: 2px solid rgba(255, 200, 0, 0.3);
      border-radius: 12px;
      overflow: hidden;
    }

    .game-header {
      background: linear-gradient(90deg, rgba(255, 0, 100, 0.2), rgba(255, 200, 0, 0.2));
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .game-type {
      font-family: 'Orbitron', monospace;
      font-size: 0.9rem;
      color: #ffd700;
      text-transform: uppercase;
    }

    .game-status {
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
    }

    .game-status.active {
      background: rgba(0, 255, 136, 0.2);
      color: #00ff88;
    }

    .game-status.finished {
      background: rgba(255, 0, 100, 0.2);
      color: #ff0064;
    }

    .players {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem 1rem;
      background: rgba(0, 0, 0, 0.3);
    }

    .player {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .player-icon {
      font-size: 1.2rem;
    }

    .player-name {
      font-weight: 600;
    }

    .vs {
      color: #ff0064;
      font-family: 'Orbitron', monospace;
    }

    .game-board {
      padding: 1rem;
      min-height: 150px;
    }

    /* Tic-Tac-Toe Board */
    .ttt-board {
      display: grid;
      grid-template-columns: repeat(3, 50px);
      gap: 4px;
      justify-content: center;
    }

    .ttt-cell {
      width: 50px;
      height: 50px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 200, 0, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      font-weight: bold;
    }

    .ttt-cell.x { color: #00ff88; }
    .ttt-cell.o { color: #ff0064; }

    /* Chess/Checkers Board */
    .chess-board {
      font-family: monospace;
      font-size: 0.9rem;
      line-height: 1.4;
      white-space: pre;
      background: rgba(0, 0, 0, 0.3);
      padding: 0.5rem;
      border-radius: 4px;
      overflow-x: auto;
    }

    /* Math/Trivia Puzzle */
    .puzzle-display {
      text-align: center;
      padding: 1rem;
    }

    .puzzle-question {
      font-size: 1.5rem;
      font-weight: bold;
      color: #ffd700;
      margin-bottom: 0.5rem;
    }

    .puzzle-instruction {
      font-size: 0.85rem;
      opacity: 0.7;
    }

    /* RPS Display */
    .rps-display {
      text-align: center;
    }

    .rps-round {
      font-size: 1.2rem;
      margin-bottom: 0.5rem;
    }

    .rps-scores {
      display: flex;
      justify-content: center;
      gap: 2rem;
      font-size: 1.1rem;
    }

    .rps-score {
      padding: 0.5rem 1rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
    }

    /* Move log */
    .move-log {
      padding: 0.5rem 1rem;
      background: rgba(0, 0, 0, 0.4);
      max-height: 80px;
      overflow-y: auto;
      font-size: 0.8rem;
    }

    .move-item {
      padding: 0.2rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Result */
    .game-result {
      padding: 0.75rem 1rem;
      background: linear-gradient(90deg, rgba(255, 215, 0, 0.2), transparent);
      border-top: 1px solid rgba(255, 215, 0, 0.3);
      font-weight: 600;
    }

    .winner-name {
      color: #ffd700;
    }

    .no-games {
      text-align: center;
      padding: 3rem;
      opacity: 0.6;
    }
  `;

  @state() private games: MiniGame[] = [];
  @state() private leaderboard: any[] = [];

  connectedCallback() {
    super.connectedCallback();
    this.fetchGames();
    this.fetchLeaderboard();

    // Auto-start some games on load
    setTimeout(() => this.runDemo(), 1000);

    // Refresh games every 1.5 seconds
    setInterval(() => this.fetchGames(), 1500);

    // Refresh leaderboard every 5 seconds
    setInterval(() => this.fetchLeaderboard(), 5000);

    // Keep games running - start new ones when old ones finish
    setInterval(() => this.ensureActiveGames(), 8000);
  }

  private async fetchGames() {
    try {
      const res = await fetch(`${API_BASE}/api/mini-game/active`);
      const data = await res.json();
      this.games = data.games || [];
    } catch (e) {
      console.error('Failed to fetch mini-games:', e);
    }
  }

  private async fetchLeaderboard() {
    try {
      const res = await fetch(`${API_BASE}/api/leaderboard`);
      const data = await res.json();
      this.leaderboard = data.leaderboard || [];
    } catch (e) {
      console.error('Failed to fetch leaderboard:', e);
    }
  }

  private async ensureActiveGames() {
    // If less than 2 active (non-finished) games, start a new one
    const activeCount = this.games.filter(g => !g.result).length;
    if (activeCount < 2) {
      const gameTypes = ['tic_tac_toe', 'chess', 'checkers', 'math_duel', 'rock_paper_scissors', 'trivia'];
      const randomType = gameTypes[Math.floor(Math.random() * gameTypes.length)];
      await this.startGame(randomType);
    }
  }

  private async startGame(gameType: string) {
    try {
      await fetch(`${API_BASE}/api/mini-game/start/${gameType}`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to start game:', e);
    }
  }

  private async runDemo() {
    try {
      await fetch(`${API_BASE}/api/mini-game/demo`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to start demo:', e);
    }
  }

  private renderGameBoard(game: MiniGame) {
    const state = game.state;

    switch (game.game_type) {
      case 'tic_tac_toe':
        return this.renderTicTacToe(state);
      case 'chess':
      case 'checkers':
        return this.renderBoard(state);
      case 'math_duel':
        return this.renderMathPuzzle(state);
      case 'trivia':
        return this.renderTrivia(state);
      case 'rock_paper_scissors':
        return this.renderRPS(state);
      case 'number_guess':
        return this.renderNumberGuess(state);
      case 'word_chain':
        return this.renderWordChain(state);
      default:
        return html`<div class="puzzle-display">${JSON.stringify(state)}</div>`;
    }
  }

  private renderTicTacToe(state: any) {
    const board = state.board || [['', '', ''], ['', '', ''], ['', '', '']];
    return html`
      <div class="ttt-board">
        ${board.flat().map((cell: string) => html`
          <div class="ttt-cell ${cell.toLowerCase()}">${cell || ''}</div>
        `)}
      </div>
    `;
  }

  private renderBoard(state: any) {
    return html`
      <div class="chess-board">${state.board || 'Loading...'}</div>
      <div style="text-align: center; margin-top: 0.5rem; font-size: 0.85rem; opacity: 0.7;">
        Move ${state.move_count || 0}
      </div>
    `;
  }

  private renderMathPuzzle(state: any) {
    return html`
      <div class="puzzle-display">
        <div class="puzzle-question">${state.problem || '?'} = ?</div>
        <div class="puzzle-instruction">First to solve wins!</div>
        ${state.solved ? html`<div style="color: #00ff88; margin-top: 0.5rem;">✓ SOLVED!</div>` : ''}
      </div>
    `;
  }

  private renderTrivia(state: any) {
    return html`
      <div class="puzzle-display">
        <div class="puzzle-question">${state.question || 'Loading...'}</div>
        <div class="puzzle-instruction">Answer the question first!</div>
        ${state.solved ? html`<div style="color: #00ff88; margin-top: 0.5rem;">✓ ANSWERED!</div>` : ''}
      </div>
    `;
  }

  private renderRPS(state: any) {
    return html`
      <div class="rps-display">
        <div class="rps-round">Round ${state.round || 1} of 3</div>
        <div class="rps-scores">
          ${Object.entries(state.scores || {}).map(([id, score]) => html`
            <div class="rps-score">${score}</div>
          `)}
        </div>
        ${(state.waiting_for || []).length > 0 ? html`
          <div style="margin-top: 0.5rem; opacity: 0.7;">Waiting for moves...</div>
        ` : ''}
      </div>
    `;
  }

  private renderNumberGuess(state: any) {
    return html`
      <div class="puzzle-display">
        <div class="puzzle-question">Guess 1-100</div>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 0.5rem;">
          <div>P1: ${state.p1_guesses || 0} guesses</div>
          <div>P2: ${state.p2_guesses || 0} guesses</div>
        </div>
      </div>
    `;
  }

  private renderWordChain(state: any) {
    return html`
      <div class="puzzle-display">
        <div class="puzzle-question">"${state.last_word || '...'}"</div>
        <div class="puzzle-instruction">
          Say a word starting with "${(state.last_word || '').slice(-1).toUpperCase()}"
        </div>
        <div style="margin-top: 0.5rem; opacity: 0.7;">Chain: ${state.chain_length || 0}</div>
      </div>
    `;
  }

  render() {
    return html`
      <div class="header">
        <h2>🎮 Mini-Game Arena</h2>
        <div class="controls">
          <button @click=${this.runDemo}>▶️ Run Demo</button>
          <button @click=${() => this.startGame('tic_tac_toe')}>⭕ Tic-Tac-Toe</button>
          <button @click=${() => this.startGame('chess')}>♔ Chess</button>
          <button @click=${() => this.startGame('checkers')}>🔴 Checkers</button>
          <button @click=${() => this.startGame('math_duel')}>🧮 Math</button>
        </div>
      </div>

      ${this.games.length === 0 ? html`
        <div class="no-games">
          No active games. Click a button above to start one!
        </div>
      ` : html`
        <div class="games-grid">
          ${this.games.map(game => html`
            <div class="game-card">
              <div class="game-header">
                <span class="game-type">${game.game_type.replace('_', ' ')}</span>
                <span class="game-status ${game.result ? 'finished' : 'active'}">
                  ${game.result ? 'FINISHED' : 'LIVE'}
                </span>
              </div>

              <div class="players">
                <div class="player">
                  <span class="player-icon">🤖</span>
                  <span class="player-name">${game.bot1}</span>
                </div>
                <span class="vs">VS</span>
                <div class="player">
                  <span class="player-name">${game.bot2}</span>
                  <span class="player-icon">🤖</span>
                </div>
              </div>

              <div class="game-board">
                ${this.renderGameBoard(game)}
              </div>

              ${game.result ? html`
                <div class="game-result">
                  🏆 Winner: <span class="winner-name">${game.result.winner}</span>
                </div>
              ` : html`
                <div class="move-log">
                  Move ${game.moves}...
                </div>
              `}
            </div>
          `)}
        </div>
      `}
    `;
  }
}
