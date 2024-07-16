import React from 'react';
import { Handle } from 'react-flow-renderer';

const CustomNode = ({ data }) => {
  let nodeStyle = {};
  
  switch (data.category) {
    case 'energySources':
      nodeStyle = { borderColor: '#00BFFF', backgroundColor: '#E0F7FF' }; // DeepSkyBlue
      break;
    case 'energyStorage':
      nodeStyle = { borderColor: '#FFD700', backgroundColor: '#FFF7E0' }; // Gold
      break;
    case 'invertersConverters':
      nodeStyle = { borderColor: '#32CD32', backgroundColor: '#E0FFE0' }; // LimeGreen
      break;
    case 'building':
      nodeStyle = { borderColor: '#FF4500', backgroundColor: '#FFE0E0' }; // OrangeRed
      break;
    case 'energySystems':
      nodeStyle = { borderColor: '#9370DB', backgroundColor: '#F3E5FF' }; // MediumPurple
      break;
    default:
      nodeStyle = { borderColor: '#000', backgroundColor: '#FFF' }; // Default
  }

  return (
    <div className="custom-node" style={nodeStyle}>
      <Handle type="target" position="left" />
      <div className="node-header">{data.label}</div>
      <Handle type="source" position="right" />
    </div>
  );
};

export default CustomNode;
