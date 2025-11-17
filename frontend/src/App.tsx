import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'
import { createTask, fetchTasks } from './api'
import type { CreateTaskMetadata, VideoTask } from './types'

const defaultMetadata: CreateTaskMetadata = {
  title: '',
  description: '',
  language: 'zh',
  voice_profile: 'narrator_female',
  target_duration: 90,
}

function App() {
  const [metadata, setMetadata] = useState<CreateTaskMetadata>(defaultMetadata)
  const [file, setFile] = useState<File | null>(null)
  const [tasks, setTasks] = useState<VideoTask[]>([])
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const selectedTask = useMemo(() => {
    if (!tasks.length) return null
    return tasks.find((task) => task.id === selectedTaskId) ?? tasks[0]
  }, [tasks, selectedTaskId])

  const loadTasks = useCallback(async () => {
    try {
      const data = await fetchTasks()
      setTasks(data)
      if (!selectedTaskId && data.length) {
        setSelectedTaskId(data[0].id)
      }
    } catch (err) {
      console.error(err)
    }
  }, [selectedTaskId])

  useEffect(() => {
    loadTasks()
    const interval = setInterval(loadTasks, 5000)
    return () => clearInterval(interval)
  }, [loadTasks])

  const handleInputChange = (key: keyof CreateTaskMetadata, value: string | number) => {
    setMetadata((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!metadata.title || !file) {
      setError('请填写标题并选择源视频文件')
      return
    }
    setLoading(true)
    setError(null)
    setSuccessMessage(null)
    try {
      await createTask(metadata, file)
      setSuccessMessage('任务已提交，稍后即可查看进度')
      setMetadata(defaultMetadata)
      setFile(null)
      await loadTasks()
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建任务失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <div>
          <p className="eyebrow">TV Commentary Studio</p>
          <h1>电视剧解说短视频自动化工作台</h1>
          <p className="subtitle">
            导入长视频 → 智能解析剧情 → 生成解说脚本 → 自动剪辑与配音，一站式完成创作。
          </p>
        </div>
      </header>

      <main>
        <section className="panel">
          <h2>1. 上传素材并配置解说风格</h2>
          <form className="task-form" onSubmit={handleSubmit}>
            <label>
              标题
              <input
                type="text"
                value={metadata.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="示例：第 12 集反转解说"
                required
              />
            </label>

            <label>
              内容概述
              <textarea
                value={metadata.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="可输入剧情概况、需要强调的角色或情绪"
                rows={3}
              />
            </label>

            <div className="grid-2">
              <label>
                输出语言
                <select
                  value={metadata.language}
                  onChange={(e) => handleInputChange('language', e.target.value)}
                >
                  <option value="zh">中文</option>
                  <option value="en">English</option>
                </select>
              </label>

              <label>
                目标时长（秒）
                <input
                  type="number"
                  min={30}
                  max={300}
                  value={metadata.target_duration}
                  onChange={(e) => handleInputChange('target_duration', Number(e.target.value))}
                />
              </label>
            </div>

            <label>
              语音音色
              <select
                value={metadata.voice_profile}
                onChange={(e) => handleInputChange('voice_profile', e.target.value)}
              >
                <option value="narrator_female">温柔女声</option>
                <option value="narrator_male">沉稳男声</option>
                <option value="dynamic_storyteller">激情解说</option>
              </select>
            </label>

            <label className="upload">
              源视频文件
              <input type="file" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </label>

            {error && <p className="message error">{error}</p>}
            {successMessage && <p className="message success">{successMessage}</p>}

            <button type="submit" disabled={loading}>
              {loading ? '提交中...' : '提交任务'}
            </button>
          </form>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>2. 任务进度面板</h2>
              <p className="subtitle">实时查看解析进度与自动生成的脚本片段</p>
            </div>
            <button className="ghost" onClick={loadTasks}>
              刷新
            </button>
          </div>

          <div className="task-layout">
            <aside>
              {tasks.length === 0 && <p className="placeholder">暂时没有任务</p>}
              {tasks.map((task) => (
                <button
                  key={task.id}
                  className={`task-card ${selectedTask?.id === task.id ? 'active' : ''}`}
                  onClick={() => setSelectedTaskId(task.id)}
                >
                  <div className="task-status-line">
                    <span className={`status-dot status-${task.status}`} />
                    <span>{task.status}</span>
                    <span className="time">{new Date(task.created_at).toLocaleString()}</span>
                  </div>
                  <p className="task-title">{task.source_asset?.url ?? '未命名任务'}</p>
                  <div className="progress">
                    <div style={{ width: `${Math.round(task.progress * 100)}%` }} />
                  </div>
                </button>
              ))}
            </aside>

            <article>
              {!selectedTask && <p className="placeholder">请选择任务查看详情</p>}
              {selectedTask && (
                <div className="task-details">
                  <div className="detail-row">
                    <h3>当前状态</h3>
                    <span className={`status-chip status-${selectedTask.status}`}>
                      {selectedTask.status}
                    </span>
                  </div>
                  <p>
                    更新时间：{new Date(selectedTask.updated_at).toLocaleString()} | 进度：
                    {Math.round(selectedTask.progress * 100)}%
                  </p>

                  {selectedTask.output_asset && (
                    <a className="primary-link" href={selectedTask.output_asset.url}>
                      查看生成视频
                    </a>
                  )}

                  <h4>自动生成的解说脚本</h4>
                  {selectedTask.script.length === 0 && (
                    <p className="placeholder">脚本生成中...</p>
                  )}
                  <ul className="script-list">
                    {selectedTask.script.map((segment) => (
                      <li key={segment.order}>
                        <div>
                          <strong>
                            第 {segment.order} 段 · {segment.start.toFixed(0)}s - {segment.end.toFixed(0)}s
                          </strong>
                          <span>{segment.emotion}</span>
                        </div>
                        <p>{segment.text}</p>
                        <p className="keywords">关键词：{segment.keywords.join('、')}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
