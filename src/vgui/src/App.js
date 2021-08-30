import './App.css';
import React from 'react';
import Money from "./money";
import Liquid from "./Liquid";

function App() {

  return (
      <div className="App">
          <div className="container">
              <div className="fill-area">
                  <div className="filler-container">
                      <div className="filler-bar"/>

                      <span className="filler-value">
                          <Liquid/>%
                      </span>
                  </div>
              </div>

              <div className="left-area">
                  <span className="logo">
                      Kropidexpolbud
                  </span>
              </div>

              <div className="top-area">Instrybutor płynu</div>

              <div className="payment-area">
                  <div className="dot">
                      <span className="money">
                          <span className="money-value"><Money/></span>
                          <span className="money-currency"> PLN</span>
                      </span>
                  </div>
              </div>

              <div className="info-area">
                  <div className="info-container">
                  Cena jednego litra płynu: 2 PLN
                  </div>
              </div>
              <div className="button-area">START</div>
          </div>
      </div>
  );
}

export default App;
