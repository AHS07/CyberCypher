Write-Host "Starting Shadow-Sherpa Engine Servers..."

# Start Legacy Server
Start-Process python -ArgumentList "-m uvicorn server_legacy:app --host 0.0.0.0 --port 8001" -WindowStyle Minimized
Write-Host "Started Legacy Server on Port 8001"

# Start Headless Server
Start-Process python -ArgumentList "-m uvicorn server_headless:app --host 0.0.0.0 --port 8002" -WindowStyle Minimized
Write-Host "Started Headless Server on Port 8002"

# Start Local Node
Start-Process python -ArgumentList "-m uvicorn local_node:app --host 0.0.0.0 --port 8000" -WindowStyle Minimized
Write-Host "Started Local Node on Port 8000"

Write-Host "All servers started in background windows."
Write-Host "Ensure Ollama is running ('ollama serve')."
