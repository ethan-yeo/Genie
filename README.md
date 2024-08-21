
# PDF and File Querying Application

## Introduction
This project is a web-based application that allows users to upload PDF files and query their contents using natural language processing and Retrieval Augmented Generation (RAG).
It leverages the LangChain framework to split, embed, and query documents, providing users with relevant responses based on their queries.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
4. [Dependencies](#dependencies)
5. [Configuration](#configuration)
6. [Documentation](#documentation)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Contributors](#contributors)
10. [License](#license)

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ethan-yeo/Genie.git
   cd Genie
   ```
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

## Usage
1. **Start the Flask backend**:
   ```bash
   python app.py
   ```
2. **Start the React frontend**:
   ```bash
   npm start
   ```
3. **Access the application**:
   Navigate to `http://localhost:3000` in your web browser.

## Features
- **PDF Querying**: Upload PDFs and ask questions about their content.
- **Batch File Query**: Upload multiple files at once and query across all of them.
- **Real-time Feedback**: See query responses in real-time with loading indicators.
- **File Reset**: Clear the current file session and start fresh.

## Dependencies
- **Backend**:
  - Flask
  - Flask-CORS
  - LangChain
  - PyMuPDF
  - Chroma
  - LMStudio
- **Frontend**:
  - React
  - Axios
  - React Loader Spinner
  - React Dropzone

## Configuration
- **Environment Variables**: 
  - Ensure to set up your OpenAI API key and other required environment variables in a `.env` file in the root directory.
    
- **LMStudio**:
  - Download the latest version of LMStudio, download your LLM of choice and host the server locally, remember to change the model name inside app.py , in my case i used "Meta-Llama-3-8B-Instruct-GGUF"

## Documentation
For detailed API documentation, refer to the inline comments within the code and the documentation provided in the `docs` directory.

## Examples
Here are a few examples of how to use the application:
- Upload a PDF and ask, "What are the key points in this document?"
- Upload multiple text files and ask, "Which document contains information about X?"

## Troubleshooting
- **Issue**: The server is not starting.
  - **Solution**: Ensure all dependencies are installed and check for any missing environment variables.
- **Issue**: Files are not uploading.
  - **Solution**: Check the file size and format; ensure it's within the allowed limits.

## Contributors
- [Ethan](https://github.com/ethan-yeo)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
