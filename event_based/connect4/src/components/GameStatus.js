import { useEffect, useRef } from 'react';
import { MDBBadge } from 'mdb-react-ui-kit';
import { PLAYERS } from '../utils/gameLogic';
import { socket } from '../socket';

// Runs `onChange(value)` whenever `value` changes, but not on the first render.
function useOnChange(value, onChange) {
  const prev = useRef(value);
  useEffect(() => {
    if (prev.current === value) return;
    prev.current = value;
    onChange(value);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);
}

// Shows whose turn it is, the result, any notice, and the scoreboard.
// Also emits status events to the server's bus.
export default function GameStatus({ currentPlayer, winner, isDraw, notice, scores }) {
  // EMIT: the turn passed to the other player
  useOnChange(currentPlayer, (player) => socket.emit('status:turn-changed', { player }));

  // EMIT: a winner is shown
  useOnChange(winner, (player) => {
    if (player) socket.emit('status:winner', { player });
  });

  // EMIT: a draw is shown
  useOnChange(isDraw, (draw) => {
    if (draw) socket.emit('status:draw', {});
  });

  // EMIT: a notice message is shown
  useOnChange(notice, (message) => {
    if (message) socket.emit('status:notice', { message });
  });

  // EMIT: the scoreboard changed
  useOnChange(scores, (newScores) => socket.emit('status:scores-updated', { scores: newScores }));

  let message;
  if (winner) {
    message = (
      <span className={`text-${PLAYERS[winner].color}`}>{PLAYERS[winner].name} wins!</span>
    );
  } else if (isDraw) {
    message = <span className="text-muted">It's a draw!</span>;
  } else {
    message = (
      <span>
        <span className={`text-${PLAYERS[currentPlayer].color}`}>
          {PLAYERS[currentPlayer].name}
        </span>
        's turn
      </span>
    );
  }

  return (
    <div className="text-center mb-3">
      <h3 className="mb-2">{message}</h3>
      <p className="small text-muted mb-2" style={{ minHeight: '1.25rem' }}>
        {notice}
      </p>
      <div className="d-flex flex-wrap justify-content-center gap-2">
        {Object.entries(PLAYERS).map(([key, player]) => (
          <MDBBadge key={key} color={player.color} pill className="fs-6 px-3 py-2">
            {player.name}: {scores[key]}
          </MDBBadge>
        ))}
        <MDBBadge color="secondary" pill className="fs-6 px-3 py-2">
          Draws: {scores.draws}
        </MDBBadge>
      </div>
    </div>
  );
}
