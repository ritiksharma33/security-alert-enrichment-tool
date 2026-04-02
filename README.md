# 🛡️ Sentinel SOAR 
### (Basically, a way to stop doing manual security lookups)

I built **Sentinel SOAR** because let's be honest—checking every single suspicious IP or file hash manually is a pain. This is a modular framework that handles the "boring" parts of security analysis. It hooks up to a few big threat intel APIs and uses some "If-This-Then-That" logic to tell you if something is actually dangerous or just a false alarm. 

It saves me (and hopefully other analysts) about 80% of the time usually spent on MTTR.

## 🚀 What it actually does
* **Smart Playbooks:** I coded a bunch of logic to sort threats into "Critical," "Warning," or "Safe." It’s not just a random guess—it looks at a few different factors at once.
* **The Big 3 APIs:** It’s already set up to talk to **AbuseIPDB** (for IPs), **WHOIS** (to see how old a domain is), and **VirusTotal** (for file hashes). 
* **Enrichment:** Instead of just getting a "bad" or "good" result, it pulls back the country, ISP, and even how many antivirus engines flagged a file.
* **Batch Mode:** If you have a huge list of IPs from a firewall log, just drop the CSV file in. It’ll scan them all at once so you don't have to go one-by-one.
* **White-listing:** I added a suppression list so the tool doesn't freak out when it sees things like Google DNS (8.8.8.8).

## 🧠 How the logic works (The "Brain")
I tried to keep the rules pretty simple but effective:

| Module | What it looks for | Result |
| :--- | :--- | :--- |
| **IPs** | Is the confidence score > 80%? | **CRITICAL** (Block it) |
| **Domains** | Is the domain less than 30 days old? | **CRITICAL** (Probably Phishing) |
| **Files** | Do 10+ AV engines say it's bad? | **CRITICAL** (It's Malware) |
| **Whitelist** | Is it on our "Trusted" list? | **SAFE** (Ignore it) |

## 📄 Step-by-Step (The SOP)
So basically, here is how you use it:
1.  **Input:** Give it an IP, Domain, or Hash. Or just upload your CSV file.
2.  **Lookup:** The app hits the APIs and checks my whitelist.
3.  **Analyze:** The engine decides the risk level based on the "If-This-Then-That" rules.
4.  **Fix:** If it’s CRITICAL, it'll give you a command (like `iptables`) to block it right away.
5.  **Logs:** Everything gets saved with a timestamp so you can go back and look at it later.

## 🛠️ Tech I used
* **Backend:** Python 3 (FastAPI) — I used async for the bulk scans so it doesn't freeze up.
* **Frontend:** React and Lucide-React for the icons.
* **Stuff that makes it work:** `httpx` for the API calls and `python-whois`.

## ⚙️ How to run it on your machine
1.  **Clone it:**
    `git clone https://github.com/ritiksharma33/security-alert-enrichment-tool`
2.  **API Keys:**
    You'll need a `.env` file in the root. Stick your keys in there like this:
    `ABUSEIPDB_API_KEY=your_key_here`
    `VIRUSTOTAL_API_KEY=your_key_here`
3.  **Start the Backend:**
    `uvicorn backend.main:app --reload`
4.  **Start the UI:**
    `npm install && npm start`

---
*I’m a 3rd-year CSE student who just wants to automate everything. If you find a bug, let me know!*

---
