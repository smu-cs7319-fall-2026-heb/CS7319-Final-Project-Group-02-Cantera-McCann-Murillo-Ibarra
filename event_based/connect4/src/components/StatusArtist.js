import { MDBBadge } from 'mdb-react-ui-kit';
import { PLAYERS } from '../constants';
import { useBusEvent } from '../useBusEvent';

const INITIAL_REPORT = {
  currentPlayer: 'red',
  winner: null,
  isDraw: false,
  notice: '',
  scores: { red: 0, yellow: 0, draws: 0 },
};

export default function StatusArtist() {
  const { currentPlayer, winner, isDraw, notice, scores } = useBusEvent(
    'status:report',
    INITIAL_REPORT
  );

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
