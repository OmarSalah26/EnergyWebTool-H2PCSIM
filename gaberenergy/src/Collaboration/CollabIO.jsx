import React, { useState } from 'react';
import Papa from 'papaparse';
import axios from 'axios';

const Collab = () => {
  const [files, setFiles] = useState({ tool1: null, tool2: null, tool3: null, tool4: null });
  const [imageUrls, setImageUrls] = useState({ tool1: '', tool2: '', tool3: '', tool4: '' });

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
      responseType: 'blob',  // Important for handling the image blob response
    })
    .then(response => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setImageUrls((prevUrls) => ({ ...prevUrls, [tool]: url }));
    })
    .catch(error => {
      console.error('Error uploading file:', error);
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
          <label className="block mb-2 font-semibold">Upload CSV from TRANSYS:</label>
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
    </div>
  );
};

export default Collab;
