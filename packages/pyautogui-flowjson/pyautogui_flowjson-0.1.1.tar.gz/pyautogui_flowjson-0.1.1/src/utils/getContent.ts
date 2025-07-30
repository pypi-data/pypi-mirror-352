import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js'

export async function getContent(
  text: any,
  isError = false
): Promise<CallToolResult> {
  return {
    content: [
      {
        type: 'text',
        text: typeof text === 'string' ? text : JSON.stringify(text),
      },
    ],
    ...(isError ? { isError: true } : {}),
  }
}
