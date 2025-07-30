import { PythonShell } from 'python-shell'
import z from 'zod'
import {
  def,
  getContent,
  KEYBOARD_KEYS,
  lfJoin,
  PythonShellOptions,
  toPyStrArg,
} from '../utils'

const getDurationSchema = () =>
  z
    .number()
    .optional()
    .describe(lfJoin('移动鼠标所需的时间', '默认为 0, 表示 瞬间移动'))

export const clickDef = def({
  name: 'click',
  description: lfJoin(
    '执行按下鼠标按钮然后立即释放的操作。',
    '当没有传递任何参数时，主鼠标按钮将在鼠标光标当前位置处点击。',
    '示例：',
    '1. 在 100 50 点击',
    `${JSON.stringify(
      {
        x: 100,
        y: 50,
      },
      null,
      2
    )}`,
    '2. 连续点击3次 每次间隔1秒',
    `${JSON.stringify(
      {
        clicks: 3,
        interval: 1,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    x: z.number().optional().describe(
      lfJoin(
        '事件发生的 x 坐标，如果未提供则使用当前鼠标位置。'
        // PyAutoGUI 没有做mac 分辨率处理
        // '如果 x 是一个字符串，则该字符串是图像文件名，PyAutoGUI 将尝试在屏幕上定位该文件并点击其中心',
      )
    ),
    y: z
      .number()
      .optional()
      .describe(lfJoin('事件发生的 y 坐标，如果未提供则使用当前鼠标位置。')),
    clicks: z
      .number()
      .optional()
      .describe(lfJoin('默认为 1', '表示要点击次数的整数')),
    interval: z
      .number()
      .optional()
      .describe(
        lfJoin(
          '如果 clicks > 1 它默认为 0 表示点击之间没有暂停',
          '表示每次点击之间等待多少秒的数量'
        )
      ),
    button: z
      .enum(['left', 'middle', 'right', 'primary', 'secondary'])
      .optional()
      .describe(
        lfJoin(
          "默认为'primary'(这是鼠标左键，除非操作系统已经设置为左撇子的用户。)",
          "可以是字符串常量 'left'、'middle'、'right'、'primary'或'secondary'之一"
        )
      ),
    duration: getDurationSchema(),
  },
  async requestHandler(arg) {
    const pyArgument = toPyStrArg(arg)
    await PythonShell.runString(
      lfJoin('import pyautogui', `pyautogui.click(${pyArgument})`),
      PythonShellOptions
    )
    return getContent('操作成功')
  },
})

export const moveRelDef = def({
  name: 'move',
  description: lfJoin(
    '将鼠标光标移动到屏幕上相对于其当前位置的某一点的位置。',
    '可以设置移动持续时间',
    '如果鼠标位置在屏幕的边界之外，事件发生在屏幕的边缘屏幕上。',
    '示例：',
    '1. 鼠标上移100px',
    `${JSON.stringify(
      {
        yOffset: -100,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    xOffset: z
      .number()
      .optional()
      .default(0)
      .describe('x 轴上的相对位移，正数向右，负数向左。'),
    yOffset: z
      .number()
      .optional()
      .default(0)
      .describe('y 轴上的相对位移，正数向下，负数向上。'),
    duration: getDurationSchema(),
  },
  async requestHandler(arg) {
    const pyArgument = toPyStrArg(arg)
    await PythonShell.runString(
      lfJoin('import pyautogui', `pyautogui.move(${pyArgument})`),
      PythonShellOptions
    )
    return getContent('操作成功')
  },
})

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

export const pressDef = def({
  name: 'press',
  description: lfJoin(
    '模拟键盘按键按下然后释放的动作。',
    '可以指定一个或多个键进行按下和释放操作。',
    '示例：',
    '1. 按下 “回车” 键',
    `${JSON.stringify(
      {
        keys: 'enter',
      },
      null,
      2
    )}`,
    '2. 按3次 a',
    `${JSON.stringify(
      {
        keys: 'a',
        presses: 3,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    keys: z
      .union([z.string(), z.array(z.string())])
      .describe(
        lfJoin(
          '要按的键',
          `有效的名称: ${KEYBOARD_KEYS.join(', ')}`,
          '也可以是这样的字符串的列表'
        )
      ),
    presses: z
      .number()
      .optional()
      .default(1)
      .describe(lfJoin('重复按下的次数', '默认为1，只按一次')),
    interval: z
      .number()
      .optional()
      .default(0)
      .describe(lfJoin('每次按压之间的秒数', '默认为0，表示按下之间没有暂停')),
  },
  async requestHandler(arg) {
    const pyArgument = toPyStrArg(arg)
    await PythonShell.runString(
      lfJoin('import pyautogui', `pyautogui.press(${pyArgument})`),
      PythonShellOptions
    )
    return getContent('操作成功')
  },
})
