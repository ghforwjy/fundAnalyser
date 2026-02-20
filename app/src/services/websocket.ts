/**
 * WebSocket 服务 - 同步进度实时推送
 */

export type ProgressEventType = 
  | 'connected'
  | 'fetch_start'
  | 'fetch_progress'
  | 'fetch_complete'
  | 'save_start'
  | 'save_progress'
  | 'save_complete'
  | 'error'
  | 'info'
  | 'pong';

export interface ProgressEvent {
  type: ProgressEventType;
  message: string;
  current?: number;
  total?: number;
  timestamp?: string;
  sync_id?: string;
  inserted?: number;
  updated?: number;
}

type ProgressCallback = (event: ProgressEvent) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private callbacks: Set<ProgressCallback> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private url: string;

  constructor() {
    // 根据当前环境确定 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = `${protocol}//${host}/ws/sync-progress`;
  }

  /**
   * 连接 WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] 已经连接');
      return;
    }

    console.log('[WebSocket] 正在连接...', this.url);
    
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[WebSocket] 连接成功');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data: ProgressEvent = JSON.parse(event.data);
          console.log('[WebSocket] 收到消息:', data);
          this.notifyCallbacks(data);
        } catch (error) {
          console.error('[WebSocket] 消息解析失败:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[WebSocket] 连接错误:', error);
      };

      this.ws.onclose = () => {
        console.log('[WebSocket] 连接关闭');
        this.ws = null;
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('[WebSocket] 连接失败:', error);
      this.attemptReconnect();
    }
  }

  /**
   * 尝试重新连接
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] 达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[WebSocket] ${this.reconnectDelay}ms 后尝试第 ${this.reconnectAttempts} 次重连...`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * 注册进度回调
   */
  onProgress(callback: ProgressCallback): () => void {
    this.callbacks.add(callback);
    return () => {
      this.callbacks.delete(callback);
    };
  }

  /**
   * 通知所有回调
   */
  private notifyCallbacks(event: ProgressEvent): void {
    this.callbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('[WebSocket] 回调执行失败:', error);
      }
    });
  }

  /**
   * 发送 ping
   */
  ping(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send('ping');
    }
  }

  /**
   * 检查连接状态
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// 单例实例
export const wsService = new WebSocketService();
