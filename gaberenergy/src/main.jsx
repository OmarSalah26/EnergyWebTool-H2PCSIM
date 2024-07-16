// index.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import H2PCSimTool from './HomePage';
import PSM from './PSM/PSM';
import Polygon from './Map/polygon';
import ESN from './ESN/ESN';
import { SharedProvider } from './SharedContext';
import Login from './Login/Login';
import Register from './Login/Register';
import './index.css';
import Scenarios from './Scenarios/Scenarios';
import Collab from './Collaboration/CollabIO';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <DndProvider backend={HTML5Backend}>
      <Router>
        <SharedProvider>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/home" element={<H2PCSimTool />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/psm" element={<PSM />} />
            <Route path="/esn" element={<ESN />} />
            <Route path="/map" element={<Polygon />} />
            <Route path="/collab" element={<Collab />} />
          </Routes>
        </SharedProvider>
      </Router>
    </DndProvider>
  </React.StrictMode>
);
