import { useState } from "react"
import axios from "axios"
import UserPreferences from "./userPreferences"
function PhotoUpload() {
    const [selectedFiles, setSelectedFiles] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [uploadResult, setUploadResult] = useState(null)
    const [userPreferences, setUserPreferences] = useState({
        favorite_colors: 'blue,black,white',
        style_preference: 'casual',
        budget_range: 'mid',
        occasion: 'everyday'
    })

    const handleAnalyze = async () => {
      if (selectedFiles.length === 0) {
          alert('Please select files first!')
          return
      }

      setIsLoading(true)
      setUploadResult(null)

      try {
          // Create FormData to send files and preferences
          const formData = new FormData()
          selectedFiles.forEach(file => {
              formData.append('files', file)
          })
          
          // Add user preferences to form data
          formData.append('favorite_colors', userPreferences.favorite_colors)
          formData.append('style_preference', userPreferences.style_preference)
          formData.append('budget_range', userPreferences.budget_range)
          formData.append('occasion', userPreferences.occasion)

          // Send to Flask API
          const response = await axios.post('http://localhost:5000/api/upload',
  formData, {
              headers: {
                  'Content-Type': 'multipart/form-data'
              }
          })

          setUploadResult(response.data)
      } catch (error) {
          setUploadResult({
              status: 'error',
              error: error.message
          })
      } finally {
          setIsLoading(false)
      }
  }
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
    
    const handlePreferencesChange = (newPreferences) => {
        setUserPreferences(newPreferences)
    }
    return (
        <div>
            <h1>StyleAI - Body Shape Analysis & Style Recommendations</h1>
            
            {/* User Preferences Form */}
            <UserPreferences onPreferencesChange={handlePreferencesChange} />
            
            <h2>Photo Upload</h2>
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
            
            {/* Analyze Button */}
            {selectedFiles.length > 0 && (
                <button 
                    onClick={handleAnalyze}
                    disabled={isLoading}
                    style={{
                        backgroundColor: isLoading ? '#ccc' : '#4CAF50',
                        color: 'white',
                        padding: '10px 20px',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        margin: '20px 0'
                    }}
                >
                    {isLoading ? 'Analyzing...' : 'Analyze Photos'}
                </button>
            )}
            
            {/* Results Display */}
            {uploadResult && (
                <div style={{
                    marginTop: '20px',
                    padding: '20px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    backgroundColor: uploadResult.status === 'error' ? '#ffebee' : '#e8f5e9'
                }}>
                    <h3>Analysis Results</h3>
                    {uploadResult.status === 'error' ? (
                        <p style={{color: 'red'}}>Error: {uploadResult.error}</p>
                    ) : (
                        <div>
                            <p style={{color: 'green'}}>{uploadResult.message}</p>
                            
                            {/* Body Analysis Results */}
                            {uploadResult.analysis && (
                                <div style={{ marginTop: '20px' }}>
                                    <h4>Body Shape Analysis</h4>
                                    {uploadResult.analysis.map((analysis, index) => (
                                        <div key={index} style={{
                                            border: '1px solid #ddd',
                                            padding: '15px',
                                            margin: '10px 0',
                                            borderRadius: '5px',
                                            backgroundColor: analysis.success ? '#f0f8ff' : '#fff5f5'
                                        }}>
                                            <h5>{analysis.filename}</h5>
                                            {analysis.success ? (
                                                <div>
                                                    <p><strong>Body Shape:</strong> {analysis.body_shape ? analysis.body_shape.replace('_', ' ').toUpperCase() : 'Unknown'}</p>
                                                    <p><strong>Confidence:</strong> {analysis.confidence ? (analysis.confidence * 100).toFixed(1) : 0}%</p>
                                                    {analysis.measurements && (
                                                        <div style={{ fontSize: '0.9em', color: '#666' }}>
                                                            <p><strong>Measurements (Ratios):</strong></p>
                                                            <ul>
                                                                <li>Shoulders: {analysis.measurements.shoulders?.toFixed(2) || 'N/A'}</li>
                                                                <li>Bust: {analysis.measurements.bust?.toFixed(2) || 'N/A'}</li>
                                                                <li>Waist: {analysis.measurements.waist?.toFixed(2) || 'N/A'}</li>
                                                                <li>Hips: {analysis.measurements.hips?.toFixed(2) || 'N/A'}</li>
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                <p style={{color: 'red'}}>Analysis failed: {analysis.error}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                            
                            {/* Style Recommendations */}
                            {uploadResult.recommendations && uploadResult.recommendations.length > 0 && (
                                <div style={{ marginTop: '20px' }}>
                                    <h4>Style Recommendations</h4>
                                    {uploadResult.recommendations.map((rec, index) => (
                                        <div key={index} style={{
                                            border: '1px solid #4CAF50',
                                            padding: '15px',
                                            margin: '10px 0',
                                            borderRadius: '5px',
                                            backgroundColor: '#f8fff8'
                                        }}>
                                            <h5>Recommendations for {rec.filename}</h5>
                                            <p><strong>Body Shape:</strong> {rec.body_shape ? rec.body_shape.replace('_', ' ').toUpperCase() : 'Unknown'}</p>
                                            <p><strong>Style:</strong> {rec.style_preference ? rec.style_preference.toUpperCase() : 'Not specified'}</p>
                                            <p><strong>Occasion:</strong> {rec.occasion ? rec.occasion.toUpperCase() : 'Not specified'}</p>
                                            
                                            <div style={{ marginTop: '15px' }}>
                                                <h6>Description:</h6>
                                                <p style={{ fontStyle: 'italic', marginBottom: '10px' }}>
                                                    {rec.recommendations?.description || 'No description available'}
                                                </p>
                                                
                                                <h6>Styling Goals:</h6>
                                                <ul>
                                                    {rec.recommendations?.styling_goals?.map((goal, i) => (
                                                        <li key={i}>{goal}</li>
                                                    )) || <li>No styling goals available</li>}
                                                </ul>
                                                
                                                <h6>Recommended Outfit:</h6>
                                                <div style={{ 
                                                    backgroundColor: '#fff',
                                                    padding: '10px',
                                                    borderRadius: '3px',
                                                    border: '1px solid #eee'
                                                }}>
                                                    {rec.outfit ? Object.entries(rec.outfit).map(([key, value]) => (
                                                        <p key={key} style={{ margin: '5px 0' }}>
                                                            <strong>{key.replace('_', ' ').toUpperCase()}:</strong> {value}
                                                        </p>
                                                    )) : <p>No outfit recommendations available</p>}
                                                </div>
                                                
                                                <h6>Styling Tips:</h6>
                                                <div style={{ fontSize: '0.9em', color: '#666' }}>
                                                    <p><strong>Best Necklines:</strong> {rec.styling_tips?.necklines?.join(', ') || 'None specified'}</p>
                                                    <p><strong>Color Tips:</strong> {rec.styling_tips?.colors?.do || 'None specified'}</p>
                                                    <p><strong>Avoid:</strong> {rec.styling_tips?.avoid?.join(', ') || 'None specified'}</p>
                                                </div>
                                                
                                                {/* Product Suggestions */}
                                                {rec.products && Object.keys(rec.products).length > 0 && (
                                                    <div style={{ marginTop: '20px' }}>
                                                        <h6>Shop These Recommendations:</h6>
                                                        {Object.entries(rec.products).map(([itemType, products]) => (
                                                            products.length > 0 && (
                                                                <div key={itemType} style={{ marginBottom: '15px' }}>
                                                                    <h7 style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                                                                        {itemType.replace('_', ' ')}:
                                                                    </h7>
                                                                    <div style={{ 
                                                                        display: 'flex', 
                                                                        gap: '10px', 
                                                                        overflowX: 'auto',
                                                                        padding: '10px 0',
                                                                        marginTop: '5px'
                                                                    }}>
                                                                        {products.map((product, idx) => (
                                                                            <div key={idx} style={{
                                                                                minWidth: '200px',
                                                                                border: '1px solid #ddd',
                                                                                borderRadius: '5px',
                                                                                padding: '10px',
                                                                                backgroundColor: '#fff'
                                                                            }}>
                                                                                {product.image_url && (
                                                                                    <img 
                                                                                        src={product.image_url} 
                                                                                        alt={product.title}
                                                                                        style={{
                                                                                            width: '100%',
                                                                                            height: '150px',
                                                                                            objectFit: 'cover',
                                                                                            borderRadius: '3px',
                                                                                            marginBottom: '8px'
                                                                                        }}
                                                                                    />
                                                                                )}
                                                                                <p style={{ 
                                                                                    fontSize: '0.85em', 
                                                                                    fontWeight: 'bold',
                                                                                    margin: '5px 0',
                                                                                    overflow: 'hidden',
                                                                                    textOverflow: 'ellipsis',
                                                                                    whiteSpace: 'nowrap'
                                                                                }}>
                                                                                    {product.title}
                                                                                </p>
                                                                                <p style={{ 
                                                                                    fontSize: '0.9em', 
                                                                                    color: '#0066cc',
                                                                                    fontWeight: 'bold',
                                                                                    margin: '5px 0'
                                                                                }}>
                                                                                    {product.price}
                                                                                </p>
                                                                                <p style={{ 
                                                                                    fontSize: '0.8em', 
                                                                                    color: '#666',
                                                                                    margin: '5px 0'
                                                                                }}>
                                                                                    {product.source}
                                                                                </p>
                                                                                {product.rating && (
                                                                                    <p style={{ 
                                                                                        fontSize: '0.8em', 
                                                                                        color: '#666',
                                                                                        margin: '5px 0'
                                                                                    }}>
                                                                                        ⭐ {product.rating} ({product.rating_count || 0} reviews)
                                                                                    </p>
                                                                                )}
                                                                                <a 
                                                                                    href={product.product_url} 
                                                                                    target="_blank" 
                                                                                    rel="noopener noreferrer"
                                                                                    style={{
                                                                                        display: 'block',
                                                                                        textAlign: 'center',
                                                                                        backgroundColor: '#4CAF50',
                                                                                        color: 'white',
                                                                                        padding: '8px',
                                                                                        borderRadius: '3px',
                                                                                        textDecoration: 'none',
                                                                                        fontSize: '0.8em',
                                                                                        marginTop: '8px'
                                                                                    }}
                                                                                >
                                                                                    View Product
                                                                                </a>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
export default PhotoUpload