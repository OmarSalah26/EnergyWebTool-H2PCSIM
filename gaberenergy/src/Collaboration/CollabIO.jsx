import React, { useState } from 'react';
import Papa from 'papaparse';
import axios from 'axios';

const toolNames = {
  tool1: 'NR-HESS',
  tool2: 'SWITCH',
  tool3: 'TRNSYS',
  tool4: 'HOMER',
};

const fileAcceptTypes = {
  tool1: '.csv,.xlsx,.jpg', // NR-HESS
  tool2: '.csv,.xlsx,.jpg', // SWITCH
  tool3: '.csv,.xlsx,.jpg,.tpf', // TRNSYS
  tool4: '.csv,.xlsx,.jpg,.homer', // HOMER
};

const Collab = () => {
  const [files, setFiles] = useState({
    tool1: {},
    tool2: {},
    tool3: {},
    tool4: {},
  });
  const [imageUrls, setImageUrls] = useState({
    tool1: {},
    tool2: {},
    tool3: {},
    tool4: {},
  });
  const [showPopup, setShowPopup] = useState({
    tool1: false,
    tool2: false,
    tool3: false,
    tool4: false,
  });
  const [uploadLocation, setUploadLocation] = useState([]);

  const handleFileChange = (e, tool, location) => {
    const file = e.target.files[0];
    if (file && uploadLocation.length > 0) {
      Papa.parse(file, {
        header: true,
        complete: (results) => {
          setFiles((prevFiles) => ({
            ...prevFiles,
            [tool]: {
              ...prevFiles[tool],
              [location]: results.data,
            },
          }));
          uploadFile(file, tool, location); // Upload file for selected location
        },
      });
    } else {
      alert("Please select a location before uploading the file.");
    }
    setShowPopup((prevState) => ({
      ...prevState,
      [tool]: false,
    }));
    setUploadLocation([]); // Clear locations after upload
  };

  const handleUploadClick = (tool) => {
    setShowPopup((prevState) => ({
      ...prevState,
      [tool]: true,
    }));
  };

  const handleLocationSelect = (location) => {
    setUploadLocation((prevLocations) =>
      prevLocations.includes(location)
        ? prevLocations.filter((loc) => loc !== location)
        : [...prevLocations, location]
    );
  };

  const deleteCollab = (tool, location) => {
    setFiles((prevFiles) => ({
      ...prevFiles,
      [tool]: {
        ...prevFiles[tool],
        [location]: null,
      },
    }));
    setImageUrls((prevUrls) => ({
      ...prevUrls,
      [tool]: {
        ...prevUrls[tool],
        [location]: '',
      },
    }));

    axios
      .delete(`http://localhost:5173/delete`, { data: { tool, location } })
      .then((response) => {
        console.log('File deleted successfully:', response.data);
      })
      .catch((error) => {
        console.error('Error deleting file:', error);
      });
  };

  const uploadFile = (file, tool, location) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('location', location); // Add location for tracking

    axios
      .post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setImageUrls((prevUrls) => ({
          ...prevUrls,
          [tool]: {
            ...prevUrls[tool],
            [location]: url,
          },
        }));
      })
      .catch((error) => {
        console.error('Error uploading file:', error);
      });
  };

  const saveCollab = (tool, location) => {
    const fileData = files[tool][location];
    if (fileData) {
      // Add your save logic here
      axios
        .post('http://localhost:5000/save', { tool, location, data: fileData })
        .then((response) => {
          console.log('File saved successfully:', response.data);
        })
        .catch((error) => {
          console.error('Error saving file:', error);
        });
    } else {
      alert('No file data available to save.');
    }
  };

  const handleDownload = () => {
    axios
      .get('http://localhost:5000/api/get_data', { responseType: 'blob' })
      .then((response) => {
        const url = window.URL.createObjectURL(
          new Blob([response.data], { type: 'text/csv' })
        );
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

  const renderUploadSection = (tool) => {
    return (
      <div className="border p-4 rounded-lg">
        <label className="block mb-2 font-semibold">Upload File from {toolNames[tool]}:</label>
        <button
          onClick={() => handleUploadClick(tool)}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        >
          Choose File for {toolNames[tool]}
        </button>

        {Object.entries(files[tool] || {}).map(([location, fileData]) => (
          fileData && (
            <div key={location} className="mt-4">
              <p>{`File for ${location}: ${fileData[0] ? fileData[0].name : 'No file'}`}</p>
              {imageUrls[tool] && imageUrls[tool][location] && (
                <img src={imageUrls[tool][location]} alt={`${toolNames[tool]} Data Plot`} />
              )}
              <div className="flex space-x-2">
                <button
                  onClick={() => saveCollab(tool, location)}
                  className="mt-2 bg-blue-400 text-white py-2 px-2 rounded-lg hover:bg-blue-500"
                >
                  Save File for {location}
                </button>
                <button
                  onClick={() => deleteCollab(tool, location)}
                  className="mt-2 bg-red-400 text-white py-2 px-2 rounded-lg hover:bg-red-500"
                >
                  Delete File for {location}
                </button>
              </div>
            </div>
          )
        ))}
      </div>
    );
  };

  const renderPopup = (tool) => (
    showPopup[tool] && (
      <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex justify-center items-center">
        <div className="bg-white p-6 rounded-lg space-y-4">
          <h2 className="text-lg font-bold">Select Upload Location for {toolNames[tool]}</h2>
          {['Home', 'Water Plant', 'Power Utility', 'Hydrogen Plant'].map((location) => (
            <button
              key={location}
              className={`py-2 px-4 rounded-lg w-full ${
                uploadLocation.includes(location)
                  ? 'bg-blue-400 text-white'
                  : 'bg-gray-200 text-black'
              }`}
              onClick={() => handleLocationSelect(location)}
            >
              {location}
            </button>
          ))}

          <label className="block">
  <input
    type="file"
    accept={fileAcceptTypes[tool]} // Different file types based on tool
    onChange={(e) => handleFileChange(e, tool, uploadLocation[0])} // Handle file change for first location selected
    className="mt-2 file:bg-blue-300 file:text-white file:py-2 file:px-4 file:rounded-lg file:border-none file:cursor-pointer hover:file:bg-blue-400 text-gray-700"
  />
  </label>
          <button
            onClick={() => setShowPopup((prevState) => ({ ...prevState, [tool]: false }))}
            className="mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-400"
          >
            Close
          </button>
        </div>
      </div>
    )
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Collaborative Simulation I/O</h1>
      <div className="space-y-4">
        {/* Render sections for each tool */}
        {Object.keys(toolNames).map((tool) => renderUploadSection(tool))}
      </div>

      <button
        onClick={handleDownload}
        className="mt-4 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
      >
        Download Database Data as CSV
      </button>

      {/* Render popups for each tool */}
      {Object.keys(toolNames).map((tool) => renderPopup(tool))}
    </div>
  );
};

export default Collab;