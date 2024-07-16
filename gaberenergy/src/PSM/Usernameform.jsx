import React, { useState } from 'react';
import './Usernameform.css'; // Ensure you import the new CSS

const UsernameForm = ({ onSave }) => {
  const [siteName, setSiteName] = useState('');
  const [siteType, setSiteType] = useState('residential');
  const [demand, setDemand] = useState(0);
  const [dailyConsumption, setDailyConsumption] = useState(0);
  const [surplus, setSurplus] = useState(0);
  const [numberOfOccupants, setNumberOfOccupants] = useState(0);
  const [size, setSize] = useState(0);

  const handleSave = () => {
    onSave({ siteName, siteType, demand, dailyConsumption, surplus, numberOfOccupants, size });
  };

  return (
    <div className="form-overlay">
      <div className="form-container">
        <h2>Enter Details</h2>
        
        <label htmlFor="siteName">Site Name</label>
        <input
          type="text"
          id="siteName"
          value={siteName}
          onChange={(e) => setSiteName(e.target.value)}
        />

        <label htmlFor="siteType">Site Type</label>
        <select
          id="siteType"
          value={siteType}
          onChange={(e) => setSiteType(e.target.value)}
        >
          <option value="residential">Residential</option>
          <option value="commercial">Commercial</option>
          <option value="industrial">Industrial</option>
        </select>

        <label htmlFor="demand">Demand</label>
        <input
          type="number"
          id="demand"
          value={demand}
          onChange={(e) => setDemand(e.target.value)}
        />

        <label htmlFor="dailyConsumption">Daily Consumption</label>
        <input
          type="number"
          id="dailyConsumption"
          value={dailyConsumption}
          onChange={(e) => setDailyConsumption(e.target.value)}
        />

        <label htmlFor="surplus">Surplus</label>
        <input
          type="number"
          id="surplus"
          value={surplus}
          onChange={(e) => setSurplus(e.target.value)}
        />

        <label htmlFor="numberOfOccupants">Number of Occupants</label>
        <input
          type="number"
          id="numberOfOccupants"
          value={numberOfOccupants}
          onChange={(e) => setNumberOfOccupants(e.target.value)}
        />

        <label htmlFor="size">Size (sq ft)</label>
        <input
          type="number"
          id="size"
          value={size}
          onChange={(e) => setSize(e.target.value)}
        />

        <button onClick={handleSave}>Save</button>
      </div>
    </div>
  );
};

export default UsernameForm;
