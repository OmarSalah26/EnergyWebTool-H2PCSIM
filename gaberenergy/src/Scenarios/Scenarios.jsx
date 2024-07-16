import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Scenarios = () => {
  const [strategies, setStrategies] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const strategiesPerPage = 10;

  useEffect(() => {
    axios.get('http://localhost:5000/api/generate_strategies')
      .then(response => {
        setStrategies(response.data.strategies);
      })
      .catch(error => {
        console.error('There was an error fetching the strategies!', error);
      });
  }, []);

  const indexOfLastStrategy = currentPage * strategiesPerPage;
  const indexOfFirstStrategy = indexOfLastStrategy - strategiesPerPage;
  const currentStrategies = strategies.slice(indexOfFirstStrategy, indexOfLastStrategy);

  const paginate = pageNumber => setCurrentPage(pageNumber);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <h1 className="text-4xl font-bold mb-8">Energy Strategies</h1>
      <div className="w-full max-w-4xl overflow-x-auto">
        <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
          <thead>
            <tr>
              <th className="py-2 px-4 bg-gray-200 text-left">Energy System</th>
              <th className="py-2 px-4 bg-gray-200 text-left">Percentage</th>
              <th className="py-2 px-4 bg-gray-200 text-left" style={{ width: '150px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentStrategies.map((strategy, index) => (
              <React.Fragment key={index}>
                <tr className="bg-gray-50">
                  <td className="py-4 px-4 font-bold" colSpan="3">
                    Strategy {indexOfFirstStrategy + index + 1}
                  </td>
                </tr>
                {Object.entries(strategy.Startegy).map(([system, percentage], sysIndex) => (
                  <tr key={`${index}-${sysIndex}`} className="border-t border-gray-200">
                    <td className="py-2 px-4">{system}</td>
                    <td className="py-2 px-4">{percentage}%</td>
                    {sysIndex === 0 && (
                      <td className="py-2 px-4" rowSpan={Object.entries(strategy.Startegy).length}>
                        <button className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">
                          Evaluate Scenario
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination
        strategiesPerPage={strategiesPerPage}
        totalStrategies={strategies.length}
        paginate={paginate}
      />
    </div>
  );
};

const Pagination = ({ strategiesPerPage, totalStrategies, paginate }) => {
  const pageNumbers = [];

  for (let i = 1; i <= Math.ceil(totalStrategies / strategiesPerPage); i++) {
    pageNumbers.push(i);
  }

  return (
    <nav className="mt-8">
      <ul className="inline-flex items-center -space-x-px">
        {pageNumbers.map(number => (
          <li key={number}>
            <a
              onClick={() => paginate(number)}
              href="#!"
              className="py-2 px-3 ml-0 leading-tight text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 hover:text-gray-700"
            >
              {number}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Scenarios;
