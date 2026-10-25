import { MDBContainer } from 'mdb-react-ui-kit';
import Game from './components/Game';
import './App.css';

function App() {
  return (
    <MDBContainer className="py-4 d-flex justify-content-center">
      <Game />
    </MDBContainer>
  );
}

export default App;
