/**
 * 服务器类型
 */
export enum ServerType {
  /**
   * mcp 服务器 配置简单
   */
  mcpServer = 'mcpServer',
  /**
   * [Low-Level Server 低级服务器 可以获取更多配置](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md#low-level-server)
   */
  server = 'server',
}

/**
 * 客户端 携带的mcp请求头 key
 */
export const headersKey = {
  /**
   * 服务器类型
   */
  serverType: 'mcp-server-type',
  /**
   * session-id
   */
  sessionId: 'mcp-session-id',
  /**
   * 是否无状态
   */
  stateless: 'mcp-stateless',
}

export const PICTURE_DESCRIBE = '可以是 本地绝对路径、远程链接、base64'
