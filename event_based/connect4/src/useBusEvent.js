import { useEffect, useState } from 'react';
import { bus } from './bus';

// Subscribes to `event` and returns the latest payload (or `initial` until
// the first one arrives).
export function useBusEvent(event, initial) {
  const [payload, setPayload] = useState(initial);
  useEffect(() => bus.subscribe(event, setPayload), [event]);
  return payload;
}
