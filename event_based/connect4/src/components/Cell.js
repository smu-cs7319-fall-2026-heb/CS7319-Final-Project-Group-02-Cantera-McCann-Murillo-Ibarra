import { useEffect, useRef } from 'react';
import { socket } from '../socket';

// Draws one slot's piece (or preview / winning highlight).
// Also emits cell events to the server's bus.
export default function Cell({ value, row, col, isWinning, isPreview, previewPlayer }) {
  const prevValue = useRef(value);
  const prevWinning = useRef(isWinning);

  // EMIT: a piece filled this cell, or the cell was cleared
  useEffect(() => {
    const prev = prevValue.current;
    prevValue.current = value;
    if (prev === value) return;

    if (value) socket.emit('cell:filled', { row, col, player: value });
    else socket.emit('cell:cleared', { row, col });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  // EMIT: this cell became part of a winning line
  useEffect(() => {
    const prev = prevWinning.current;
    prevWinning.current = isWinning;
    if (isWinning && !prev) socket.emit('cell:highlighted', { row, col, player: value });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isWinning]);

  const classes = ['cell'];
  if (value) classes.push(`cell--${value}`, 'cell--dropped');
  if (isWinning) classes.push('cell--winning');
  if (!value && isPreview) classes.push(`cell--preview-${previewPlayer}`);

  return (
    <div
      className={classes.join(' ')}
      style={{ '--drop-rows': row + 1 }}
      aria-label={value ? `${value} piece` : 'empty'}
    />
  );
}
