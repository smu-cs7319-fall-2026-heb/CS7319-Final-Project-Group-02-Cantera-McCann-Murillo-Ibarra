import { useEffect } from 'react';
import { MDBBtn, MDBBtnGroup, MDBCard, MDBCardBody, MDBCardHeader } from 'mdb-react-ui-kit';
import StatusArtist from './StatusArtist';
import Clock from './Clock';
import BoardArtist from './BoardArtist';
import Player from './Player';
import { bus } from '../bus';
import { useBusEvent } from '../useBusEvent';

const DURATIONS = [10, 20, 30];

// ---- WindowingManager ----
// Lays out the window and owns the window-level controls (new game, pause,
// scores, turn length). It announces itself on open so every logic
// component sends its current state.
//
// Listens: game:phase, clock:configured, metrics:updated
// Publishes: window:opened, window:new-game, window:pause, window:resume,
//            window:reset-scores, window:duration-changed
export default function WindowingManager() {
  const { phase } = useBusEvent('game:phase', { phase: 'playing' });
  const { duration } = useBusEvent('clock:configured', { duration: 20 });
  const metrics = useBusEvent('metrics:updated', { gamesPlayed: 0, moves: 0, timeouts: 0 });

  useEffect(() => {
    bus.publish('window:opened');
  }, []);

  const isPaused = phase === 'paused';
  const gameOver = phase === 'over';

  return (
    <MDBCard className="game-card shadow-5">
      <MDBCardHeader className="text-center">
        <h1 className="h2 mb-0">Connect Four</h1>
      </MDBCardHeader>
      <MDBCardBody>
        <StatusArtist />
        {!gameOver && <Clock />}
        <div className="board-window mt-3">
          <BoardArtist />
          <Player />
        </div>

        <div className="d-flex flex-wrap justify-content-center align-items-center gap-2 mt-3">
          <MDBBtn color="primary" onClick={() => bus.publish('window:new-game')}>
            New Game
          </MDBBtn>
          <MDBBtn
            color="secondary"
            onClick={() => bus.publish(isPaused ? 'window:resume' : 'window:pause')}
            disabled={gameOver}
          >
            {isPaused ? 'Resume' : 'Pause'}
          </MDBBtn>
          <MDBBtn color="light" onClick={() => bus.publish('window:reset-scores')}>
            Reset Scores
          </MDBBtn>
          <MDBBtnGroup aria-label="Turn length">
            {DURATIONS.map((seconds) => (
              <MDBBtn
                key={seconds}
                color={duration === seconds ? 'dark' : 'light'}
                onClick={() => bus.publish('window:duration-changed', { seconds })}
              >
                {seconds}s
              </MDBBtn>
            ))}
          </MDBBtnGroup>
        </div>

        <p className="small text-muted text-center mt-3 mb-0">
          Games played: {metrics.gamesPlayed} · Moves: {metrics.moves} · Timeouts:{' '}
          {metrics.timeouts}
        </p>
      </MDBCardBody>
    </MDBCard>
  );
}
