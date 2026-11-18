// Draws one slot's piece (or preview / winning highlight). Used by BoardArtist.
export default function Cell({ value, row, isWinning, isPreview, previewPlayer }) {
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
