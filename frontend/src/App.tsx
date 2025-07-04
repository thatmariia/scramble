import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import React from 'react';

import Home from "./pages/Home";
import Scramble from "./pages/Scramble";


const App: React.FC = () => {
  return (
    <Router> 
      <div className="App">
          <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/scramble" element={<Scramble />} />
          </Routes>
      </div>
    </Router>
  );
}


export default App;

