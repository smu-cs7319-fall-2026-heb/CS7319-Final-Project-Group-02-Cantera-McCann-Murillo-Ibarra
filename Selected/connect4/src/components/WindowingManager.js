import { useEffect } from 'react';
import { MDBBtn, MDBBtnGroup, MDBCard, MDBCardBody, MDBCardHeader } from 'mdb-react-ui-kit';
import StatusArtist from './StatusArtist';
import Clock from './Clock';
import BoardArtist from './BoardArtist';
import Player from './Player';
import { bus } from '../bus';
import { useBusEvent } from '../useBusEvent';

const DURATIONS = [10, 20, 30];

const EMPTY_STAT = { count: 0, last: null, median: null, p95: null };
const INITIAL_METRICS = {
  gamesPlayed: 0,
  moves: 0,
  timeouts: 0,
  summary: { placedMs: EMPTY_STAT, turnMs: EMPTY_STAT, winMs: EMPTY_STAT, messages: EMPTY_STAT },
};

const ms = (value) => (value === null ? '-' : `${value.toFixed(1)} ms`);
const num = (value) => (value === null ? '-' : value);

export default function WindowingManager() {
  const { phase } = useBusEvent('game:phase', { phase: 'playing' });
  const { duration } = useBusEvent('clock:configured', { duration: 20 });
  const metrics = useBusEvent('metrics:updated', INITIAL_METRICS);
  const { placedMs, turnMs, winMs, messages } = metrics.summary;

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

        <div className="small text-muted text-center mt-3">
          <div>
            Games played: {metrics.gamesPlayed} | Moves: {metrics.moves} | Timeouts:{' '}
            {metrics.timeouts}
          </div>
          <div>
            Last move: placed {ms(placedMs.last)} | turn passed {ms(turnMs.last)} |{' '}
            {num(messages.last)} messages
          </div>
          <div>
            Median ({placedMs.count} moves): placed {ms(placedMs.median)} | turn passed{' '}
            {ms(turnMs.median)} | win detected {ms(winMs.median)} | {num(messages.median)}{' '}
            messages
          </div>
        </div>
      </MDBCardBody>
    </MDBCard>
  );
}
