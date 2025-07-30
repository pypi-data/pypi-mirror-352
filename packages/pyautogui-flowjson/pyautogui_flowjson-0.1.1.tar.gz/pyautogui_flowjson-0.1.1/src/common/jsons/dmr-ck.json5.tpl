// uv run flowjson --workflowJsonAddress dmr-ck.json5 --imagesDirPath $PWD/src/common/images/dmr/ck --isDebug
/** 时间间隔 */
const delayInterval = 0.5
/** 点击房子到首页 */
const goToHomePageJobs = [
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: {
          uri: 'job1/12-1-home-click.png',
          confidence: 0.75,
        },
      },
    },
    action: {
      type: 'click',
    },
  },
]
/** 在抽卡页面选择金币抽卡并点击 */
const selectTheGoldDrawCardAndClickJobs = [
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        // 使用M币位置更准确
        position: 'job1/2-1-mb-move.png',
      },
    },
    action: {
      type: 'moveTo',
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    action: {
      type: 'move',
      arguments: {
        xOffset: -300,
        yOffset: 130,
      },
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    action: {
      type: 'scroll',
      // 滚动 向下滚动 wins是 完全一致
      arguments: [-9999],
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job1/3-1-jbck-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job1/4-2-10ck-click.png',
        includes: ['job1/4-1-jbck-tip-include.png'],
      },
    },
    action: {
      type: 'click',
    },
  },
]
/** 金币抽卡 */
const goldCardJobs = [
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job1/1-1-ck-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
  ...selectTheGoldDrawCardAndClickJobs,
  {
    delay: {
      next: delayInterval,
    },
    loop: {
      exitCondition: {
        image: {
          includes: [
            'job1/11-1-stash-full-include.png',
            'job1/11-2-stash-full-no-click.png',
          ],
        },
      },
    },
    jobs: [
      {
        delay: {
          next: delayInterval,
        },
        condition: {
          image: {
            position: 'job1/5-2-max-click.png',
            includes: ['job1/5-1-ck-tip-include.png'],
          },
        },
        action: {
          type: 'click',
        },
      },
      {
        delay: {
          next: delayInterval,
        },
        condition: {
          image: {
            // 点击后要等待很长时间
            position: 'job1/6-2-yes-click.png',
            includes: ['job1/6-1-ck-inquire-include.png'],
          },
        },
        action: {
          type: 'click',
        },
        loop: {
          exitCondition: {
            image: {
              includes: [
                'job1/7-2-close-click.png',
                'job1/7-1-res-list-include.png',
              ],
              excludes: 'job1/7-3-manle-exclude.png',
            },
          },
        },
        jobs: [
          {
            // 空任务
            delay: {
              next: 1,
            },
          },
        ],
      },
      {
        delay: {
          next: delayInterval,
        },
        condition: {
          image: {
            position: 'job1/7-2-close-click.png',
            includes: 'job1/7-1-res-list-include.png',
          },
        },
        action: {
          type: 'click',
        },
      },
      {
        delay: {
          next: delayInterval,
        },
        condition: {
          image: {
            position: 'job1/8-4-backward-click.png',
            includes: [
              'job1/8-1-ck-res-include.png',
              'job1/8-2-0ck-bright-include.png',
              'job1/8-3-remain-ckcs-include.png',
            ],
          },
        },
        action: {
          type: 'click',
        },
      },
      ...selectTheGoldDrawCardAndClickJobs,
    ],
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job1/11-2-stash-full-no-click.png',
        includes: ['job1/11-1-stash-full-include.png'],
      },
    },
    action: {
      type: 'click',
    },
  },
  ...goToHomePageJobs,
]
/** 点击分解 选择N */
const salvageSelectNJobs = [
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job2/2-1-decomposition-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job2/3-1-n-unselected-click.png',
        includes: ['job2/3-2-please-select-include.png'],
      },
    },
    action: {
      type: 'click',
    },
  },
  // 移动到分解 防止 验证N 匹配鼠标遮挡
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job2/3-3-fj-move.png',
      },
    },
    action: {
      type: 'moveTo',
    },
  },
]
/** 进入仓库 */
const enterTheWarehouseJobs = [
  {
    delay: {
      next: 1,
    },
    condition: {
      image: {
        position: 'job2/1-1-warehouse-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
]
/** 分解武器 */
const disassemblyWeaponJobs = [
  ...enterTheWarehouseJobs,
  ...salvageSelectNJobs,
  {
    loop: {
      exitCondition: {
        image: {
          includes: [
            {
              uri: 'job2/7-1-n-selected-include.png',
              // 0.99 是能够区分出 是已经选中 还是未选中
              confidence: 0.99,
            },
            'job2/3-2-please-select-include.png',
          ],
        },
      },
    },
    jobs: [
      {
        condition: {
          image: {
            // 确认
            position: 'job2/4-2-yes-click.png',
            excludes: ['job2/3-2-please-select-include.png'],
          },
        },
        action: {
          type: 'click',
        },
        // 如果 condition 不满足 jobs也不执行
        jobs: [
          {
            delay: {
              pre: delayInterval,
              next: delayInterval,
            },
            // 因为上一步 点击位置 和 下一步位置重合了 鼠标会影响截图 这里重置下
            action: {
              type: 'move',
              arguments: {
                xOffset: 0,
                yOffset: -100,
              },
            },
          },
          {
            delay: {
              next: delayInterval,
            },
            condition: {
              image: {
                // 二次确认
                position: 'job2/4-1-double-yes-click.png',
              },
            },
            action: {
              type: 'click',
            },
          },
          {
            // 去掉 分解完毕 提示
            delay: {
              // 确保上一步 一定是 做完了
              pre: 1,
              next: delayInterval,
            },
            condition: {
              image: {
                position: {
                  uri: 'job2/6-1-breakdown-prompt-click.png',
                  // 低精度 有背景
                  confidence: 0.8,
                },
              },
            },
            action: {
              type: 'click',
            },
          },
          ...salvageSelectNJobs,
        ],
      },
    ],
  },
  ...goToHomePageJobs,
]
/** 点击出售 选择N 选择R */
const sellSelectNRJobs = [
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job3/2-1-sell-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: {
          uri: 'job3/3-1-n-unselected-click.png',
          confidence: 0.99,
        },
      },
    },
    action: {
      type: 'click',
    },
  },
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: {
          uri: 'job3/3-2-r-unselected-click.png',
          confidence: 0.99,
        },
      },
    },
    action: {
      type: 'click',
    },
  },
  // 点击后 有可能出现提示 选取已达上限
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: {
          uri: 'job3/3-3-limit-tip.png',
        },
      },
    },
    action: {
      type: 'click',
    },
  },
  // 移动到贩卖 防止 验证N/R 匹配鼠标遮挡
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job3/3-4-fm-move.png',
      },
    },
    action: {
      type: 'moveTo',
    },
  },
]
/** 出售勾玉 */
const sellMagatamaJobs = [
  ...enterTheWarehouseJobs,
  {
    delay: {
      next: delayInterval,
    },
    condition: {
      image: {
        position: 'job3/1-1-gouguette-click.png',
      },
    },
    action: {
      type: 'click',
    },
  },
  ...sellSelectNRJobs,
  {
    loop: {
      exitCondition: {
        image: {
          includes: [
            {
              uri: 'job3/7-1-n-selected-include.png',
              confidence: 0.99,
            },
            'job2/3-2-please-select-include.png',
          ],
        },
      },
    },
    jobs: [
      {
        condition: {
          image: {
            // 确认
            position: 'job3/4-2-yes-click.png',
            excludes: ['job2/3-2-please-select-include.png'],
          },
        },
        action: {
          type: 'click',
        },
        // 如果 condition 不满足 jobs也不执行
        jobs: [
          {
            delay: {
              pre: delayInterval,
              next: delayInterval,
            },
            // 因为上一步 点击位置 和 下一步位置重合了 鼠标会影响截图 这里重置下
            action: {
              type: 'move',
              arguments: {
                xOffset: 0,
                yOffset: -100,
              },
            },
          },
          {
            delay: {
              next: 1,
            },
            condition: {
              image: {
                // 二次确认
                position: 'job2/4-1-double-yes-click.png',
              },
            },
            action: {
              type: 'click',
            },
          },
          {
            delay: {
              // 确保一定是 做完了
              next: 1,
            },
            condition: {
              image: {
                // 二次确认
                position: 'job3/5-1-double-yes-click.png',
              },
            },
            action: {
              type: 'click',
            },
          },
          {
            delay: {
              next: delayInterval,
            },
            // 贩卖成功 tip
            condition: {
              image: {
                position: 'job3/5-2-successfulsale-tip-click.png',
              },
            },
            action: {
              type: 'click',
            },
          },
          ...sellSelectNRJobs,
        ],
      },
    ],
  },
  ...goToHomePageJobs,
]

const Workflows = [
  {
    delay: {
      next: 2,
    },
  },
  {
    // 无限循环
    loop: {},
    jobs: [...goldCardJobs, ...disassemblyWeaponJobs, ...sellMagatamaJobs],
  },
]

console.log({
  goldCardJobs,
  disassemblyWeaponJobs,
  sellMagatamaJobs,
  Workflows,
})
