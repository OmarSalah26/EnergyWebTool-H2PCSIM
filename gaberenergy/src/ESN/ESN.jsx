import React, { useEffect, useRef, useState, useContext } from 'react';
import * as d3 from 'd3';
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import SharedContext from '../SharedContext';
import './ESN.css'; // Import the CSS file
import { useNavigate } from 'react-router-dom';

function ESN() {
  const ref = useRef();
  const navigate = useNavigate();
  const [selectedNode, setSelectedNode] = useState(null);
  const [detailedView, setDetailedView] = useState(true);
  const { sharedData } = useContext(SharedContext);

  const nodeTypes = [
    'PVArray', 'WT', 'Fuel Cell', 'Geothermal', 'Biomass', 'Hydro', 
    'Electrolyzer', 'Generator', 'SteamMethane', 'energyStorage', 
    'energyConverter', 'energyLoad', 'parameter', 'parameterValue'
  ];

  const color = d3.scaleOrdinal()
    .domain(nodeTypes)
    .range([
      '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
      '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78', '#c49c94'
    ]);

  function preprocessData(sharedData, detailed) {
    const nodeMap = new Map();
    const parameterNodes = [];
    const parameterEdges = [];
    const valueNodes = [];
    const valueEdges = [];
  
    if (detailed) {
      sharedData.nodes.forEach(node => {
        nodeMap.set(node.id, node);
        node.parameters.forEach(param => {
          // Create parameter node if it doesn't exist
          if (!nodeMap.has(param.name)) {
            const paramNode = { id: param.name, name: param.name, type: 'parameter' };
            nodeMap.set(param.name, paramNode);
            parameterNodes.push(paramNode);
          }
          parameterEdges.push({ source: node.id, target: param.name, type: 'parameter' });

          // Create value node if the value is not blank
          if (param.value !== '') {
            const paramValueNodeId = `${node.id}-${param.name}-value`;
            const paramValueNode = { id: paramValueNodeId, name: `${param.name}: ${param.value}`, type: 'parameterValue', value: param.value };
            nodeMap.set(paramValueNodeId, paramValueNode);
            valueNodes.push(paramValueNode);
            valueEdges.push({ source: param.name, target: paramValueNodeId, type: 'parameter' });
          }
        });
      });
    }
  
    const componentEdges = sharedData.edges.map(edge => ({
      ...edge,
      type: 'component'
    }));
  
    return {
      nodes: [...sharedData.nodes, ...parameterNodes, ...valueNodes],
      edges: [...componentEdges, ...parameterEdges, ...valueEdges],
    };
  }
  
  useEffect(() => {
    if (!sharedData || sharedData.nodes.length === 0) return;
  
    const processedData = preprocessData(sharedData, detailedView);
  
    const width = 1200;
    const height = 600;
  
    // Create a new force simulation
    const simulation = d3.forceSimulation(processedData.nodes)
      .force('link', d3.forceLink(processedData.edges).id(d => d.id).distance(50).strength(0.1)) // increase link distance
      .force('charge', d3.forceManyBody().strength(-400)) // increase repulsion strength
      .force('center', d3.forceCenter(width / 2, height / 2)) // center the nodes in the SVG
      .force('collide', d3.forceCollide().radius(40)); // increase collision radius
  
    // Select or create the SVG element
    const svg = d3.select(ref.current);
  
    // Clear previous content
    svg.selectAll('*').remove();
  
    // Apply zoom behavior to the SVG
    const zoomLayer = svg
      .attr('viewBox', `0 0 ${width} ${height}`)
      .call(d3.zoom().on('zoom', (event) => {
        zoomLayer.attr('transform', event.transform);
      }))
      .append('g');
  
    // Create links
    const link = zoomLayer.append('g')
      .selectAll('line')
      .data(processedData.edges)
      .join('line')
      .attr('stroke', d => d.type === 'parameter' ? '#999' : '#000') // set the stroke color based on type
      .attr('stroke-opacity', 0.6) // set the stroke opacity
      .attr('stroke-width', 1) // set a fixed stroke width
      .attr('stroke-dasharray', d => d.type === 'parameter' ? '0' : '4'); // solid line for parameter, dashed for component
  
    // Drag handlers
    const dragStarted = (event, d) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    };
  
    const dragged = (event, d) => {
      d.fx = event.x;
      d.fy = event.y;
    };
  
    const dragEnded = (event, d) => {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    };
  
    // Create nodes
    const node = zoomLayer.append('g')
      .selectAll('circle')
      .data(processedData.nodes)
      .join('circle')
      .attr('r', 10) // reduce node radius
      .attr('fill', d => color(d.type)) // color nodes based on their type
      .on('click', (event, d) => setSelectedNode(d)) // Attach click event listener
      .call(d3.drag() // Apply drag behavior
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded)
      );
  
    // Create labels
    const label = zoomLayer.append('g')
      .selectAll('text')
      .data(processedData.nodes)
      .join('text')
      .text(d => d.name) // set the text to the node name
      .attr('dx', 12) // offset the label horizontally
      .attr('dy', '.35em'); // offset the label vertically
  
    // Create edge labels for component edges
    const edgeLabel = zoomLayer.append('g')
      .selectAll('text')
      .data(processedData.edges.filter(edge => edge.type === 'component'))
      .join('text')
      .text('isConnected') // set the label to "isConnected"
      .attr('font-size', '10px')
      .attr('fill', '#000');
  
    // Update nodes, links, and labels on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
  
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
  
      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
  
      edgeLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2);
    });
  
  }, [sharedData, detailedView]);

  return (
    <>
      <h1 className="esn-title">Energy Semantic Network</h1>
      <div className="esn-container">
        {(!sharedData || sharedData.nodes.length === 0) && (
          <Popup open modal className='esn-popup'>
            <div className="esn-popup-message">
              <h2>No Energy Flow Diagram found</h2>
            </div>
          </Popup>
        )}
        <div className="esn-graph">
          <svg ref={ref}></svg>
        </div>
        <div className="esn-sidebar">
          {selectedNode && (
            <div>
              <h2>Node Parameters</h2>
              <p><strong>ID:</strong> {selectedNode.id}</p>
              <p><strong>Type:</strong> {selectedNode.type}</p>
              <p><strong>Name:</strong> {selectedNode.name}</p>
              <h3>Parameters:</h3>
              <ul>
                {selectedNode.parameters && selectedNode.parameters.map((param, index) => (
                  <li key={index}><strong>{param.name}:</strong> {param.value}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <button className="toggle-button" onClick={() => setDetailedView(!detailedView)}>
          {detailedView ? 'Show Non-Detailed View' : 'Show Detailed View'}
        </button>
      </div>
      <button className="toggle-button" onClick={() => navigate('/scenarios')}>
          Synthesize Scenarios
        </button>
    </>
  );
}

export default ESN;
