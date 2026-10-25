import { useEffect, useRef, useState } from 'react';
import { MDBProgress, MDBProgressBar } from 'mdb-react-ui-kit';
import { socket } from '../socket';

// Counts down from `duration` seconds while `isRunning` is true and calls
// `onTimeUp` at zero. Give it a new `key` to restart the countdown.
// Also emits timer events to the server's bus.
export default function Timer({ duration, isRunning, onTimeUp }) {
  const [timeLeft, setTimeLeft] = useState(duration);
  const expiredSent = useRef(false); // make sure "expired" is only sent once

  // EMIT: the timer started or restarted (runs once per new key)
  useEffect(() => {
    socket.emit('timer:started', { duration });
  }, [duration]);

  // EMIT: paused / resumed
  useEffect(() => {
    socket.emit(isRunning ? 'timer:resumed' : 'timer:paused', { timeLeft });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isRunning]);

  useEffect(() => {
    if (!isRunning) return;
    const id = setInterval(() => setTimeLeft((t) => Math.max(t - 1, 0)), 1000);
    return () => clearInterval(id);
  }, [isRunning]);

  // EMIT: time ran out
  useEffect(() => {
    if (timeLeft === 0 && isRunning && !expiredSent.current) {
      expiredSent.current = true;
      socket.emit('timer:expired', { duration });
      onTimeUp(); // keep the existing behavior for now
    }
  }, [timeLeft, isRunning, onTimeUp, duration]);

  const percent = (timeLeft / duration) * 100;
  const barColor = percent > 50 ? 'success' : percent > 25 ? 'warning' : 'danger';

  return (
    <div className="timer">
      <div className="d-flex justify-content-between mb-1">
        <span className="fw-bold">Turn timer</span>
        <span className={`fw-bold text-${barColor}`}>
          {timeLeft}s{!isRunning && ' (paused)'}
        </span>
      </div>
      <MDBProgress height="12">
        <MDBProgressBar bgColor={barColor} width={percent} valuemin={0} valuemax={100} />
      </MDBProgress>
    </div>
  );
}