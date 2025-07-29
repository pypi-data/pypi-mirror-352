# MagiCode CLI

A powerful command-line interface for interacting with MagiCode AI services.

## Installation

```bash
pip install magicode
```

##Getting Started

Before using MagiCode CLI, you'll need to authenticate with your credentials:

```bash
magicode auth
```
You'll be prompted to enter your email and secret token. These credentials will be securely stored for future use.

## Uploading Files

To upload a file to MagiCode, use the following command:

```bash
magicode upload [path]
``` 

The "path" can point to a local file or directory. 

To upload to a specific directory, use the following command: 

```bash
magicode upload [path] --destination folder/
``` 


## Local Development 

To run the CLI locally, you can use the following command:

```bash
python uninstall magicode 
pip install -e . 
```

