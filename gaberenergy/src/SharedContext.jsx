
import React, { createContext, useState } from 'react';

const SharedContext = createContext();

export const SharedProvider = ({ children }) => {
  const [sharedData, setSharedData] = useState(null);

  return (
    <SharedContext.Provider value={{ sharedData, setSharedData }}>
      {children}
    </SharedContext.Provider>
  );
};

export default SharedContext;
