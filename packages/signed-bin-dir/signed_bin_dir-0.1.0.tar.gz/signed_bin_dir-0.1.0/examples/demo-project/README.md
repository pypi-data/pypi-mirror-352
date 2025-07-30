# Demo Project

This is an example project showing how to use `signed-bin-dir`.

## Setup

1. Make the scripts executable:
   ```bash
   chmod +x bin/hello bin/deploy
   ```

2. Sign the bin directory:
   ```bash
   sign-bin-dir sign bin
   ```

3. Navigate into this directory and the tools will be automatically added to your PATH:
   ```bash
   cd examples/demo-project
   hello      # Should work!
   deploy     # Should work!
   ```

4. Navigate away and the tools are removed from PATH:
   ```bash
   cd ..
   hello      # Command not found
   ```

## Tools

- `hello` - A simple Python script that prints a greeting
- `deploy` - A bash script that simulates a deployment process 