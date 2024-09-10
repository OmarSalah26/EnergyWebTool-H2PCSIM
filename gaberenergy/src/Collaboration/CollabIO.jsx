import React, { useState , useEffect} from 'react';
import Papa from 'papaparse';
import axios from 'axios';
import Chart from 'chart.js/auto';

const Collab = () => {
  const [files, setFiles] = useState({ tool1: null, tool2: null, tool3: null, tool4: null });
  const [imageUrls, setImageUrls] = useState({ tool1: '', tool2: '', tool3: '', tool4: '' });
  const [lcoe, setLcoe] = useState(null);
  const [popupContent, setPopupContent] = useState('');
  const [popupVisible, setPopupVisible] = useState(false); 
  const [userId, setUserId] = useState('');
  const [retrievedData, setRetrievedData] = useState(null);
  const [mgOpResults, setMgOpResults] = useState(null); // State for MG-Op results
  const [kpiData, setKpiData] = useState(null); // State for KPI data


  // useEffect to plot charts and display results once data is available
  useEffect(() => {
    if (mgOpResults) {
      displayResults(mgOpResults);
      plotEnergyProductionChart(mgOpResults);
      plotSurplusEnergyChart(mgOpResults);
    }

   /* if (kpiData) {
      displayKpiResults(kpiData);
    }*/
  }, [mgOpResults, kpiData]); // Runs whenever mgOpResults or kpiData changes

  const toggleDetails = (id) => {
    const element = document.getElementById(id);
    if (element.style.display === 'none') {
      element.style.display = 'table-row';
    } else {
      element.style.display = 'none';
    }
  };
  
  
  // Function to display results in a table
  const displayResults = (data) => {
    const resultsBody = document.getElementById('resultsBody');
    resultsBody.innerHTML = ''; // Clear previous results

    data.forEach(result => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${result.Hour}</td>
        <td>${result.Grid.toFixed(2)}</td>
        <td>${result.PV.toFixed(2)}</td>
        <td>${result.Wind.toFixed(2)}</td>
        <td>${result.Surplus.toFixed(2)}</td>
      `;
      resultsBody.appendChild(row);
    });
  };

  // Function to plot the energy production chart
  const plotEnergyProductionChart = (data) => {
    const ctx = document.getElementById('energyProductionChart').getContext('2d');
    const hours = data.map(item => `${item.Hour}:00`);
    const gridData = data.map(item => item.Grid);
    const pvData = data.map(item => item.PV);
    const windData = data.map(item => item.Wind);

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: hours,
        datasets: [
          { label: 'Grid (kW)', data: gridData, borderColor: 'red', fill: false },
          { label: 'Photovoltaic (kW)', data: pvData, borderColor: 'orange', fill: false },
          { label: 'Wind (kW)', data: windData, borderColor: 'blue', fill: false }
        ]
      }
    });
  };

  // Function to plot the surplus energy chart
  const plotSurplusEnergyChart = (data) => {
    const ctx = document.getElementById('surplusEnergyChart').getContext('2d');
    const hours = data.map(item => `${item.Hour}:00`);
    const surplusData = data.map(item => item.Surplus);

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: hours,
        datasets: [{ label: 'Surplus (kW)', data: surplusData, borderColor: 'green', fill: false }]
      }
    });
  };

  // Function to display KPI results
  const displayKpiResults = (kpi) => {
    document.getElementById('totalGridCost').innerText = `Grid: $${kpi.total_grid_cost.toFixed(2)}`;
    document.getElementById('totalPvCost').innerText = `PV (Daily): $${(kpi.total_pv_cost / 365).toFixed(2)}`;
    document.getElementById('totalWindCost').innerText = `Wind (Daily): $${(kpi.total_wind_cost / 365).toFixed(2)}`;
    document.getElementById('surplusEnergyValue').innerText = `Surplus Energy Value: $${kpi.total_surplus_value.toFixed(2)}`;
    document.getElementById('actualCostWithoutRenewable').innerText = `Actual cost of electricity from the grid per day without Renewable: $${kpi.actual_cost_without_renewable.toFixed(2)}`;
    document.getElementById('totalCost').innerText = `Total Cost: $${kpi.total_cost.toFixed(2)}`;
    document.getElementById('totalRevenue').innerText = `Total Revenue: $${kpi.total_revenue.toFixed(2)}`;
    document.getElementById('electricityPrice').innerText = `Electricity Price: $${kpi.electricity_price.toFixed(2)} per kWh`;
    document.getElementById('ghgEmissions').innerText = `GHG Emissions: ${kpi.ghg_emissions.toFixed(2)} kg CO2 per day`;
    document.getElementById('totalSurplusEnergy').innerText = `Total Surplus Energy: ${kpi.total_surplus.toFixed(2)} kWh per day`;
    document.getElementById('totalGridPower').innerText = `Total Grid Power After Optimization: ${kpi.total_grid_power.toFixed(2)} kWh per day`;
    document.getElementById('costReduction').innerText = `Cost Reduction: ${(kpi.cost_reduction * 100).toFixed(2)}% (Target: 20%)`;
    document.getElementById('emissionReduction').innerText = `Emission Reduction: ${(kpi.emission_reduction * 100).toFixed(2)}% (Target: 30%)`;
    document.getElementById('renewableFraction').innerText = `Renewable Fraction: ${(kpi.renewable_fraction * 100).toFixed(2)}% (Target: 50%)`;
    document.getElementById('kpiResults').style.display = 'block';
  };
  const handleFileChange = (e, tool) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        header: true,
        complete: (results) => {
          setFiles((prevFiles) => ({ ...prevFiles, [tool]: results.data }));
          uploadFile(file, tool);
        },
      });
    }
  };

  const uploadFile = (file, tool) => {
    const formData = new FormData();
    formData.append('file', file);

    axios.post('http://localhost:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    })
    .then(response => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setImageUrls((prevUrls) => ({ ...prevUrls, [tool]: url }));
      if (tool === 'tool3') {
        calculateLCOE(file);
      }
    })
    .catch(error => {
      console.error('Error uploading file:', error);
    });
  };

  const calculateLCOE = (file) => {
    const formData = new FormData();
    formData.append('file', file);

    axios.post('http://localhost:5000/lcoe', formData)
      .then(response => {
        const lcoeValue = response.data.LCOE;
        if (lcoeValue) {
          setPopupContent(`LCOE: ${lcoeValue}`);
          setPopupVisible(true);
        } else {
          console.error('LCOE not found in response');
        }
      })
      .catch(error => {
        console.error('Error calculating LCOE:', error.response?.data?.message || error.message);
      });
  };

  const handleRetrieve = () => {
    axios.get(`http://localhost:5000/retrieve?user_id=${userId}`)
      .then(response => {
        setRetrievedData(response.data);
      })
      .catch(error => {
        console.error('Error retrieving data:', error.response?.data?.message || error.message);
      });
  };

  const handleDownload = () => {
    axios.get('http://localhost:5000/api/get_data', { responseType: 'blob' })
    .then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'all_data.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch((error) => {
      console.error(error);
    });
  };

  const closePopup = () => {
    setPopupVisible(false);
  };
  const handleRunMgOp = () => {
    axios.get(`http://localhost:5000/RunMGOP?user_id=${userId}`)
      .then(response => {
        console.log("Backend response: ", response.data); // Log the entire response
  
        if (response.data && response.data.results_df) {
          setMgOpResults(response.data.results_df); // Save the results in state
  
          // Check if kpi_data exists and log it
          if (response.data.kpi_data) {
            console.log("KPI Data: ", response.data.kpi_data);
            setKpiData(response.data.kpi_data); // Set KPI data if it exists
          } else {
            console.warn("KPI Data is missing or undefined.");
          }
        }
      })
      .catch(error => {
        console.error('Error running MG-Op:', error.response?.data?.message || error.message);
      });
  };
  
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Collaborative Simulation I/O</h1>
      <div className="space-y-4">
        <div className="border p-4 rounded-lg">
          <label className="block mb-2 font-semibold">Upload CSV from NR-HESS:</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, 'tool1')}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {imageUrls.tool1 && <div className="mt-4"><img src={imageUrls.tool1} alt="CSV Data Plot" /></div>}
        </div>
        <div className="border p-4 rounded-lg">
          <label className="block mb-2 font-semibold">Upload CSV from SWITCH:</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, 'tool2')}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {imageUrls.tool2 && <div className="mt-4"><img src={imageUrls.tool2} alt="CSV Data Plot" /></div>}
        </div>
        <div className="border p-4 rounded-lg">
          <label className="block mb-2 font-semibold">Upload CSV from HOMER:</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, 'tool3')}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {imageUrls.tool3 && <div className="mt-4"><img src={imageUrls.tool3} alt="CSV Data Plot" /></div>}
        </div>
        <div className="border p-4 rounded-lg">
          <label className="block mb-2 font-semibold">Upload CSV from TRNSYS:</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, 'tool4')}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {imageUrls.tool4 && <div className="mt-4"><img src={imageUrls.tool4} alt="CSV Data Plot" /></div>}
        </div>
      </div>
      <button
        onClick={handleDownload}
        className="mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
      >
        Download Database Data as CSV
      </button>
      <div className="mt-4 border p-4 rounded-lg flex items-center">
        <div className="mr-4">
          <label className="block mb-2 font-semibold">Retrieve User Data:</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter User ID"
            className="block w-full text-sm text-gray-500 mb-4"
          />
          <button
            onClick={handleRetrieve}
            className="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
          >
            Retrieve Data
          </button>
          <button
        onClick={handleRunMgOp}
        className="bg-blue-700 text-white py-2 px-4 rounded-lg hover:bg-blue-800 mt-4"
      >
        RUN MG-op
      </button>
        </div>
      </div>

      {retrievedData && (
  <div className="mt-4">
    <h2 className="text-xl font-bold mb-2">Retrieved Data:</h2>
      {/*  <pre>{JSON.stringify(retrievedData, null, 2)}</pre>  */}
   

    <div className="mt-4 overflow-x-auto">
    <table className="table-auto w-full text-sm text-left text-gray-500 border-collapse border border-gray-300">
  <thead>
    <tr className="bg-gray-200">
      <th className="px-4 py-2 border">ID</th>
      <th className="px-4 py-2 border">Name</th>
      <th className="px-4 py-2 border">Type</th>
      <th className="px-4 py-2 border">Size (sq ft)</th>
      <th className="px-4 py-2 border">Daily Consumption</th>
      <th className="px-4 py-2 border">Demand</th>
      <th className="px-4 py-2 border">Surplus</th>
      <th className="px-4 py-2 border">Number of Occupants</th>
      <th className="px-4 py-2 border">Energy Sources</th>
    </tr>
  </thead>
  <tbody>
    {retrievedData.sites && retrievedData.sites.length > 0 ? (
      retrievedData.sites.map((site, index) => (
        <React.Fragment key={index}>
          {/* Main Row for Site Details */}
          <tr>
            <td className="border px-4 py-2">{site.id}</td>
            <td className="border px-4 py-2">{site.name}</td>
            <td className="border px-4 py-2">{site.site_type}</td>
            <td className="border px-4 py-2">{site.size}</td>
            <td className="border px-4 py-2">{site.daily_consumption}</td>
            <td className="border px-4 py-2">{site.demand}</td>
            <td className="border px-4 py-2">{site.surplus}</td>
            <td className="border px-4 py-2">{site.number_of_occupants}</td>
            <td className="border px-4 py-2">
              {/* Toggle to show energy sources dynamically */}
              <button onClick={() => toggleDetails(`energy_sources_${index}`)}>Show Energy Sources</button>
            </td>
          </tr>

          {/* Dynamic Energy Sources Details */}
          {site.energy_sources && (
            <tr id={`energy_sources_${index}`} style={{ display: 'none' }}>
              <td colSpan="9" className="border px-4 py-2">
                {Object.keys(site.energy_sources).map((sourceType, sourceIndex) => (
                  <div key={sourceIndex} className="mb-4">
                    <h3 className="font-bold capitalize">{sourceType.replace('_', ' ')} Details:</h3>
                    <table className="table-auto w-full text-sm text-left text-gray-500 border-collapse border border-gray-300">
                      <thead>
                        <tr className="bg-gray-100">
                          {Object.keys(site.energy_sources[sourceType]).map((detailKey, detailIndex) => (
                            <th key={detailIndex} className="px-4 py-2 border capitalize">{detailKey.replace('_', ' ')}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          {Object.values(site.energy_sources[sourceType]).map((detailValue, detailIndex) => (
                            <td key={detailIndex} className="border px-4 py-2">{detailValue || 'N/A'}</td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                ))}
              </td>
            </tr>
          )}
        </React.Fragment>
      ))
    ) : (
      <tr>
        <td colSpan="9" className="border px-4 py-2 text-center">No data available</td>
      </tr>
    )}
  </tbody>
</table>




    </div>
  </div>



)}

    
          
 

      {/* Display MG-Op results */}
      {mgOpResults && (
        <div className="mt-4">
          <h2 className="text-xl font-bold mb-2">MG-Op Results:</h2>
        {/*<pre>{JSON.stringify(mgOpResults, null, 2)}</pre>*/}  

          <div className="mt-4 overflow-x-auto">
        
             {/* Results Table */}
      <table id="resultsTable" className="mt-4 table-auto w-full text-sm text-left text-gray-500">
        <thead>
          <tr className="bg-gray-200">
            <th className="px-4 py-2 border">Hour</th>
            <th className="px-4 py-2 border">Grid</th>
            <th className="px-4 py-2 border">PV</th>
            <th className="px-4 py-2 border">Wind</th>
            <th className="px-4 py-2 border">Surplus</th>
          </tr>
        </thead>
        <tbody id="resultsBody"></tbody>
      </table>
          </div>
        </div>
      )}

      {/* Popup for LCOE */}
      {popupVisible && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <p>{popupContent}</p>
            <button
              onClick={closePopup}
              className="mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
      
   
      {/* Display KPI Results if available */}
      {kpiData && (
        <div id="kpiResults" className="mt-4">
          <h2 className="text-xl font-bold">KPI Results:</h2>
          <p>Total Grid Cost: ${kpiData.total_grid_cost.toFixed(2)}</p>
          <p>Total PV Cost (Daily): ${ (kpiData.total_pv_cost / 365).toFixed(2) }</p>
          <p>Total Wind Cost (Daily): ${ (kpiData.total_wind_cost / 365).toFixed(2) }</p>
          <p>Surplus Energy Value: ${ kpiData.total_surplus_value.toFixed(2) }</p>
          <p>Actual Cost Without Renewable: ${ kpiData.actual_cost_without_renewable.toFixed(2) }</p>
          <p>Total Cost: ${ kpiData.total_cost.toFixed(2) }</p>
          <p>Total Revenue: ${ kpiData.total_revenue.toFixed(2) }</p>
          <p>Electricity Price: ${ kpiData.electricity_price.toFixed(2) } per kWh</p>
          <p>GHG Emissions: { kpiData.ghg_emissions.toFixed(2) } kg CO2 per day</p>
          <p>Total Surplus Energy: { kpiData.total_surplus.toFixed(2) } kWh per day</p>
          <p>Total Grid Power: { kpiData.total_grid_power.toFixed(2) } kWh per day</p>
          <p>Cost Reduction: { (kpiData.cost_reduction * 100).toFixed(2) }%</p>
          <p>Emission Reduction: { (kpiData.emission_reduction * 100).toFixed(2) }%</p>
          <p>Renewable Fraction: { (kpiData.renewable_fraction * 100).toFixed(2) }%</p>
        </div>
      )}
   
     

      {/* Energy Production Chart */}
      <canvas id="energyProductionChart" className="mt-4"></canvas>

      {/* Surplus Energy Chart */}
      <canvas id="surplusEnergyChart" className="mt-4"></canvas>



      </div>
  );
};

export default Collab;