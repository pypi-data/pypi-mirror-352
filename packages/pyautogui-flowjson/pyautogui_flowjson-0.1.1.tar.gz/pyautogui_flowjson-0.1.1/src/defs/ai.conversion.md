### 背景

- 我在将 pyautogui 的 api 转换成 node js mcp 的写法
- 我将给你一个参考示例 然后我会提供 pyautogui api 定义 请严格按照示例仿写（转换成 node js mcp 的写法）
- 有关 Mcp 额外的信息 可以查看 参考资料

### 参考资料

- [MCP 基础介绍](https://modelcontextprotocol.io/introduction)
  - [MCP 核心架构](https://modelcontextprotocol.io/docs/concepts/architecture)
  - [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [入门 MCP Server 开发](https://modelcontextprotocol.io/quickstart/server) 重点关注 Node 的实现
- [入门 MCP Client 开发](https://modelcontextprotocol.io/quickstart/client) 重点关注 Node 的实现
- [MCP Typescript SDK 文档](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/README.md)

### 参考示例

- 例如 有如下 pyautogui.scroll 定义

```python
def scroll(clicks, x=None, y=None, logScreenshot=None, _pause=True):
    """Performs a scroll of the mouse scroll wheel.

    Whether this is a vertical or horizontal scroll depends on the underlying
    operating system.

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      clicks (int, float): The amount of scrolling to perform.
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.

    Returns:
      None
    """
```

应该得到

```ts
export const scrollDef = def({
  name: 'scroll',
  description: lfJoin(
    '执行鼠标滚轮的滚动',
    '这是垂直的还是水平的滚动取决于底层操作系统',
    'x和y参数指定事件发生的屏幕位置。如果未提供，则使用当前鼠标位置。',
    '示例：',
    '1. 在 520 235 处 向下滚动100px',
    `${JSON.stringify(
      {
        clicks: -100,
        x: 520,
        y: 235,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    clicks: z
      .number()
      .describe(lfJoin('要执行的滚动量', '正值表示向上滚动，负值表示向下滚动')),
    x: z
      .number()
      .optional()
      .describe(lfJoin('事件发生的 x 坐标，如果未提供则使用当前鼠标位置。')),
    y: z
      .number()
      .optional()
      .describe('事件发生的 y 坐标，如果未提供则使用当前鼠标位置。'),
  },
  async requestHandler(arg) {
    const pyArgument = toPyStrArg(arg)
    await PythonShell.runString(
      lfJoin('import pyautogui', `pyautogui.scroll(${pyArgument})`),
      PythonShellOptions
    )
    return getContent('操作成功')
  },
})
```
