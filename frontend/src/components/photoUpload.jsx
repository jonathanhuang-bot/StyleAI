import { useState } from "react"
function PhotoUpload() {
    const [selectedFiles, setSelectedFiles] = useState([])
    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files)
        setSelectedFiles(files)
    }
    const handleDragOver = (e) => {
        e.preventDefault()
    }
    const handleDrop = (e) => {
        e.preventDefault()
        const files = Array.from(e.dataTransfer.files)
        setSelectedFiles(files)
    }
    return (
        <div>
            <h1>Photo Upload</h1>
            <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                style={{
                    border: '2px dashed #ccc',
                    padding: '20px',
                    textAlign: 'center',
                    margin: '20px 0'
                }}
            >
                <p>Drag and drop images here, or click to select</p>
                <input type="file" onChange={handleFileSelect} multiple accept="image/*"/>
            </div>
            <p>Selected files: {selectedFiles.length}</p>
            <div>
                <h3>Preview:</h3>
                {selectedFiles.map((file, index) => (
                    <div key={index} style = {{margin: '10px'}}>
                        <img 
                            src = {URL.createObjectURL(file)}
                            alt = {file.name}
                            style = {{width: '200px', height: '200px', objectFit:'cover'}}
                        />
                        <p>{file.name} ({(file.size/1024/1024).toFixed(2)} MB)</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
export default PhotoUpload