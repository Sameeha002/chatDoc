import React from "react";
import "./Navbar.css"
import { GoSidebarExpand } from "react-icons/go";

const Navbar = ({ toggleSidebar }) => {
  return (
    <nav className="navbar navbar-expand-lg">
      <div className="container-fluid">
        <div className="expand-sidebar" onClick={toggleSidebar}>

        <GoSidebarExpand title="expand sidebar"/>
        </div>
        
        
        {/* <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNavAltMarkup"
          aria-controls="navbarNavAltMarkup"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div
          className="collapse navbar-collapse"
          id="navbarNavAltMarkup"
        >
        </div> */}
      </div>
    </nav>
  );
};

export default Navbar;
