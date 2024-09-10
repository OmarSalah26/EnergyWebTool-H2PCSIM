import React, { useState } from 'react';
import Papa from 'papaparse';
import axios from 'axios';

const Collab = () => {
  const [files, setFiles] = useState({ tool1: null, tool2: null, tool3: null, tool4: null });
  const [imageUrls, setImageUrls] = useState({ tool1: '', tool2: '', tool3: '', tool4: '' });
  const [lcoe, setLcoe] = useState(null);
  const [popupContent, setPopupContent] = useState('');
  const [popupVisible, setPopupVisible] = useState(false); 
  const [userId, setUserId] = useState('');
  const [retrievedData, setRetrievedData] = useState(null);
  const [mgOpResults, setMgOpResults] = useState(null); // State for MG-Op results

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
    axios.get('http://localhost:5000/RunMGOP')
      .then(response => {
        if (response.data && response.data.results_df) {
          setMgOpResults(response.data.results_df); // Save the results in state
        }
        console.log(response.data.results_df)
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
        </div>
      </div>

      {retrievedData && (
  <div className="mt-4">
    <h2 className="text-xl font-bold mb-2">Retrieved Data:</h2>
    <pre>{JSON.stringify(retrievedData, null, 2)}</pre>

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
            <th className="px-4 py-2 border">PV Array Capacity (kW)</th>
            <th className="px-4 py-2 border">PV Array Efficiency (kW)</th>
            <th className="px-4 py-2 border">Wind Turbine Capacity (kW)</th>
          </tr>
        </thead>
        <tbody>
          {retrievedData.sites && retrievedData.sites.length > 0 ? (
            retrievedData.sites.map((site, index) => (
              <tr key={index}>
                <td className="border px-4 py-2">{site.id}</td>
                <td className="border px-4 py-2">{site.name}</td>
                <td className="border px-4 py-2">{site.site_type}</td>
                <td className="border px-4 py-2">{site.size}</td>
                <td className="border px-4 py-2">{site.daily_consumption}</td>
                <td className="border px-4 py-2">{site.demand}</td>
                <td className="border px-4 py-2">{site.surplus}</td>
                <td className="border px-4 py-2">{site.number_of_occupants}</td>
                <td className="border px-4 py-2">
                  {site.energy_sources?.pv_array?.capacity || 'N/A'}
                </td>
                <td className="border px-4 py-2">
                  {site.energy_sources?.pv_array?.efficiency || 'N/A'}
                </td>
                <td className="border px-4 py-2">
                  {site.energy_sources?.wind_turbine?.capacity || 'N/A'}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="10" className="border px-4 py-2 text-center">No data available</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  </div>



)}


        {/* Button to run MG-Op */}
        <button
        onClick={handleRunMgOp}
        className="bg-blue-700 text-white py-2 px-4 rounded-lg hover:bg-blue-800 mt-4"
      >
        RUN MG-op
      </button>
          
 

      {/* Display MG-Op results */}
      {mgOpResults && (
        <div className="mt-4">
          <h2 className="text-xl font-bold mb-2">MG-Op Results:</h2>
          <pre>{JSON.stringify(mgOpResults, null, 2)}</pre>

          <div className="mt-4 overflow-x-auto">
            <table className="table-auto w-full text-sm text-left text-gray-500 border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-200">
                  <th className="px-4 py-2 border">Hour</th>
                  <th className="px-4 py-2 border">Grid</th>
                  <th className="px-4 py-2 border">PV</th>
                  <th className="px-4 py-2 border">Wind</th>
                  <th className="px-4 py-2 border">Surplus</th>
                </tr>
              </thead>
              <tbody>
                {mgOpResults.length > 0 ? (
                  mgOpResults.map((result, index) => (
                    <tr key={index}>
                      <td className="border px-4 py-2">{result.Hour}</td>
                      <td className="border px-4 py-2">{result.Grid}</td>
                      <td className="border px-4 py-2">{result.PV}</td>
                      <td className="border px-4 py-2">{result.Wind}</td>
                      <td className="border px-4 py-2">{result.Surplus}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="border px-4 py-2 text-center">No results available</td>
                  </tr>
                )}
              </tbody>
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
    </div>
  );
};

export default Collab;