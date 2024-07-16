import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import H2PCSim from '/H2PCSS.png';
import BackgroundImage from '/Hydrogen-header.webp'; // Adjust this path as necessary
import axios from 'axios';

const H2PCSimTool = () => {
  const [selectedModule, setSelectedModule] = useState('PSM');
  const navigate = useNavigate();

  const modules = ['PSM', 'ESN', 'Map', 'Etc'];

  const handleModuleClick = (module) => {
    setSelectedModule(module);
  };

  const handleConfirmSelection = () => {
    switch (selectedModule) {
      case 'PSM':
        navigate('/psm');
        break;
      case 'ESN':
        navigate('/esn');
        break;
      case 'Map':
        navigate('/map');
        break;
      case 'Etc':
        navigate('/etc');
        break;
      default:
        break;
    }
  };

  const moduleDetails = {
    PSM: 'Used to define the Energy Flow Diagrams for various physical models.',
    ESN: 'Used to visualize the Energy Semantic Network, and display all related components.',
    Map: 'Used to plot physical models across the region.',
    Etc: 'Etc includes additional functionalities and tools.'
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <header className="bg-white shadow-md py-4">
        <div className="container mx-auto px-6 flex items-center justify-between">
          <img src={H2PCSim} alt="Company Logo" className="h-16 w-auto" />
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center">
        <div className="relative w-full h-80">
          <img src={BackgroundImage} alt="Background" className="w-full h-full object-cover" />
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <h1 className="text-4xl text-white font-bold">Welcome to the H2PCSim Tool!</h1>
          </div>
        </div>
        <div className="container mx-auto px-6 py-10 pb-2 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <h2 className="text-2xl font-bold mb-3 text-blue-600">About Us</h2>
            <p className="text-lg text-gray-700">
              We are a dedicated team focused on providing the best simulation tools for hydrogen power systems. (Placeholder for now)
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <h2 className="text-2xl font-bold mb-3 text-blue-600">Purpose</h2>
            <p className="text-lg text-gray-700">
              Place holder for now. Will be updated with more information.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
            <h2 className="text-2xl font-bold mb-3 text-blue-600">Contact Us</h2>
            <p className="text-lg text-gray-700">
              For inquiries, please email us at contact@h2pcsim.com or call us at 123-456-7890. (Placeholder for now)
            </p>
          </div>
        </div>
        <div className="container mx-auto px-6 py-6">
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition text-center">
            <h3 className="text-2xl font-bold mb-3 text-blue-600">Selected Module: {selectedModule}</h3>
            <p className="text-lg text-gray-700">{moduleDetails[selectedModule]}</p>
          </div>
        </div>
        <div className="container mx-auto px-6 py-6 pt-2 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((module) => (
            <button
              key={module}
              className={`px-4 py-2 rounded-md text-lg font-semibold text-white transition ${
                selectedModule === module ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
              }`}
              onClick={() => handleModuleClick(module)}
            >
              {module}
            </button>
          ))}
        </div>
        <div className="container mx-auto px-6 py-6 pt-2 text-center">
          <button
            className="px-4 py-2 rounded-md text-lg font-semibold text-white bg-green-600 hover:bg-green-700 transition"
            onClick={handleConfirmSelection}
          >
            Confirm Selection
          </button>
        </div>
      </main>
      <footer className="bg-gray-800 text-white py-4">
        <div className="container mx-auto px-6 text-center">
          <p>Developed by Dr.Hossam Gaber and Team</p>
        </div>
      </footer>
    </div>
  );
};

export default H2PCSimTool;
