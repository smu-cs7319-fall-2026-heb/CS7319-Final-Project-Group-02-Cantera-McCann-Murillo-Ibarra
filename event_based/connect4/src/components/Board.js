import { useEffect, useRef, useState } from 'react';
import Cell from './Cell';
import { getDropRow, isBoardFull } from '../utils/gameLogic';
import { socket } from '../socket';

// Finds the one cell that went from empty to filled between two boards.
function findNewPiece(prev, next) {
  for (let r = 0; r < next.length; r++) {
    for (let c = 0; c < next[r].length; c++) {
      if (!prev[r][c] && next[r][c]) return { row: r, col: c, player: next[r][c] };
    }
  }
  return null;
}

const isBoardEmpty = (board) => board.every((row) => row.every((cell) => !cell));

// Renders the grid and reports clicks to `onColumnClick`.
// Also emits board events to the server's bus.
export default function Board({ board, currentPlayer, winningCells, disabled, onColumnClick }) {
  const [hoverCol, setHoverCol] = useState(null);
  const prevBoard = useRef(board);
  const previewRow = hoverCol !== null && !disabled ? getDropRow(board, hoverCol) : -1;
  const isWinning = (r, c) => winningCells.some(([wr, wc]) => wr === r && wc === c);

  // EMIT: a piece landed, the board filled up, or the board was cleared
  useEffect(() => {
    const prev = prevBoard.current;
    prevBoard.current = board;
    if (prev === board) return;

    if (isBoardEmpty(board)) {
      if (!isBoardEmpty(prev)) socket.emit('board:reset', {});
      return;
    }

    const piece = findNewPiece(prev, board);
    if (piece) socket.emit('board:piece-dropped', piece);
    if (isBoardFull(board) && winningCells.length === 0) socket.emit('board:full', {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [board]);

  // EMIT: four in a row
  useEffect(() => {
    if (winningCells.length === 0) return;
    const [r, c] = winningCells[0];
    socket.emit('board:win', { player: board[r][c], cells: winningCells });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [winningCells]);

  // EMIT: a column was clicked (or was full)
  const handleClick = (col) => {
    if (disabled) return;
    if (getDropRow(board, col) === -1) {
      socket.emit('board:column-full', { col, player: currentPlayer });
    } else {
      socket.emit('board:column-clicked', { col, player: currentPlayer });
    }
    onColumnClick(col); // keep the existing behavior for now
  };

  return (
    <div
      className={`board ${disabled ? 'board--disabled' : ''}`}
      onMouseLeave={() => setHoverCol(null)}
    >
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            className={`slot ${hoverCol === colIndex && !disabled ? 'slot--hover' : ''}`}
            onMouseEnter={() => setHoverCol(colIndex)}
            onClick={() => handleClick(colIndex)}
            role="button"
            aria-label={`Drop in column ${colIndex + 1}`}
          >
            <Cell
              value={cell}
              row={rowIndex}
              col={colIndex}
              isWinning={isWinning(rowIndex, colIndex)}
              isPreview={rowIndex === previewRow && hoverCol === colIndex}
              previewPlayer={currentPlayer}
            />
          </div>
        ))
      )}
    </div>
  );
}
