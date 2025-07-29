## Running instructions
### 1. configure cursor
go to cursor settings -> MCP tab -> add new
copy paste this:
```json
{
  "mcpServers": {
    "CoDatascientist": {
        "url": "http://localhost:8000/sse"
    }
  }
}
```

### 2. optional (recommended): enable autorun mode 
this way it doesn't ask for permission to run the tool each time. settings -> features -> enable auto-run 

### 3. run co-datascientist-backend
follow co-datascientist-backend instructions on how to run. 

it will probably run on port 8001. make sure the CO_DATASCIENTIST_BACKEND_URL in settings (.env) is correct. 

### 4. run the local mcp server

`uv run .\main.py`

it will ask you to enter your api key. generate the key using `scripts/generate_token.py` in the `co-datascientist-backend` repository.

### 5. test it!
open `test/test.py` in cursor, and ask the model help from co-datascientist in improving the code


## problems
- venv and env vars: the command often is "python file.py", and it works now only because i activated the venv. we need a more foolproof interpreter path
- replacing the file with the temp: rn we just split the command by space and replace the .py part, but what if the path has spaces? what if it's not python?
- coupling to python
- relative paths accessed from the baseline
- implications of running the baseline script locally: compute, token usage, other stateful changes.
- multiple files with imports?


## TODO
- instead of temp files, create the files on a folder in the users project
- make clear that the workflow uses a LOT of cpu by actually running the code on the users machine
- make sure to reflect the progress
- make it easier to find the absolute path! now its staggering