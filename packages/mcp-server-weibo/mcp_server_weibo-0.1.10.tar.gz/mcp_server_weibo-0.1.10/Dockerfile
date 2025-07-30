FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install uvx

# Copy project files
COPY . .

# Install the package
RUN pip install -e .

# Expose the port MCP servers typically use
EXPOSE 8080

# Run the server
CMD ["mcp-server-weibo"]