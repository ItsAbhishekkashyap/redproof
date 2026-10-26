# Alan setup

Exact steps for wiring Redproof into Alan on this machine.

## A. Install Redproof

```powershell
python -m pip install -e C:\Users\abhi4\redproof\redproof
```

Later, install the published GitHub version:

```powershell
python -m pip install git+https://github.com/ItsAbhishekkashyap/redproof
```

## B. Add the MCP server in Alan

In Alan: **Settings -> Plugins -> MCP tab -> "Add custom connector"**.

### Option 1: local command (stdio)

Find the full Python path:

```powershell
python -c "import sys; print(sys.executable)"
```

On this machine it is:

```
C:\Users\abhi4\AppData\Local\Programs\Python\Python312\python.exe
```

Use these values in the connector:

- Command: `C:\Users\abhi4\AppData\Local\Programs\Python\Python312\python.exe`
- Arguments: `["-m", "redproof.mcp_server"]`

The exact stdio command line is:

```
C:\Users\abhi4\AppData\Local\Programs\Python\Python312\python.exe -m redproof.mcp_server
```

### Option 2: URL (streamable HTTP)

Start the server:

```powershell
redproof-mcp --http --port 8765
```

Then use this URL in the connector:

```
http://127.0.0.1:8765/mcp
```

The installed `mcp` 2.3.0 serves streamable HTTP at `/mcp`, so this is the correct path.

## C. Add the skill

In Alan's skills, import from GitHub using the folder link:

```
https://github.com/ItsAbhishekkashyap/redproof/tree/main/skills/redproof
```

## D. Try it

Create the loop scenario (pick a folder that does not exist yet):

```powershell
python C:\Users\abhi4\redproof\redproof\demo\make_demo.py C:\Users\abhi4\redproof-demo-loop --scenario loop
```

Open `C:\Users\abhi4\redproof-demo-loop` in a new Alan session on **"This computer"**, then send:

```
I fixed the discount bug in shop/pricing.py and wrote a test. Verify my tests are real before we finish.
```

Redproof should report `FAKE_TESTS_FOUND`, the skill should make the agent rewrite the test, and a second round should reach `PROVEN`. The reports are written under `.redproof/` in the demo folder.