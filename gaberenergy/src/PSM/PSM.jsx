import React, { useState, useCallback, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactFlow, {
  addEdge,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'react-flow-renderer';
import CustomNode from './CustomNode.jsx';
import { parameterTemplates } from './parameterTemplates.js';
import './PSM.css';
import Popup from 'reactjs-popup';
import UsernameForm from './Usernameform.jsx';
import 'reactjs-popup/dist/index.css';
import axios from 'axios'; 
import SharedContext from '../SharedContext.jsx';

const apiRoute = 'http://localhost:5000'; 

const initialNodes = [];
const initialEdges = [];

const nodeTypes = {
  customNode: CustomNode,
};

const components = {
  renewableEnergySources: {
    elecGeneration: [
      'PVArray',
      'WT',
      'FC',
      'Geothermal',
      'Biomass',
      'Hydro',
      "WaterTreatmentPlant",
      "CHP",
      "HydrogenBasedCPHS"
    ],
    h2Generation: [
      'Electrolyzer',
    ],
  },
  nonRenewableEnergySources: {
    elecGeneration: [
      'Generator',
    ],
    h2Generation: [
      'SteamMethane',
    ],
  },
  energyStorage: [
    'Battery',
    'H2Tank',
    'Flywheel',
    'Thermal',
  ],
  invertersConverters: [
    'Converter_DC_AC',
    'Inverter_AC_DC',
  ],
  energyLoad: [
    'WaterLoad',
    'ElectricLoad',
    'HydrogenLoad',
    'GasLoad',
  ],
  utilities: [
    'Utility',
  ],
  organization: [
    'Organization',
  ],
};

function PSM() {
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, nodeId: null });
  const [selectedNode, setSelectedNode] = useState(null);
  const [open, setOpen] = useState(true); 
  const [userData, setUserData] = useState('');
  const [isLocationFormOpen, setIsLocationFormOpen] = useState(false);
  const [locationData, setLocationData] = useState({
    longitude: '',
    latitude: '',
    altitude: '',
    name: '',
    description: '',
    country: '',
    city: '',
    address: '',
  });

  const { setSharedData } = useContext(SharedContext);

  const handleSaveFormData = (userData) => {
    if (userData) {
      setUserData(userData);
      setOpen(false);
    }
  };

  useEffect(() => {
    setOpen(true);
  }, []);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge({ ...params }, eds));
  }, [setEdges]);

  const onDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const onDrop = (event) => {
    event.preventDefault();
  
    const reactFlowBounds = event.target.getBoundingClientRect();
    const type = event.dataTransfer.getData('application/reactflow');
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    };
  
    let parameters = [];
    let category = '';

    if (components.renewableEnergySources.elecGeneration.includes(type)) {
      category = 'renewableEnergySources.elecGeneration';
      parameters = parameterTemplates.energySources.renewableEnergySources.elecGeneration[type].map(({ name, type }) => ({ name, value: '', type, valid: true }));
    } else if (components.renewableEnergySources.h2Generation.includes(type)) {
      category = 'renewableEnergySources.h2Generation';
      parameters = parameterTemplates.energySources.renewableEnergySources.h2Generation[type].map(({ name, type }) => ({ name, value: '', type, valid: true }));
    } else if (components.nonRenewableEnergySources.elecGeneration.includes(type)) {
      category = 'nonRenewableEnergySources.elecGeneration';
      parameters = parameterTemplates.energySources.nonRenewableEnergySources.elecGeneration[type].map(({ name, type }) => ({ name, value: '', type, valid: true }));
    } else if (components.nonRenewableEnergySources.h2Generation.includes(type)) {
      category = 'nonRenewableEnergySources.h2Generation';
      parameters = parameterTemplates.energySources.nonRenewableEnergySources.h2Generation[type].map(({ name, type }) => ({ name, value: '', type, valid: true }));
    } else if (components.energyStorage.includes(type)) {
      category = 'energyStorage';
      parameters = parameterTemplates.energyStorage[type].map(({ name, type }) => ({ name, value: '', type, valid: true }));
    } else if (components.invertersConverters.includes(type)) {
      parameters = parameterTemplates.energyConverter.map(({ name, type }) => ({ name, value: '', type, valid: true }));
      category = 'invertersConverters';
      if (type === 'Converter_DC_AC') {
        parameters.forEach((param) => {
          if (param.name === 'dc_ac_out') {
            param.value = 'AC';
          }
        });
      } else if (type === 'Inverter_AC_DC') {
        parameters.forEach((param) => {
          if (param.name === 'dc_ac_out') {
            param.value = 'DC';
          }
        });
      }
    } else if (components.energyLoad.includes(type)) {
      parameters = parameterTemplates.energyLoad.map(({ name, type }) => ({ name, value: '', type, valid: true }));
      category = 'energyLoad';
      parameters.forEach((param) => {
        if (param.name === 'Load Type') {
          param.value = type.replace('Load', '').toLowerCase();
        }
      });
    } else if (components.utilities.includes(type)) {
      parameters = parameterTemplates.utilities.map(({ name, type }) => ({ name, value: '', type, valid: true }));
      category = 'utilities';
    } else if (components.organization.includes(type)) {
      parameters = parameterTemplates.organization.map(({ name, type }) => ({ name, value: '', type, valid: true }));
      category = 'organization';
    }
  
    const newNode = {
      id: (nodes.length + 1).toString(),
      type: 'customNode',
      position,
      data: { label: `${type}`, parameters, category },
      style: { border: '1px solid #777', padding: '10px', borderRadius: '5px', backgroundColor: '#fff' },
    };
  
    setNodes((nds) => nds.concat(newNode));
  };

  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onNodeContextMenu = (event, node) => {
    event.preventDefault();
    setContextMenu({
      visible: true,
      x: event.clientX,
      y: event.clientY,
      nodeId: node.id,
    });
    setSelectedNode(node);
  };

  const handleCloseContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, nodeId: null });
    setSelectedNode(null);
  };

  const handleUpdateParameter = (index, value) => {
    const updatedNodes = nodes.map((node) => {
      if (node.id === selectedNode.id) {
        const updatedParameters = [...node.data.parameters];
        const { type } = updatedParameters[index];
        let parsedValue = value;
        let valid = true;

        if (type === 'int') {
          parsedValue = parseInt(value, 10);
          valid = !isNaN(parsedValue);
        } else if (type === 'float') {
          parsedValue = parseFloat(value);
          valid = !isNaN(parsedValue);
        }

        updatedParameters[index].value = valid ? parsedValue : value;
        updatedParameters[index].valid = valid;
        return {
          ...node,
          data: {
            ...node.data,
            parameters: updatedParameters,
          },
        };
      }
      return node;
    });
    setNodes(updatedNodes);
  };

  const renderCustomInput = (param, index) => {
    if (param.name === 'dc_ac_out') {
      return (
        <select value={param.value} onChange={(e) => handleUpdateParameter(index, e.target.value)}>
          <option value="">Select...</option>
          <option value="DC">DC</option>
          <option value="AC">AC</option>
        </select>
      );
    }

    return (
      <input
        type="text"
        value={param.value}
        style={{ borderColor: param.valid ? 'initial' : 'red' }}
        onChange={(e) => handleUpdateParameter(index, e.target.value)}
      />
    );
  };

  const serializeData = () => {
    const serializedNodes = nodes.map((node) => ({
      id: node.id,
      type: node.data.category,
      name: node.data.label,
      parameters: node.data.parameters.map((param) => ({
        name: param.name,
        value: param.valid ? param.value : '',
        type: param.type,
      })),
    }));

    const serializedEdges = edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    }));

    return { nodes: serializedNodes, edges: serializedEdges };
  };

  const handleSaveModel = () => {
    const serializedData = serializeData();
    const serializedLocationData = locationData;
    console.log('Serialized Data:', JSON.stringify(serializedData, null, 2));
    console.log('Form Data:', userData);
    console.log('Location Data:', serializedLocationData);

    // Update SharedContext with all the data
    setSharedData({ nodes: serializedData.nodes, edges: serializedData.edges, userData:userData, locationData: serializedLocationData });

    // Send the data to the backend
    axios
      .post(`${apiRoute}/api/save_model`, { ...serializedData, userData: userData, locationData: serializedLocationData, userID: localStorage.getItem('userId')}) 
      .then((response) => {
        console.log('Response from server:', response.data);
      })
      .catch((error) => {
        console.error('Error sending data to server:', error);
      });
  };

  const handleESNRun = () => {
    handleSaveModel();
    navigate('/esn');
  };

  const handleLocationInputChange = (e) => {
    const { name, value } = e.target;
    setLocationData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleLocationFormSubmit = (e) => {
    e.preventDefault();
    console.log('Location Data:', locationData);
    setIsLocationFormOpen(false);
  };

  return (
    <div className="psm-dndflow">
      <div className="psm-sidebar">
        <h3 className="psm-h3">Renewable Energy Sources</h3>
        <h4 className="psm-h4">Electric Generation</h4>
        {components.renewableEnergySources.elecGeneration.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-energy-source"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h4 className="psm-h4">H2 Generation</h4>
        {components.renewableEnergySources.h2Generation.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-h2-generation"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Non-Renewable Energy Sources</h3>
        <h4 className="psm-h4">Electric Generation</h4>
        {components.nonRenewableEnergySources.elecGeneration.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-nonrenewable-elec-generation"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h4 className="psm-h4">H2 Generation</h4>
        {components.nonRenewableEnergySources.h2Generation.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-nonrenewable-h2-generation"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Energy Storage</h3>
        {components.energyStorage.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-energy-storage"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Inverters/Converters</h3>
        {components.invertersConverters.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-inverter-converter"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Energy Load</h3>
        {components.energyLoad.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-energy-load"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Utilities</h3>
        {components.utilities.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-utility"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
        <h3 className="psm-h3">Organization</h3>
        {components.organization.map((type) => (
          <div
            key={type}
            className="psm-dndnode psm-organization"
            onDragStart={(event) => onDragStart(event, type)}
            draggable
          >
            {type}
          </div>
        ))}
      </div>
      <div className="psm-main-content" onClick={handleCloseContextMenu}>
        <h1 className="psm-h1">Define Physical System (PSM):</h1>
        <p className="psm-form-data">
        Site Name: {userData.siteName} | Site Type: {userData.siteType} | Demand: {userData.demand} | Daily Consumption: {userData.dailyConsumption} | Surplus: {userData.surplus} | Number of Occupants: {userData.numberOfOccupants} | Size: {userData.size}
        </p>
        <div className="psm-reactflow-wrapper" onDrop={onDrop} onDragOver={onDragOver}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onNodeContextMenu={onNodeContextMenu}
            fitView
          >
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
        <div className="flex space-x-4 mt-4">
          <button className="psm-button" onClick={handleSaveModel}>Save PSM Model</button>
          <button className="psm-button" onClick={handleESNRun}>Run ESN on Energy Flow Model</button>
          <button className="psm-button" onClick={() => setIsLocationFormOpen(true)}>Add Location</button>
        </div>

        {/* Help Section */}
        <div className="psm-help-section">
          <span className="psm-help-text">?</span>
          <div className="psm-help-popup">
            <p>Tips:</p>
            <ul>
              <li>Drag and drop nodes from the sidebar to the canvas.</li>
              <li>Right-click on a node to edit its parameters.</li>
              <li>Click backspace on a selected node to delete it</li>
              <li>Use the buttons below to save or run models.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Node Parameter Menu */}
      {contextMenu.visible && (
        <div
          className="psm-context-menu"
          style={{ top: contextMenu.y, left: contextMenu.x }}
        >
          <h4>{selectedNode?.data.label} Parameters</h4>
          {selectedNode && selectedNode.data.parameters && selectedNode.data.parameters.map((param, index) => (
            <div key={index}>
              <label>{param.name}: </label>
              {renderCustomInput(param, index)}
              {!param.valid && <span className="error-message">Invalid {param.type}</span>}
            </div>
          ))}
          <button onClick={handleCloseContextMenu}>Close</button>
        </div>
      )}

      {/* Location Form Popup */}
      <Popup open={open} closeOnDocumentClick={false} onClose={() => setOpen(false)}>
        <UsernameForm onSave={handleSaveFormData} />
      </Popup>

      <Popup open={isLocationFormOpen} closeOnDocumentClick={false} onClose={() => setIsLocationFormOpen(false)}>
        <div className="psm-popup-form">
          <form onSubmit={handleLocationFormSubmit}>
            <h3>Location Parameters</h3>
            <label>Longitude:</label>
            <input type="text" name="longitude" value={locationData.longitude} onChange={handleLocationInputChange} />
            <label>Latitude:</label>
            <input type="text" name="latitude" value={locationData.latitude} onChange={handleLocationInputChange} />
            <label>Altitude:</label>
            <input type="text" name="altitude" value={locationData.altitude} onChange={handleLocationInputChange} />
            <label>Name:</label>
            <input type="text" name="name" value={locationData.name} onChange={handleLocationInputChange} />
            <label>Description:</label>
            <input type="text" name="description" value={locationData.description} onChange={handleLocationInputChange} />
            <label>Country:</label>
            <input type="text" name="country" value={locationData.country} onChange={handleLocationInputChange} />
            <label>City:</label>
            <input type="text" name="city" value={locationData.city} onChange={handleLocationInputChange} />
            <label>Address:</label>
            <input type="text" name="address" value={locationData.address} onChange={handleLocationInputChange} />
            <button type="submit">Save Location</button>
            <button type="button" className="psm-cancel-button" onClick={() => setIsLocationFormOpen(false)}>Cancel</button>
          </form>
        </div>
      </Popup>
    </div>
  );
}

export default PSM;
