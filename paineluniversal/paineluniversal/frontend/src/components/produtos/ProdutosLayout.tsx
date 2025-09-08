import React from 'react';
import { Outlet } from 'react-router-dom';

const ProdutosLayout: React.FC = () => {
  return (
    <div className="h-full bg-background">
      <Outlet />
    </div>
  );
};

export default ProdutosLayout;