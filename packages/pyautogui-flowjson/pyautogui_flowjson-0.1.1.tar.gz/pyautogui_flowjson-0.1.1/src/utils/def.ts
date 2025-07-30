import { ToolCallback } from '@modelcontextprotocol/sdk/server/mcp.js'
import { ZodRawShape } from 'zod'

/** Ts 辅助函数 */
export function def<Args extends ZodRawShape>(obj: {
  name: string
  description: string
  argsSchema: Args
  requestHandler: ToolCallback<Args>
}) {
  return obj
}
