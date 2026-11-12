import React from 'react';
import ReactDOM from 'react-dom/client';
import 'mdb-react-ui-kit/dist/css/mdb.min.css';
import './index.css';
import App from './App';
import { bus } from './bus';
import { startLogic } from './logic';

// Start the non-visual components (Board Logic, TurnLogic, Status,
// Status Logic, Clock, Metrics) once, before anything renders.
startLogic(bus);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
