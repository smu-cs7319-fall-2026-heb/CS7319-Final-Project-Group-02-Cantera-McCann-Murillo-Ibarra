import Cell from './Cell';
import { emptyBoard } from '../constants';
import { useBusEvent } from '../useBusEvent';

// ---- BoardArtist ----
// Draws the board exactly as Board Logic reports it, plus the hover preview.
// It holds no game state of its own.
//
// Listens: board:updated, player:column-hovered, status:report, game:phase
export default function BoardArtist() {
  const { board, winningCells } = useBusEvent('board:updated', {
    board: emptyBoard(),
    winningCells: [],
  });
  const { col: hoverCol } = useBusEvent('player:column-hovered', { col: null });
  const { currentPlayer } = useBusEvent('status:report', { currentPlayer: 'red' });
  const { phase } = useBusEvent('game:phase', { phase: 'playing' });

  const disabled = phase !== 'playing';
  const showHover = hoverCol !== null && !disabled;
  const previewRow = showHover ? board.findLastIndex((row) => !row[hoverCol]) : -1;
  const isWinning = (r, c) => winningCells.some(([wr, wc]) => wr === r && wc === c);

  return (
    <div className={`board ${disabled ? 'board--disabled' : ''}`}>
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            className={`slot ${showHover && hoverCol === colIndex ? 'slot--hover' : ''}`}
          >
            <Cell
              value={cell}
              row={rowIndex}
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
