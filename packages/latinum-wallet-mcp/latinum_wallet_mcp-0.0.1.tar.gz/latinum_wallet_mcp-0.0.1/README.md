
# Local test
```
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
python3 server_stdio.py
```



# Compile
```
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
pyinstaller --onefile --name latinum_wallet_mcp server_stdio.py
```

# test:
```
./dist/latinum_wallet_mcp
```


# claude_desktop_config.json:

/Users/dennj/Library/Application Support/Claude/claude_desktop_config.json

```
{
    "mcpServers": {
        "latinum_wallet_mcp": {
            "command": "/Users/dennj/workspace/latinum_wallet_mcp/dist/latinum_wallet_mcp"
        }
    }
}
```





python setup.py sdist bdist_wheel