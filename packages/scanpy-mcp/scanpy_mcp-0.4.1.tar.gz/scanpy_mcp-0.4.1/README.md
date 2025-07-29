# Scanpy-MCP

Natural language interface for scRNA-Seq analysis with Scanpy through MCP.

## 🪩 What can it do?

- IO module like read and write scRNA-Seq data
- Preprocessing module,like filtering, quality control, normalization, scaling, highly-variable genes, PCA, Neighbors,...
- Tool module, like clustering, differential expression etc.
- Plotting module, like violin, heatmap, dotplot

## ❓ Who is this for?

- Anyone who wants to do scRNA-Seq analysis natural language!
- Agent developers who want to call scanpy's functions for their applications

## 🌐 Where to use it?

You can use scanpy-mcp in most AI clients, plugins, or agent frameworks that support the MCP:

- AI clients, like Cherry Studio
- Plugins, like Cline
- Agent frameworks, like Agno 


## 📚 Documentation

scmcphub's complete documentation is available at https://docs.scmcphub.org

## 🎬 Demo

A demo showing scRNA-Seq cell cluster analysis in a AI client Cherry Studio using natural language based on scanpy-mcp

https://github.com/user-attachments/assets/93a8fcd8-aa38-4875-a147-a5eeff22a559

## 🏎️ Quickstart

### Install

Install from PyPI
```
pip install scanpy-mcp
```
you can test it by running
```
scanpy-mcp run
```


#### run scnapy-mcp locally
Refer to the following configuration in your MCP client:

check path
```
$ which scanpy 
/home/test/bin/scanpy-mcp
```

```
"mcpServers": {
  "scanpy-mcp": {
    "command": "//home/test/bin/scanpy-mcp",
    "args": [
      "run"
    ]
  }
}
```

#### run scnapy-mcp remotely
Refer to the following configuration in your MCP client:

run it in your server
```
scanpy-mcp run --transport shttp --port 8000
```

Then configure your MCP client in local AI client, like this:
```

"mcpServers": {
  "scanpy-mcp": {
    "url": "http://localhost:8000/mcp"
  }
}
```

## 🤝 Contributing

If you have any questions, welcome to submit an issue, or contact me(hsh-me@outlook.com). Contributions to the code are also welcome!

## Citing
If you use scanpy-mcp in for your research, please consider citing  following work: 
> Wolf, F., Angerer, P. & Theis, F. SCANPY: large-scale single-cell gene expression data analysis. Genome Biol 19, 15 (2018). https://doi.org/10.1186/s13059-017-1382-0

