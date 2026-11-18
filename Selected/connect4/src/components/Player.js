import { COLS } from '../constants';
import { bus } from '../bus';
import { useBusEvent } from '../useBusEvent';


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
          onClick={() => bus.publish('player:column-clicked', { col, clickedAt: performance.now() })}
        />
      ))}
    </div>
  );
}
