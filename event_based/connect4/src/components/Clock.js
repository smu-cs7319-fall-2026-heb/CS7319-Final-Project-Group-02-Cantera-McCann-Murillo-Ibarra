import { MDBProgress, MDBProgressBar } from 'mdb-react-ui-kit';
import { useBusEvent } from '../useBusEvent';

// ---- Clock (display) ----
// Shows the countdown that the Clock logic (src/logic/clock.js) publishes.
//
// Listens: clock:tick
export default function Clock() {
  const { timeLeft, duration, running } = useBusEvent('clock:tick', {
    timeLeft: 20,
    duration: 20,
    running: true,
  });

  const percent = (timeLeft / duration) * 100;
  const barColor = percent > 50 ? 'success' : percent > 25 ? 'warning' : 'danger';

  return (
    <div className="timer">
      <div className="d-flex justify-content-between mb-1">
        <span className="fw-bold">Turn timer</span>
        <span className={`fw-bold text-${barColor}`}>
          {timeLeft}s{!running && ' (paused)'}
        </span>
      </div>
      <MDBProgress height="12">
        <MDBProgressBar bgColor={barColor} width={percent} valuemin={0} valuemax={100} />
      </MDBProgress>
    </div>
  );
}
