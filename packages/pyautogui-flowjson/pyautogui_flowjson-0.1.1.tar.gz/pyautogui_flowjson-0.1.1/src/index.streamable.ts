// [streamableHttp 参考](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md#streamable-http)
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js'
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js'
import { isInitializeRequest } from '@modelcontextprotocol/sdk/types.js'
import express from 'express'
import { randomUUID } from 'node:crypto'
import { headersKey, ServerType } from './types'
import { getErrorJson, getIsStateless } from './utils'
import { getServer } from './utils/getServer'

const app = express()
app.use(express.json())

// 按 sessionID 存储传输对象的映射
const transports = {
  streamable: {} as Record<string, StreamableHTTPServerTransport>,
  sse: {} as Record<string, SSEServerTransport>,
}

// 处理客户端到服务器的POST请求
app.post('/mcp', async (req, res) => {
  // 通过header设置serverType
  const server = getServer(
    req.headers[headersKey.serverType] as ServerType | undefined
  )
  /**
   * 处理有状态
   */
  async function handleStatehave() {
    // 检查是否存在 sessionID
    const sessionId = req.headers[headersKey.sessionId] as string | undefined
    let transport: StreamableHTTPServerTransport

    if (sessionId && transports.streamable[sessionId]) {
      // 重用现有的传输对象
      transport = transports.streamable[sessionId]
    } else if (!sessionId && isInitializeRequest(req.body)) {
      // 新的初始化请求
      // const eventStore = new InMemoryEventStore();
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (sessionId) => {
          // 按 sessionID 存储传输对象
          transports.streamable[sessionId] = transport
        },
      })

      // 当传输关闭时进行清理
      transport.onclose = () => {
        if (transport.sessionId) {
          delete transports.streamable[transport.sessionId]
        }
      }

      await server.connect(transport)
    } else {
      // 无效请求
      res.status(400).json(getErrorJson('错误请求：没有提供有效的 sessionID'))
      return
    }

    // 处理请求
    await transport.handleRequest(req, res, req.body)
  }
  /**
   * 处理无状态
   */
  async function handleStateless() {
    // 在无状态模式下，为每个请求创建一个新的transport和服务器实例
    // 确保完全隔离。单个实例将导致请求ID冲突
    // 当多个客户端并发连接时。

    try {
      const transport: StreamableHTTPServerTransport =
        new StreamableHTTPServerTransport({
          sessionIdGenerator: undefined,
        })
      res.on('close', () => {
        transport.close()
        server.close()
      })
      await server.connect(transport)
      await transport.handleRequest(req, res, req.body)
    } catch (error) {
      console.error('错误处理 MCP request:', error)
      if (!res.headersSent) {
        res.status(500).json(getErrorJson('服务器内部错误'))
      }
    }
  }
  // 分发
  await (getIsStateless(req) ? handleStateless() : handleStatehave())
})

// 用于GET和DELETE请求的可重用处理器
const handleSessionRequest = async (
  req: express.Request,
  res: express.Response
) => {
  /**
   * 处理有状态
   */
  async function handleStatehave() {
    const sessionId = req.headers[headersKey.sessionId] as string | undefined
    if (!sessionId || !transports.streamable[sessionId]) {
      res.status(400).send('无效或丢失 sessionID')
      return
    }

    const transport = transports.streamable[sessionId]
    await transport.handleRequest(req, res, req.body)
  }
  /**
   * 处理无状态
   */
  async function handleStateless() {
    res.writeHead(405).end(JSON.stringify(getErrorJson('方法不允许')))
  }
  // 分发
  await (getIsStateless(req) ? handleStateless() : handleStatehave())
}

// 处理通过SSE进行服务器到客户端通知的GET请求
app.get('/mcp', handleSessionRequest)

// 处理会话终止的DELETE请求
app.delete('/mcp', handleSessionRequest)

// [兼容 SSE](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md#server-side-compatibility)
// 兼容遗留的 SSE 端点 来自老客户端
app.get('/sse', async (req, res) => {
  // 通过header设置serverType
  const server = getServer(
    req.headers[headersKey.serverType] as ServerType | undefined
  )

  // 创建 SSE transport for legacy clients
  const transport = new SSEServerTransport('/messages', res)
  transports.sse[transport.sessionId] = transport

  res.on('close', () => {
    delete transports.sse[transport.sessionId]
  })
  await server.connect(transport)
})

// 兼容遗留的 message 端点 来自老客户端
app.post('/messages', async (req, res) => {
  const sessionId = req.query.sessionId as string
  const transport = transports.sse[sessionId]
  if (transport) {
    // [ServerError: stream is not readable](https://levelup.gitconnected.com/mcp-server-and-client-with-sse-the-new-streamable-http-d860850d9d9d)
    await transport.handlePostMessage(req, res, req.body)
  } else {
    res.status(400).send('未找到 sessionId 对应的 transport')
  }
})

const PORT = process.env.PORT ?? 3000

app.listen(PORT, (err) => {
  if (err) return console.error(err)
  console.info(`MCP Server running on Streamable, listening port ${PORT}`)
})
