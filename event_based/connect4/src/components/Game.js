import { useCallback, useState } from 'react';
import { MDBCard, MDBCardBody, MDBCardHeader } from 'mdb-react-ui-kit';
import Board from './Board';
import Timer from './Timer';
import GameStatus from './GameStatus';
import GameControls from './GameControls';
import {
  PLAYERS,
  createBoard,
  getDropRow,
  placePiece,
  findWinningLine,
  isBoardFull,
  nextPlayer,
} from '../utils/gameLogic';

const INITIAL_SCORES = { red: 0, yellow: 0, draws: 0 };

export default function Game() {
  const [board, setBoard] = useState(createBoard);
  const [currentPlayer, setCurrentPlayer] = useState('red');
  const [winner, setWinner] = useState(null);
  const [winningCells, setWinningCells] = useState([]);
  const [isDraw, setIsDraw] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [notice, setNotice] = useState('');
  const [scores, setScores] = useState(INITIAL_SCORES);
  const [turnDuration, setTurnDuration] = useState(20);
  // Bumped every turn so the Timer remounts and restarts its countdown.
  const [turnId, setTurnId] = useState(0);

  const gameOver = Boolean(winner) || isDraw;

  const handleColumnClick = (col) => {
    if (gameOver || isPaused) return;
    const row = getDropRow(board, col);
    if (row === -1) {
      setNotice('That column is full, pick another one.');
      return;
    }

    const newBoard = placePiece(board, row, col, currentPlayer);
    setBoard(newBoard);
    setNotice('');

    const line = findWinningLine(newBoard, row, col);
    if (line) {
      setWinner(currentPlayer);
      setWinningCells(line);
      setScores((s) => ({ ...s, [currentPlayer]: s[currentPlayer] + 1 }));
    } else if (isBoardFull(newBoard)) {
      setIsDraw(true);
      setScores((s) => ({ ...s, draws: s.draws + 1 }));
    } else {
      setCurrentPlayer(nextPlayer);
      setTurnId((id) => id + 1);
    }
  };

  const handleTimeUp = useCallback(() => {
    setNotice(`${PLAYERS[currentPlayer].name} ran out of time! Turn skipped.`);
    setCurrentPlayer(nextPlayer);
    setTurnId((id) => id + 1);
  }, [currentPlayer]);

  const handleNewGame = () => {
    setBoard(createBoard());
    setCurrentPlayer('red');
    setWinner(null);
    setWinningCells([]);
    setIsDraw(false);
    setIsPaused(false);
    setNotice('');
    setTurnId((id) => id + 1);
  };

  const handleDurationChange = (seconds) => {
    setTurnDuration(seconds);
    setTurnId((id) => id + 1);
  };

  return (
    <MDBCard className="game-card shadow-5">
      <MDBCardHeader className="text-center">
        <h1 className="h2 mb-0">Connect Four</h1>
      </MDBCardHeader>
      <MDBCardBody>
        <GameStatus
          currentPlayer={currentPlayer}
          winner={winner}
          isDraw={isDraw}
          notice={notice}
          scores={scores}
        />
        {!gameOver && (
          <Timer
            key={turnId}
            duration={turnDuration}
            isRunning={!isPaused}
            onTimeUp={handleTimeUp}
          />
        )}
        <div className="mt-3">
          <Board
            board={board}
            currentPlayer={currentPlayer}
            winningCells={winningCells}
            disabled={gameOver || isPaused}
            onColumnClick={handleColumnClick}
          />
        </div>
        <GameControls
          isPaused={isPaused}
          gameOver={gameOver}
          turnDuration={turnDuration}
          onNewGame={handleNewGame}
          onTogglePause={() => setIsPaused((p) => !p)}
          onDurationChange={handleDurationChange}
          onResetScores={() => setScores(INITIAL_SCORES)}
        />
      </MDBCardBody>
    </MDBCard>
  );
}
