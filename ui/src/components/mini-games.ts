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
      position: relative;
    }

    /* Cyberpunk scanline overlay */
    :host::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.03) 0px,
        rgba(0, 0, 0, 0.03) 1px,
        transparent 1px,
        transparent 2px
      );
      pointer-events: none;
      z-index: 1000;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }

    h2 {
      font-family: 'Orbitron', monospace;
      color: #00f0ff;
      margin: 0;
      text-shadow: 0 0 10px #00f0ff, 0 0 20px #00f0ff;
      letter-spacing: 2px;
    }

    .controls {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    button {
      font-family: 'Rajdhani', sans-serif;
      padding: 0.6rem 1.2rem;
      background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 100, 0.15));
      border: 1px solid #00f0ff;
      color: #00f0ff;
      cursor: pointer;
      transition: all 0.3s;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 1px;
      clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
    }

    button:hover {
      background: rgba(0, 240, 255, 0.3);
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
      text-shadow: 0 0 10px #00f0ff;
    }

    .games-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 1.5rem;
    }

    .game-card {
      background: linear-gradient(135deg, rgba(0, 10, 20, 0.95), rgba(20, 0, 30, 0.95));
      border: 1px solid rgba(0, 240, 255, 0.3);
      border-radius: 4px;
      overflow: hidden;
      position: relative;
      transition: all 0.3s ease;
    }

    .game-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, #00f0ff, #ff0064, transparent);
      animation: scan 2s linear infinite;
    }

    @keyframes scan {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(100%); }
    }

    .game-card:hover {
      border-color: #00f0ff;
      box-shadow: 0 0 30px rgba(0, 240, 255, 0.2), 0 0 60px rgba(255, 0, 100, 0.1);
      transform: translateY(-2px);
    }

    .game-header {
      background: linear-gradient(90deg, rgba(0, 240, 255, 0.1), rgba(255, 0, 100, 0.1));
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(0, 240, 255, 0.2);
    }

    .game-type {
      font-family: 'Orbitron', monospace;
      font-size: 0.85rem;
      color: #00f0ff;
      text-transform: uppercase;
      letter-spacing: 2px;
      text-shadow: 0 0 5px #00f0ff;
    }

    .game-status {
      font-size: 0.75rem;
      padding: 0.25rem 0.75rem;
      border-radius: 2px;
      font-family: 'Orbitron', monospace;
    }

    .game-status.active {
      background: rgba(0, 255, 136, 0.2);
      color: #00ff88;
      border: 1px solid #00ff88;
      animation: pulse-status 1.5s ease-in-out infinite;
    }

    @keyframes pulse-status {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .game-status.finished {
      background: rgba(255, 0, 100, 0.2);
      color: #ff0064;
      border: 1px solid #ff0064;
    }

    .players {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1rem;
      background: rgba(0, 0, 0, 0.4);
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
      font-family: 'Rajdhani', sans-serif;
      color: #fff;
    }

    .vs {
      color: #ff0064;
      font-family: 'Orbitron', monospace;
      text-shadow: 0 0 10px #ff0064;
    }

    .game-board {
      padding: 1rem;
      min-height: 180px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Tic-Tac-Toe Board - Cyberpunk */
    .ttt-board {
      display: grid;
      grid-template-columns: repeat(3, 60px);
      gap: 4px;
      justify-content: center;
    }

    .ttt-cell {
      width: 60px;
      height: 60px;
      background: rgba(0, 20, 40, 0.8);
      border: 1px solid rgba(0, 240, 255, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      font-weight: bold;
    }

    .ttt-cell.x { 
      color: #00f0ff; 
      text-shadow: 0 0 15px #00f0ff;
    }
    .ttt-cell.o { 
      color: #ff0064; 
      text-shadow: 0 0 15px #ff0064;
    }

    /* Chess/Checkers Board - Real 8x8 grid */
    .chess-board-container {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .chess-grid {
      display: grid;
      grid-template-columns: repeat(8, 28px);
      grid-template-rows: repeat(8, 28px);
      border: 2px solid #00f0ff;
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
    }

    .chess-cell {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
    }

    .chess-cell.light {
      background: linear-gradient(135deg, #2a3a4a, #1a2a3a);
    }

    .chess-cell.dark {
      background: linear-gradient(135deg, #0a1520, #051015);
    }

    .chess-move-count {
      margin-top: 0.5rem;
      font-size: 0.8rem;
      color: #00f0ff;
      font-family: 'Orbitron', monospace;
    }

    /* Math/Trivia Puzzle */
    .puzzle-display {
      text-align: center;
      padding: 1rem;
    }

    .puzzle-question {
      font-size: 1.4rem;
      font-weight: bold;
      color: #ff0064;
      margin-bottom: 0.5rem;
      font-family: 'Orbitron', monospace;
      text-shadow: 0 0 10px rgba(255, 0, 100, 0.5);
    }

    .puzzle-instruction {
      font-size: 0.85rem;
      color: rgba(255, 255, 255, 0.6);
    }

    /* RPS Display */
    .rps-display {
      text-align: center;
    }

    .rps-round {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
      color: #00f0ff;
      font-family: 'Orbitron', monospace;
    }

    .rps-scores {
      display: flex;
      justify-content: center;
      gap: 2rem;
      font-size: 1.1rem;
    }

    .rps-score {
      padding: 0.5rem 1rem;
      background: rgba(0, 240, 255, 0.1);
      border: 1px solid rgba(0, 240, 255, 0.3);
      border-radius: 4px;
      font-family: 'Orbitron', monospace;
    }

    /* Move log */
    .move-log {
      padding: 0.5rem 1rem;
      background: rgba(0, 0, 0, 0.5);
      border-top: 1px solid rgba(0, 240, 255, 0.2);
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.6);
      font-family: monospace;
    }

    /* Result */
    .game-result {
      padding: 0.75rem 1rem;
      background: linear-gradient(90deg, rgba(255, 215, 0, 0.15), transparent);
      border-top: 1px solid rgba(255, 215, 0, 0.3);
      font-weight: 600;
    }

    .winner-name {
      color: #ffd700;
      text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
      font-family: 'Orbitron', monospace;
    }

    .no-games {
      text-align: center;
      padding: 3rem;
      color: rgba(255, 255, 255, 0.5);
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
    // Backend format: "  a b c d e f g h\n8 r n b q k b n r\n7 p p p p ..."
    // Each row starts with row number, then space-separated pieces
    const boardStr = state.board || '';
    const lines = boardStr.split('\n').filter((line: string) => /^\d/.test(line.trim()));

    // Map piece letters to Unicode chess symbols
    const pieceMap: { [key: string]: string } = {
      'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
      'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
      '·': '', '.': '', 'w': '⚪', 'W': '🔵', 'x': '🔴', 'X': '🟠'
    };

    // Create 8x8 grid cells
    const cells = [];
    for (let row = 0; row < 8; row++) {
      const line = lines[row] || '';
      // Split by space, skip first element (row number)
      const parts = line.trim().split(/\s+/);
      const pieces = parts.slice(1); // Remove row number

      for (let col = 0; col < 8; col++) {
        const isLight = (row + col) % 2 === 0;
        const piece = pieces[col] || '';

        cells.push(html`
          <div class="chess-cell ${isLight ? 'light' : 'dark'}">
            ${pieceMap[piece] !== undefined ? pieceMap[piece] : piece}
          </div>
        `);
      }
    }

    return html`
      <div class="chess-board-container">
        <div class="chess-grid">
          ${cells}
        </div>
        <div class="chess-move-count">Move ${state.move_count || 0}</div>
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
