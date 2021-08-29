import logo from './logo.svg';
import './App.css';

function App() {
  return (
      <div className="App">
          <div className="container">
              <div className="fill-area">fill</div>
              <div className="left-area">
                  Nalewaxpol
              </div>
              <div className="top-area">Dystrybutor płynu</div>
              <div className="payment-area">
                  <div className="dot">
                      <span className="money">
                          <span className="money-value">2</span>
                          <span className="money-currency"> PLN</span>
                      </span>
                  </div>
              </div>
              <div className="info-area">Cena litra płynu to 1024zł</div>
              <div className="button-area">button</div>
          </div>
      </div>

    // <div className="App">
    //   <div className="App-header">
    //     <img src={logo} className="App-logo" alt="logo" />
    //     <p>
    //       Dystrybutor płynu
    //     </p>
    //   </div>
    // </div>
  );
}

export default App;
