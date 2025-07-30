#!/usr/bin/env node

// [stdio 参考](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md#stdio)
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { argv } from '@zeroer/general-tools'
import { getServer } from './utils/getServer'

async function main() {
  try {
    const transport = new StdioServerTransport()
    const server = getServer(argv.serverType)
    await server.connect(transport)
    console.info('MCP Server running on Stdio')
  } catch (error) {
    console.error('MCP Server running Stdio error', error)
    process.exit(1)
  }
}

main()
