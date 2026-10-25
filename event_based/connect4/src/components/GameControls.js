import { MDBBtn, MDBBtnGroup } from 'mdb-react-ui-kit';
import { socket } from '../socket';

const DURATIONS = [10, 20, 30];

// Buttons for new game, pause/resume, score reset and turn length.
// Also emits control events to the server's bus.
export default function GameControls({
  isPaused,
  gameOver,
  turnDuration,
  onNewGame,
  onTogglePause,
  onDurationChange,
  onResetScores,
}) {
  // EMIT: start a new game
  const handleNewGame = () => {
    socket.emit('controls:new-game', {});
    onNewGame(); // keep the existing behavior for now
  };

  // EMIT: pause or resume was pressed
  const handleTogglePause = () => {
    socket.emit(isPaused ? 'controls:resume' : 'controls:pause', {});
    onTogglePause();
  };

  // EMIT: scores were reset
  const handleResetScores = () => {
    socket.emit('controls:reset-scores', {});
    onResetScores();
  };

  // EMIT: a new turn length was picked
  const handleDurationChange = (seconds) => {
    socket.emit('controls:duration-changed', { from: turnDuration, to: seconds });
    onDurationChange(seconds);
  };

  return (
    <div className="d-flex flex-wrap justify-content-center align-items-center gap-2 mt-3">
      <MDBBtn color="primary" onClick={handleNewGame}>
        New Game
      </MDBBtn>
      <MDBBtn color="secondary" onClick={handleTogglePause} disabled={gameOver}>
        {isPaused ? 'Resume' : 'Pause'}
      </MDBBtn>
      <MDBBtn color="light" onClick={handleResetScores}>
        Reset Scores
      </MDBBtn>
      <MDBBtnGroup aria-label="Turn length">
        {DURATIONS.map((seconds) => (
          <MDBBtn
            key={seconds}
            color={turnDuration === seconds ? 'dark' : 'light'}
            onClick={() => handleDurationChange(seconds)}
          >
            {seconds}s
          </MDBBtn>
        ))}
      </MDBBtnGroup>
    </div>
  );
}
