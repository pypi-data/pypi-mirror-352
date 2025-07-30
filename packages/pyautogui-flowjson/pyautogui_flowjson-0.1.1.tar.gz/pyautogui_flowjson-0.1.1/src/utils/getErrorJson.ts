export function getErrorJson(message = '发生错误') {
  return {
    id: null,
    jsonrpc: '2.0',
    error: {
      code: -32000,
      message,
    },
  }
}
