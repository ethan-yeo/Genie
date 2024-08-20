import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { Oval } from 'react-loader-spinner';
import { useDropzone } from 'react-dropzone';
import './BatchFileQueryPage.css';
import MainNavBar from "../components/MainNavBar";
import { useNavigate } from "react-router-dom";

const BatchFileQueryPage = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]); 
  const [userPrompt, setUserPrompt] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);


  const handleKeyPress = (e) => {
    // Check if Enter key is pressed without Shift key
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent the default action to avoid line break in textarea
      handleFileUpload(); // Call the file upload function
    }
  };


  const onDrop = useCallback(acceptedFiles => {
    setFiles(acceptedFiles);
    const names = acceptedFiles.map(file => file.name); 
    setFileNames(names); 
  }, []);

  const {getRootProps, getInputProps, isDragActive} = useDropzone({
    onDrop,
    accept: 'application/pdf',
    multiple: true
  });

  const handleUserPromptChange = (e) => {
    setUserPrompt(e.target.value);
  };

  const handleFileUpload = async () => {
    if (!files.length || !userPrompt) {
      alert("Please select files and enter a prompt.");
      return;
    }
    setIsLoading(true);
    setUploadStatus("Uploading...");
    const formData = new FormData();
    files.forEach(file => {
      formData.append('uploaded_files', file);
    });
    formData.append('user_prompt', userPrompt);


  try {
    const response = await axios.post('http://localhost:5000/batch_file_query', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob', // Important for handling binary data
    });
    
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'BatchQueryResponses.zip'; // Default filename for ZIP
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?(.+)"?/);
      if (match) filename = match[1];
    }
    
    // Create a URL for the blob
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename); // Set the filename for ZIP
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    setUploadStatus("Download Ready");
    setIsLoading(false);
    // Optionally reset state or navigate
    setFiles([]);
    setUserPrompt('');
    // navigate('/some/path'); // If you want to navigate the user away
  } catch (error) {
    console.error('Error during file upload:', error);
    setUploadStatus("Error during upload");
    setIsLoading(false);
  }
};
   return (
    <div className="batch-file-query-page">
      <MainNavBar />
      <div className="upload-form">
        <h2>Batch File Query</h2>
        <div {...getRootProps()} className="dropzone">
          <input {...getInputProps()} />
          {
            isDragActive ?
              <p>Drop the files here ...</p> :
              fileNames.length > 0 ? // Step 4: Display file names if present
                <ul>{fileNames.map(name => <li key={name}>{name}</li>)}</ul> :
              <p>Drag 'n' drop some files here, or click to select files</p>
          }
        </div>


        <div className="prompt-and-submit-container">
        <textarea
          className="prompt-box"
          placeholder="Enter your prompt here..."
          value={userPrompt}
          onChange={handleUserPromptChange}
          onKeyPress={handleKeyPress}
        ></textarea>
        <button
          className="submit-button"
          onClick={handleFileUpload}
          disabled={isLoading}
        >
         {isLoading ? <Oval color="#fff" height={20} width={20} /> : 'Submit'}
          </button>

          <button
          className="reset-button"
          onClick={() => {
            setFiles([]);
            setFileNames([]);
            setUserPrompt('');
            setUploadStatus('');
            setIsLoading(false);
          }}
          disabled={isLoading}
        >
          Reset
          </button>
        </div>


        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
      </div>
    </div>
  );
};

export default BatchFileQueryPage;