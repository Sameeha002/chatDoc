import React, { useState } from "react";
import "./Sidebar.css";
import { GoSidebarCollapse } from "react-icons/go";
import axios from "axios";
function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const [fileName, setFileName] = useState("");
  const [uploadedFiles, setuploadedFiles] = useState([])

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append("files", file);

    try {
      const response = await axios.post(
        "http://localhost:8000/upload/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("Upload success:", response.data);
      getDocuments() //refresh the file list after each upload
    } catch (error) {
      if (error.response) {
        // Server responded with a status code outside the 2xx range
        console.error("Upload error:", error.response.data);
      } else if (error.request) {
        // Request was made but no response received
        console.error(
          "No response received:",
          error.request
        );
      } else {
        // Something else happened
        console.error("Error:", error.message);
      }
      alert("Upload failed!");
    }
  };

  const handleInput = (e) => {
    const files = e.target.files[0];
    if (!files) return;

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
      "application/msword", // .doc
      "application/vnd.openxmlformats-officedocument.presentationml.presentation", // .pptx
      "text/csv", // .csv
    ];

    if (!allowedTypes.includes(files.type)) {
      console.error("Unsupported file type:", files.type);
      alert(
        "Only PDF, DOC, DOCX, and CSV files are allowed."
      );
      return;
    }
    setFileName(files.name);
    console.log("Selected file:", files);

    handleUpload(files);
  };

  const getDocuments = async() => {
    try {
      const response = await axios.get('http://localhost:8000/documents/')
      console.log('get documents succesfully', response.data)

      setuploadedFiles(response.data.files)
    } catch (error) {
      console.log("Error Fetching Documents:", error.message)
    }
  }
  return (
    <div className={`sidebar ${sidebarOpen ? "open" : ""}`}>
      <div
        className="close-sidebar"
        onClick={() => setSidebarOpen(false)}
      >
        <GoSidebarCollapse title="collapse sidebar" />
      </div>
      <h4>Configuration</h4>
      <div className="upload-doc">
        <p>Upload a document</p>
        <div className="drag-and-drop">
          <p className="drop-file">
            Drag and drop file here
          </p>
          <p className="file-formats">
            Accepted File Formats: PDF, DOCX, DOC, PPTX, CSV
          </p>
          <label className="custom-file-label">
            Choose File
            <input
              type="file"
              accept=".pdf, .doc, .docx, .csv, .pptx"
              onChange={handleInput}
            />
          </label>
          {sidebarOpen && fileName && (
            <p className="uploaded-file">{fileName}</p>
          )}
        </div>
      </div>
      <div className="see-uploaded-documents">
        <p onClick={getDocuments}>Click Here to see previous uploaded documents.</p>
        <ul>
          {uploadedFiles.map((file, index) => (
            <li key={index}>{file.split("_").slice(1).join("_")}</li>

          ))}
        </ul>
      </div>
    </div>
  );
}

export default Sidebar;
