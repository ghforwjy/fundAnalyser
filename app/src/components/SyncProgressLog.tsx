import React, { useEffect, useRef, useState } from 'react';
import { wsService, type ProgressEvent, type ProgressEventType } from '../services/websocket';

interface LogEntry {
  id: number;
  type: ProgressEventType;
  message: string;
  timestamp: string;
  current?: number;
  total?: number;
}

interface SyncProgressLogProps {
  visible: boolean;
}

const SyncProgressLog: React.FC<SyncProgressLogProps> = ({ visible }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logIdRef = useRef(0);

  useEffect(() => {
    if (!visible) return;

    // 连接 WebSocket
    wsService.connect();

    // 注册进度回调
    const unsubscribe = wsService.onProgress((event: ProgressEvent) => {
      const newLog: LogEntry = {
        id: ++logIdRef.current,
        type: event.type,
        message: event.message,
        timestamp: event.timestamp || new Date().toLocaleTimeString(),
        current: event.current,
        total: event.total,
      };

      setLogs(prev => [...prev.slice(-99), newLog]); // 保留最近 100 条

      if (event.type === 'connected') {
        setIsConnected(true);
      }
    });

    // 检查连接状态
    setIsConnected(wsService.isConnected());

    return () => {
      unsubscribe();
    };
  }, [visible]);

  // 自动滚动到底部
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // 清空日志
  const clearLogs = () => {
    setLogs([]);
  };

  // 获取日志类型对应的样式
  const getLogStyle = (type: ProgressEventType): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      padding: '4px 8px',
      borderRadius: '4px',
      marginBottom: '4px',
      fontSize: '13px',
      fontFamily: 'monospace',
    };

    switch (type) {
      case 'fetch_start':
      case 'save_start':
        return { ...baseStyle, backgroundColor: '#e6f7ff', color: '#096dd9' };
      case 'fetch_progress':
      case 'save_progress':
        return { ...baseStyle, backgroundColor: '#f6ffed', color: '#389e0d' };
      case 'fetch_complete':
      case 'save_complete':
        return { ...baseStyle, backgroundColor: '#f6ffed', color: '#389e0d', fontWeight: 'bold' };
      case 'error':
        return { ...baseStyle, backgroundColor: '#fff2f0', color: '#cf1322' };
      case 'connected':
        return { ...baseStyle, backgroundColor: '#f9f0ff', color: '#531dab' };
      default:
        return { ...baseStyle, color: '#595959' };
    }
  };

  // 获取类型标签
  const getTypeLabel = (type: ProgressEventType): string => {
    switch (type) {
      case 'fetch_start': return '[获取]';
      case 'fetch_progress': return '[进度]';
      case 'fetch_complete': return '[完成]';
      case 'save_start': return '[保存]';
      case 'save_progress': return '[进度]';
      case 'save_complete': return '[完成]';
      case 'error': return '[错误]';
      case 'connected': return '[连接]';
      case 'info': return '[信息]';
      default: return '';
    }
  };

  if (!visible) return null;

  return (
    <div style={{
      marginTop: '16px',
      border: '1px solid #d9d9d9',
      borderRadius: '8px',
      backgroundColor: '#fafafa',
    }}>
      {/* 头部 */}
      <div style={{
        padding: '8px 12px',
        borderBottom: '1px solid #d9d9d9',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#f0f0f0',
        borderRadius: '8px 8px 0 0',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: 'bold', fontSize: '14px' }}>同步详细日志</span>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isConnected ? '#52c41a' : '#ff4d4f',
            display: 'inline-block',
          }} />
          <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {isConnected ? '已连接' : '未连接'}
          </span>
        </div>
        <button
          onClick={clearLogs}
          style={{
            padding: '4px 12px',
            fontSize: '12px',
            border: '1px solid #d9d9d9',
            borderRadius: '4px',
            backgroundColor: '#fff',
            cursor: 'pointer',
          }}
        >
          清空日志
        </button>
      </div>

      {/* 日志列表 */}
      <div style={{
        maxHeight: '300px',
        overflowY: 'auto',
        padding: '8px',
      }}>
        {logs.length === 0 ? (
          <div style={{
            textAlign: 'center',
            color: '#bfbfbf',
            padding: '40px',
            fontSize: '14px',
          }}>
            等待同步开始...
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} style={getLogStyle(log.type)}>
              <span style={{ color: '#8c8c8c', marginRight: '8px' }}>
                {log.timestamp}
              </span>
              <span style={{ marginRight: '8px', fontWeight: 'bold' }}>
                {getTypeLabel(log.type)}
              </span>
              <span>{log.message}</span>
              {log.current !== undefined && log.total !== undefined && (
                <span style={{ marginLeft: '8px', color: '#8c8c8c' }}>
                  ({log.current}/{log.total})
                </span>
              )}
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default SyncProgressLog;
