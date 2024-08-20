import React from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import PDFChatPage from "./pages/PDFChatPage";
import BatchFileQueryPage from './pages/BatchFileQueryPage';

function App() {
  return(
    <div className-="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PDFChatPage />} />
          <Route path="/batchfilequery" element={<BatchFileQueryPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App;