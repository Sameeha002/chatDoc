import React, { useState } from 'react'
import Sidebar from '../Sidebar/Sidebar'
import Chatbot from '../Chatbot/Chatbot'
import Navbar from '../Navbar/Navbar'

const Home = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }
  return (
    <div className='home-container'>
      <Navbar toggleSidebar={toggleSidebar}/>
        <div className="sidebar">
            <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}/>
        </div>
        <div className="chatbot-message">
          <Chatbot  sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}/>
        </div>
      
    </div>
  )
}

export default Home
