import { useEffect, useState } from 'react';
import { bus } from './bus';

export function useBusEvent(event, initial) {
  const [payload, setPayload] = useState(initial);
  useEffect(() => bus.subscribe(event, setPayload), [event]);
  return payload;
}
