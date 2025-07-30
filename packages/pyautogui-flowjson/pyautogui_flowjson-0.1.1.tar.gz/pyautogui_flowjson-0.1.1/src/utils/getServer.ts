import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import {
  CallToolRequestSchema,
  CallToolResult,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'
import { z } from 'zod'
import { zodToJsonSchema } from 'zod-to-json-schema'
import pkg from '../../package.json'
import * as defs from '../defs'
import { ServerType } from '../types'
import { def } from './def'
import { getContent } from './getContent'
import { logger } from './log'

const loggerRequestHandlerName = 'requestHandler'

export function getServer(serverType: ServerType = ServerType.mcpServer) {
  const coreDefs = Object.keys(defs)
    .filter((key) => key.includes('Def'))
    // @ts-expect-error
    .map((key) => defs[key] as ReturnType<typeof def>)

  switch (serverType) {
    case ServerType.mcpServer:
      const mcpServer = new McpServer({
        name: pkg.name,
        version: pkg.version,
        capabilities: {
          resources: {},
          tools: {},
        },
      })
      for (const v of coreDefs) {
        mcpServer.tool(v.name, v.description, v.argsSchema, async (...args) => {
          try {
            logger.info({
              type: `${v.name}:${loggerRequestHandlerName}:pre`,
              arg: args[0],
            })
            const res = await v.requestHandler(...args)
            logger.info({
              type: `${v.name}:${loggerRequestHandlerName}:next`,
              res,
            })
            return res
          } catch (err) {
            const errMessage = err instanceof Error ? err.message : String(err)
            const res: CallToolResult = await getContent(errMessage, true)
            logger.error({
              type: `${v.name}:${loggerRequestHandlerName}:next`,
              res,
            })
            return res
          }
        })
      }
      return mcpServer
    case ServerType.server:
      const server = new Server(
        {
          name: pkg.name,
          version: pkg.version,
        },
        {
          capabilities: {
            tools: {},
          },
        }
      )
      // Define available tools
      server.setRequestHandler(ListToolsRequestSchema, async () => {
        return {
          tools: coreDefs.map((v) => ({
            name: v.name,
            description: v.description,
            inputSchema: zodToJsonSchema(
              z.object(v.argsSchema)
              // .strict() // 默认 additionalProperties: false,
              // .passthrough() // additionalProperties: true,
            ),
          })),
        }
      })
      // Handle tool execution
      server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: arg } = request.params
        try {
          const item = coreDefs.find((v) => name === v.name)
          if (!item) throw new Error(`Unknown tool: ${name}`)

          logger.info({
            type: `${name}:${loggerRequestHandlerName}:pre`,
            arg: arg,
          })
          // @ts-expect-error
          const res = await item.requestHandler(arg)
          logger.info({
            type: `${name}:${loggerRequestHandlerName}:next`,
            res,
          })
          return res
        } catch (err) {
          const errMessage = err instanceof Error ? err.message : String(err)
          const res = await getContent(errMessage, true)
          logger.error({
            type: `${name}:${loggerRequestHandlerName}:next`,
            res,
          })
          return res
        }
      })
      return server
    default:
      throw new Error('Unknown server type')
  }
}
