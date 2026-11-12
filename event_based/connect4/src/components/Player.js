import { COLS } from '../constants';
import { bus } from '../bus';
import { useBusEvent } from '../useBusEvent';

// ---- Player ----
// The player's input. An invisible row of columns laid over the board that
// reports hovers and clicks. Whether a click becomes a move is up to TurnLogic.
//
// Listens: game:phase
// Publishes: player:column-hovered, player:column-clicked
export default function Player() {
  const { phase } = useBusEvent('game:phase', { phase: 'playing' });
  const disabled = phase !== 'playing';

  return (
    <div
      className={`player-input ${disabled ? 'player-input--disabled' : ''}`}
      onMouseLeave={() => bus.publish('player:column-hovered', { col: null })}
    >
      {Array.from({ length: COLS }, (_, col) => (
        <div
          key={col}
          className="player-column"
          role="button"
          aria-label={`Drop in column ${col + 1}`}
          onMouseEnter={() => bus.publish('player:column-hovered', { col })}
          onClick={() => bus.publish('player:column-clicked', { col })}
        />
      ))}
    </div>
  );
}
