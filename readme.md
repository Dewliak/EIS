# EU wallett identification

HTTPS needed : cloudflare

> curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
> chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
after that: 
> cloudflared tunnel --url http://localhost:5000