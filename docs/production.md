## Production Deployment

### Reverse Proxy (nginx)
```nginx
# /etc/nginx/sites-available/ohdsi-mcp
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # For SSE support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### Systemd Service
```ini
# /etc/systemd/system/ohdsi-mcp.service
[Unit]
Description=OHDSI WebAPI MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ohdsi-mcp
Environment=WEBAPI_BASE_URL=https://your-webapi.org/WebAPI
Environment=WEBAPI_SOURCE_KEY=YOUR_CDM_SOURCE
Environment=MCP_PORT=8000
Environment=MCP_HOST=127.0.0.1
ExecStart=/usr/local/bin/ohdsi-webapi-mcp-http
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ohdsi-mcp
sudo systemctl start ohdsi-mcp
sudo systemctl status ohdsi-mcp
```
