# EU wallett identification

HTTPS needed : cloudflare

> curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
> chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
after that: 
> cloudflared tunnel --url http://localhost:5000
> 
 using python 3.13 \

> sudo dnf install python3.13 python3.13-devel python3.13-venv -y \

C libs for PIllow

> sudo dnf install libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel -y

> 1. start fastapi: uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000 --reload
> 2. start streamlit login page: streamlit run app.py --server.port 8501