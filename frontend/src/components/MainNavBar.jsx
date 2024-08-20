import React, { useState, useEffect } from "react";
import { MainNavBarData } from "./MainNavBarData";
import "./MainNavBar.css";
import { NavLink, useNavigate } from 'react-router-dom'

function MainNavBar() {

  const navigate = useNavigate();


  return (
    <div className="sidebar">
      <ul className="sidebar-list">
        {MainNavBarData.map((val, key) => {
          return (
            <li
              key={key}
              // divider row
              className={
                val.title == "- - - - - - - - - - - - - - -"
                  ? "special-row"
                  : "row"
              }
              id={
                // set different colour for currently active page
                window.location.pathname.split("/").slice(-2)[0] == val.link
                  ? "active"
                  : ""
              }
              onClick={() => {
                let pagePath = "/" + val.link; // path to selected page
                navigate(pagePath);
              }}
            >
              <div className="flex flex-row items-center">
                <div id="icon" className="mr-4"> {val.icon} </div>
                <div id="title"> {val.title} </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default MainNavBar;
