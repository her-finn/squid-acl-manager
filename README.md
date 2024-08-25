# NACL - a Simple Squid ACL Manager
## Requirements
- Debian 12 Server (or any other Server where Python3 and Squid can be installed on)
- Squid installed
- git
- Python3 Packges installed with pip
## Installation and Connection with Squid
### 1. Clone the repository to /nacl and cd into
```
git clone https://github.com/her-finn/squid-acl-manager.git /nacl
cd /nacl
```
### 2. Install required Python Packages
```
pip3 install -r requirements.txt
```
### 3. Initialize Database and test
```
python3 nacl-check.py
```
*Abort (STRG + c)*
and Check if Database was created
```
ls nacl.db
```
### 4. Make script executeable
```
chmod +x nacl-check.py
```
### 5. Adjust Squid config
```
vim /etc/squid/squid.conf
```
and add these Lines on top of the file to use nacl.py as acl manager
```
external_acl_type nacl children=5 ttl=60 %SRC %URI /nacl/nacl-check.py
acl nacl external nacl
http_access allow nacl
```
### 6. Restart Squid
```
systemctl restart squid
```

## Installation of Web-Management
### 1. Copy Systemd File
```
cp /nacl/nacl-manager-web.service /etc/systemd/system/nacl-manager-web.service
```
### 2. Reload Systemd
```
systemctl daemon-reload
```
### 3. Start + Enable Web-Frontend
```
systemctl enable --now nacl-manager-web
```

**Now youre able to Access Management UI via [http://localhost:5000](http://localhost:5000). If you want to Access to Management UI from Network (WHICH IS NOT RECOMMENDED, Just use a Reverse Proxy like nginx)**, change the /nacl/web/app.py like this:
```
vim /nacl/web/app.py
```
search for this line: `app.run(debug=False)` and change it:
```
app.run(Debug=False,host="0.0.0.0")
```
   
