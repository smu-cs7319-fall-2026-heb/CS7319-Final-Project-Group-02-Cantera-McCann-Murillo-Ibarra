import { MDBContainer } from 'mdb-react-ui-kit';
import WindowingManager from './components/WindowingManager';
import './App.css';

function App() {
  return (
    <MDBContainer className="py-4 d-flex justify-content-center">
      <WindowingManager />
    </MDBContainer>
  );
}

export default App;
