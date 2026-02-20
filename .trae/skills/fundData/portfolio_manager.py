"""
组合管理模块
提供组合管理、成分基金管理、持仓历史记录、持仓计算等功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class PortfolioManager:
    """组合管理类"""
    
    # ==================== 组合管理接口 ====================
    
    def create_portfolio(self, name: str, description: str = None) -> Dict[str, Any]:
        """
        创建组合
        
        Args:
            name: 组合名称
            description: 组合描述（可选）
        
        Returns:
            创建的组合信息
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO portfolio (name, description)
                    VALUES (?, ?)
                ''', (name, description))
                conn.commit()
                
                portfolio_id = cursor.lastrowid
                return {
                    'success': True,
                    'portfolio_id': portfolio_id,
                    'name': name,
                    'description': description
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def delete_portfolio(self, portfolio_id: int) -> Dict[str, Any]:
        """
        删除组合
        
        Args:
            portfolio_id: 组合ID
        
        Returns:
            删除结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM portfolio WHERE id = ?', (portfolio_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': '组合不存在'}
            
            portfolio_name = row['name']
            cursor.execute('DELETE FROM portfolio WHERE id = ?', (portfolio_id,))
            conn.commit()
            
            return {
                'success': True,
                'deleted_portfolio_id': portfolio_id,
                'deleted_portfolio_name': portfolio_name
            }
    
    def rename_portfolio(self, portfolio_id: int, new_name: str) -> Dict[str, Any]:
        """
        重命名组合
        
        Args:
            portfolio_id: 组合ID
            new_name: 新名称
        
        Returns:
            更新结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE portfolio SET name = ?, update_time = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_name, portfolio_id))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return {'success': False, 'error': '组合不存在'}
                
                return {
                    'success': True,
                    'portfolio_id': portfolio_id,
                    'new_name': new_name
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def update_portfolio_description(self, portfolio_id: int, description: str) -> Dict[str, Any]:
        """
        更新组合描述
        
        Args:
            portfolio_id: 组合ID
            description: 新描述
        
        Returns:
            更新结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE portfolio SET description = ?, update_time = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (description, portfolio_id))
            conn.commit()
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': '组合不存在'}
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'description': description
            }
    
    def list_portfolios(self) -> List[Dict[str, Any]]:
        """
        查询所有组合
        
        Returns:
            组合列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM portfolio_fund WHERE portfolio_id = p.id) as fund_count
                FROM portfolio p
                ORDER BY p.create_time DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """
        获取组合详情
        
        Args:
            portfolio_id: 组合ID
        
        Returns:
            组合详情
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM portfolio_fund WHERE portfolio_id = p.id) as fund_count
                FROM portfolio p
                WHERE p.id = ?
            ''', (portfolio_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== 成分基金管理接口 ====================
    
    def _add_single_fund(self, portfolio_id: int, fund_code: str,
                         buy_date: str = None, buy_nav: float = None,
                         shares: float = None,
                         notes: str = None) -> Dict[str, Any]:
        """
        内部方法：添加单只基金（不对外暴露）
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            buy_date: 买入日期
            buy_nav: 买入净值
            shares: 持有份额
            notes: 备注
        
        Returns:
            添加结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM portfolio WHERE id = ?', (portfolio_id,))
            if not cursor.fetchone():
                return {'success': False, 'error': '组合不存在'}
            
            fund_name = self._get_fund_name(fund_code)
            
            try:
                cursor.execute('''
                    INSERT INTO portfolio_fund 
                    (portfolio_id, fund_code, fund_name, buy_date, buy_nav, shares, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (portfolio_id, fund_code, fund_name, buy_date, buy_nav, shares, notes))
                conn.commit()
                
                # 如果传入了份额，自动记录持仓快照
                if shares is not None and shares > 0:
                    self.record_holding(
                        portfolio_id=portfolio_id,
                        fund_code=fund_code,
                        shares=shares,
                        record_date=buy_date,
                        notes='初始持仓导入' if not notes else notes
                    )
                
                return {
                    'success': True,
                    'fund_code': fund_code,
                    'fund_name': fund_name
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def add_funds_to_portfolio(self, portfolio_id: int,
                                holdings: Dict[str, Dict[str, any]],
                                exclude_money_market: bool = True) -> Dict[str, Any]:
        """
        批量添加成分基金（支持单只或批量）
        
        Args:
            portfolio_id: 组合ID
            holdings: 持仓数据字典，格式为 {
                fund_code: {
                    'shares': 份额,
                    'amount': 金额,
                    'buy_date': 买入日期,
                    'buy_nav': 买入净值,
                    'notes': 备注
                }
            }
            exclude_money_market: 是否排除货币基金（默认True）
        
        Returns:
            添加结果
        """
        results = {
            'success_count': 0,
            'failed_count': 0,
            'excluded_count': 0,
            'details': []
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM portfolio WHERE id = ?', (portfolio_id,))
            if not cursor.fetchone():
                return {'success': False, 'error': '组合不存在'}
            
            for fund_code, data in holdings.items():
                if exclude_money_market:
                    fund_type = self._get_fund_type(fund_code)
                    if fund_type and '货币' in fund_type:
                        results['excluded_count'] += 1
                        results['details'].append({
                            'fund_code': fund_code,
                            'status': 'excluded',
                            'reason': '货币基金已排除'
                        })
                        continue
                
                # 获取持仓数据（废弃amount字段）
                shares = data.get('shares') if isinstance(data, dict) else None
                buy_date = data.get('buy_date') if isinstance(data, dict) else None
                buy_nav = data.get('buy_nav') if isinstance(data, dict) else None
                notes = data.get('notes') if isinstance(data, dict) else None
                
                result = self._add_single_fund(
                    portfolio_id, fund_code,
                    buy_date=buy_date,
                    buy_nav=buy_nav,
                    shares=shares,
                    notes=notes
                )
                if result['success']:
                    results['success_count'] += 1
                    results['details'].append({
                        'fund_code': fund_code,
                        'status': 'success'
                    })
                else:
                    results['failed_count'] += 1
                    results['details'].append({
                        'fund_code': fund_code,
                        'status': 'failed',
                        'error': result.get('error')
                    })
        
        return results
    
    def remove_fund_from_portfolio(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        """
        移除成分基金
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
        
        Returns:
            移除结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM portfolio_fund 
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            conn.commit()
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': '成分基金不存在'}
            
            return {
                'success': True,
                'removed_fund_code': fund_code
            }
    
    def update_portfolio_fund(self, portfolio_id: int, fund_code: str,
                               **kwargs) -> Dict[str, Any]:
        """
        更新成分基金
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            **kwargs: 可更新字段（buy_date, buy_nav, shares, amount, notes）
        
        Returns:
            更新结果
        """
        allowed_fields = ['buy_date', 'buy_nav', 'shares', 'amount', 'notes']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return {'success': False, 'error': '没有可更新的字段'}
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
            set_clause += ', update_time = CURRENT_TIMESTAMP'
            
            values = list(update_fields.values()) + [portfolio_id, fund_code]
            
            cursor.execute(f'''
                UPDATE portfolio_fund SET {set_clause}
                WHERE portfolio_id = ? AND fund_code = ?
            ''', values)
            conn.commit()
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': '成分基金不存在'}
            
            # 如果更新了份额，自动记录持仓快照
            if 'shares' in update_fields and update_fields['shares'] is not None:
                self.record_holding(
                    portfolio_id=portfolio_id,
                    fund_code=fund_code,
                    shares=update_fields['shares'],
                    record_date=update_fields.get('buy_date'),
                    notes='持仓更新' if 'notes' not in update_fields else update_fields['notes']
                )
            
            return {
                'success': True,
                'updated_fields': list(update_fields.keys())
            }
    
    def list_portfolio_funds(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        查询组合成分基金
        
        Args:
            portfolio_id: 组合ID
        
        Returns:
            成分基金列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM portfolio_fund
                WHERE portfolio_id = ?
                ORDER BY fund_code
            ''', (portfolio_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def refresh_portfolio_fund_metrics(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        """
        刷新单只基金指标
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
        
        Returns:
            刷新结果
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT period, period_return, rank_in_category 
                FROM fund_performance 
                WHERE fund_code = ? AND performance_type = '阶段业绩'
            ''', (fund_code,))
            perf_rows = cursor.fetchall()
            
            cursor.execute('''
                SELECT period, max_drawdown, sharpe_ratio, annual_volatility
                FROM fund_risk_metrics
                WHERE fund_code = ?
            ''', (fund_code,))
            risk_rows = cursor.fetchall()
            
            # 如果没有数据，尝试同步
            if not perf_rows or not risk_rows:
                try:
                    from syncers.group_syncers import sync_single_fund_performance, sync_single_fund_risk
                    
                    if not perf_rows:
                        perf_result = sync_single_fund_performance(fund_code)
                        if perf_result.get('success'):
                            # 重新查询
                            cursor.execute('''
                                SELECT period, period_return, rank_in_category 
                                FROM fund_performance 
                                WHERE fund_code = ? AND performance_type = '阶段业绩'
                            ''', (fund_code,))
                            perf_rows = cursor.fetchall()
                    
                    if not risk_rows:
                        risk_result = sync_single_fund_risk(fund_code)
                        if risk_result.get('success'):
                            # 重新查询
                            cursor.execute('''
                                SELECT period, max_drawdown, sharpe_ratio, annual_volatility
                                FROM fund_risk_metrics
                                WHERE fund_code = ?
                            ''', (fund_code,))
                            risk_rows = cursor.fetchall()
                        else:
                            # 雪球获取失败，使用自计算
                            print(f"[PortfolioManager] 雪球风险指标获取失败，尝试自计算 {fund_code}")
                            from risk_metrics_calculator import calculate_fund_risk_metrics
                            calc_result = calculate_fund_risk_metrics(fund_code, '近1年')
                            if calc_result.get('success'):
                                # 重新查询（自计算结果已存入数据库）
                                cursor.execute('''
                                    SELECT period, max_drawdown, sharpe_ratio, annual_volatility
                                    FROM fund_risk_metrics
                                    WHERE fund_code = ?
                                ''', (fund_code,))
                                risk_rows = cursor.fetchall()
                except Exception as e:
                    print(f"[PortfolioManager] 同步基金指标失败 {fund_code}: {e}")
            
            updates = {}
            
            for row in perf_rows:
                period = row['period']
                if period == '近1月':
                    updates['return_1m'] = row['period_return']
                elif period == '近6月':
                    updates['return_6m'] = row['period_return']
                elif period == '近1年':
                    updates['return_1y'] = row['period_return']
                    updates['rank_in_category'] = row['rank_in_category']
            
            for row in risk_rows:
                period = row['period']
                if period == '近1年':
                    updates['max_drawdown_1y'] = row['max_drawdown']
                    updates['sharpe_ratio_1y'] = row['sharpe_ratio']
                    updates['annual_volatility_1y'] = row['annual_volatility']
            
            fund_info = self._get_fund_info(fund_code)
            if fund_info:
                updates['rank_category'] = fund_info.get('fund_type')
            
            if updates:
                updates['metrics_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
                values = list(updates.values()) + [portfolio_id, fund_code]
                
                cursor.execute(f'''
                    UPDATE portfolio_fund SET {set_clause}
                    WHERE portfolio_id = ? AND fund_code = ?
                ''', values)
                conn.commit()
            
            return {
                'success': True,
                'fund_code': fund_code,
                'updated_fields': list(updates.keys()) if updates else []
            }
    
    def refresh_portfolio_metrics(self, portfolio_id: int, force: bool = False) -> Dict[str, Any]:
        """
        刷新组合所有基金指标
        
        Args:
            portfolio_id: 组合ID
            force: 是否强制刷新（忽略新鲜度判断）
        
        Returns:
            刷新结果
        """
        results = {
            'updated_count': 0,
            'cached_count': 0,
            'failed_count': 0,
            'details': []
        }
        
        funds = self.list_portfolio_funds(portfolio_id)
        
        for fund in funds:
            fund_code = fund['fund_code']
            metrics_time = fund.get('metrics_update_time')
            
            need_update = force
            if not force and metrics_time:
                try:
                    last_update = datetime.strptime(metrics_time, '%Y-%m-%d %H:%M:%S')
                    if datetime.now() - last_update > timedelta(hours=12):
                        need_update = True
                except:
                    need_update = True
            elif not metrics_time:
                need_update = True
            
            if need_update:
                result = self.refresh_portfolio_fund_metrics(portfolio_id, fund_code)
                if result['success']:
                    results['updated_count'] += 1
                else:
                    results['failed_count'] += 1
                results['details'].append({
                    'fund_code': fund_code,
                    'status': 'updated' if result['success'] else 'failed'
                })
            else:
                results['cached_count'] += 1
                results['details'].append({
                    'fund_code': fund_code,
                    'status': 'cached'
                })
        
        return results
    
    # ==================== 持仓历史记录接口 ====================
    
    def record_holding(self, portfolio_id: int, fund_code: str, shares: float,
                        record_date: str = None, notes: str = None) -> Dict[str, Any]:
        """
        记录持仓快照
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            shares: 持有份额
            record_date: 记录日期（可选，默认今天）
            notes: 备注
        
        Returns:
            记录结果
        """
        if not record_date:
            record_date = datetime.now().strftime('%Y-%m-%d')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT shares FROM holding_history
                WHERE portfolio_id = ? AND fund_code = ? AND record_date < ?
                ORDER BY record_date DESC LIMIT 1
            ''', (portfolio_id, fund_code, record_date))
            last_record = cursor.fetchone()
            
            shares_change = None
            if last_record:
                shares_change = shares - last_record['shares']
            
            nav = self._get_nav_at_date(fund_code, record_date)

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO holding_history
                    (portfolio_id, fund_code, record_date, shares, nav, shares_change, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (portfolio_id, fund_code, record_date, shares, nav, shares_change, notes))
                conn.commit()

                cursor.execute('''
                    UPDATE portfolio_fund SET shares = ?, update_time = CURRENT_TIMESTAMP
                    WHERE portfolio_id = ? AND fund_code = ?
                ''', (shares, portfolio_id, fund_code))
                conn.commit()

                # 市值实时计算，不存储
                market_value = shares * nav if nav else None

                return {
                    'success': True,
                    'record_date': record_date,
                    'shares': shares,
                    'nav': nav,
                    'market_value': market_value,
                    'shares_change': shares_change
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_holding_history(self, portfolio_id: int, fund_code: str = None,
                             start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        查询持仓历史
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        
        Returns:
            持仓历史列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM holding_history WHERE portfolio_id = ?'
            params = [portfolio_id]
            
            if fund_code:
                query += ' AND fund_code = ?'
                params.append(fund_code)
            
            if start_date:
                query += ' AND record_date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND record_date <= ?'
                params.append(end_date)
            
            query += ' ORDER BY record_date DESC, fund_code'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_latest_holding(self, portfolio_id: int, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取最近一次持仓记录
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
        
        Returns:
            最近持仓记录
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM holding_history
                WHERE portfolio_id = ? AND fund_code = ?
                ORDER BY record_date DESC LIMIT 1
            ''', (portfolio_id, fund_code))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== 持仓计算接口 ====================
    
    def get_shares_at_date(self, portfolio_id: int, fund_code: str, target_date: str) -> Optional[float]:
        """
        获取指定日期的份额
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            target_date: 目标日期
        
        Returns:
            份额
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT shares FROM holding_history
                WHERE portfolio_id = ? AND fund_code = ? AND record_date <= ?
                ORDER BY record_date DESC LIMIT 1
            ''', (portfolio_id, fund_code, target_date))
            row = cursor.fetchone()
            return row['shares'] if row else None
    
    def get_market_value_at_date(self, portfolio_id: int, fund_code: str, target_date: str) -> Optional[Dict[str, Any]]:
        """
        获取指定日期的市值
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            target_date: 目标日期
        
        Returns:
            市值信息
        """
        shares = self.get_shares_at_date(portfolio_id, fund_code, target_date)
        if shares is None:
            return None
        
        nav = self._get_nav_at_date(fund_code, target_date)
        market_value = shares * nav if nav else None
        
        return {
            'fund_code': fund_code,
            'target_date': target_date,
            'shares': shares,
            'nav': nav,
            'market_value': market_value
        }
    
    def get_portfolio_value_at_date(self, portfolio_id: int, target_date: str) -> Dict[str, Any]:
        """
        获取组合在指定日期的总市值
        
        Args:
            portfolio_id: 组合ID
            target_date: 目标日期
        
        Returns:
            组合市值信息
        """
        funds = self.list_portfolio_funds(portfolio_id)
        
        total_value = 0
        fund_values = []
        
        for fund in funds:
            fund_code = fund['fund_code']
            value_info = self.get_market_value_at_date(portfolio_id, fund_code, target_date)
            
            if value_info and value_info['market_value']:
                total_value += value_info['market_value']
                fund_values.append({
                    'fund_code': fund_code,
                    'fund_name': fund['fund_name'],
                    'shares': value_info['shares'],
                    'nav': value_info['nav'],
                    'market_value': value_info['market_value']
                })
        
        return {
            'portfolio_id': portfolio_id,
            'target_date': target_date,
            'total_value': total_value,
            'fund_count': len(fund_values),
            'funds': fund_values
        }
    
    def calculate_profit_loss(self, portfolio_id: int, fund_code: str,
                               from_date: str, to_date: str = None) -> Dict[str, Any]:
        """
        计算指定时间段盈亏
        
        Args:
            portfolio_id: 组合ID
            fund_code: 基金代码
            from_date: 起始日期
            to_date: 结束日期（可选，默认当前）
        
        Returns:
            盈亏报告
        """
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        shares_from = self.get_shares_at_date(portfolio_id, fund_code, from_date)
        shares_to = self.get_shares_at_date(portfolio_id, fund_code, to_date)
        
        nav_from = self._get_nav_at_date(fund_code, from_date)
        nav_to = self._get_nav_at_date(fund_code, to_date)
        
        fund_name = self._get_fund_name(fund_code)
        
        result = {
            'fund_code': fund_code,
            'fund_name': fund_name,
            'from_date': from_date,
            'to_date': to_date,
            'shares_from': shares_from,
            'shares_to': shares_to,
            'nav_from': nav_from,
            'nav_to': nav_to,
            'value_from': None,
            'value_to': None,
            'shares_change': None,
            'profit_loss': None
        }
        
        if shares_from is not None and nav_from:
            result['value_from'] = shares_from * nav_from
        
        if shares_to is not None and nav_to:
            result['value_to'] = shares_to * nav_to
        
        if shares_from is not None and shares_to is not None:
            result['shares_change'] = shares_to - shares_from
        
        if result['value_from'] is not None and result['value_to'] is not None:
            result['profit_loss'] = result['value_to'] - result['value_from']
        
        return result
    
    def get_portfolio_profit_loss_report(self, portfolio_id: int, from_date: str,
                                          to_date: str = None) -> Dict[str, Any]:
        """
        获取组合盈亏报告
        
        Args:
            portfolio_id: 组合ID
            from_date: 起始日期
            to_date: 结束日期（可选，默认当前）
        
        Returns:
            组合盈亏报告
        """
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        portfolio = self.get_portfolio(portfolio_id)
        funds = self.list_portfolio_funds(portfolio_id)
        
        total_value_from = 0
        total_value_to = 0
        fund_reports = []
        
        for fund in funds:
            fund_code = fund['fund_code']
            report = self.calculate_profit_loss(portfolio_id, fund_code, from_date, to_date)
            
            if report['value_from']:
                total_value_from += report['value_from']
            if report['value_to']:
                total_value_to += report['value_to']
            
            fund_reports.append({
                'fund_code': fund_code,
                'fund_name': fund['fund_name'],
                'value_from': report['value_from'],
                'value_to': report['value_to'],
                'shares_change': report['shares_change'],
                'profit_loss': report['profit_loss']
            })
        
        return {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio['name'] if portfolio else None,
            'from_date': from_date,
            'to_date': to_date,
            'total_value_from': total_value_from,
            'total_value_to': total_value_to,
            'total_profit_loss': total_value_to - total_value_from,
            'funds': fund_reports
        }
    
    # ==================== 辅助方法 ====================
    
    def _get_fund_name(self, fund_code: str) -> Optional[str]:
        """获取基金名称"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT fund_name FROM fund_info WHERE fund_code = ?', (fund_code,))
            row = cursor.fetchone()
            return row['fund_name'] if row else None
    
    def _get_fund_type(self, fund_code: str) -> Optional[str]:
        """获取基金类型"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT fund_type FROM fund_info WHERE fund_code = ?', (fund_code,))
            row = cursor.fetchone()
            return row['fund_type'] if row else None
    
    def _get_fund_info(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """获取基金信息"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM fund_info WHERE fund_code = ?', (fund_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def _get_nav_at_date(self, fund_code: str, target_date: str) -> Optional[float]:
        """获取指定日期的净值"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT unit_nav FROM fund_nav
                WHERE fund_code = ? AND nav_date <= ?
                ORDER BY nav_date DESC LIMIT 1
            ''', (fund_code, target_date))
            row = cursor.fetchone()
            return row['unit_nav'] if row else None

    def _get_latest_nav(self, fund_code: str) -> Optional[float]:
        """获取基金最新净值"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT unit_nav FROM fund_nav
                WHERE fund_code = ?
                ORDER BY nav_date DESC LIMIT 1
            ''', (fund_code,))
            row = cursor.fetchone()
            return row['unit_nav'] if row else None

    def import_profit_data(self, portfolio_id: int, profit_data: List[Dict[str, Any]], 
                         import_date: str = None, import_mode: str = 'accumulate',
                         source_type: str = 'manual') -> Dict[str, Any]:
        """
        导入盈亏数据到指定组合
        
        Args:
            portfolio_id: 组合ID
            profit_data: 盈亏数据列表，每项包含：
                - fund_code: 基金代码
                - profit_loss: 持仓收益（正数表示盈利，负数表示亏损）
                - fund_name: 基金名称（可选）
                - current_value: 当前持有金额（已废弃，后端自动计算）
            import_date: 导入日期（默认今天）
            import_mode: 导入模式
                - 'overwrite': 覆盖模式，替换现有数据
                - 'accumulate': 累加模式，与现有数据累加（默认）
            source_type: 数据来源
        
        Returns:
            导入结果统计
        """
        if not import_date:
            import_date = datetime.now().strftime('%Y-%m-%d')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            success_count = 0
            fail_count = 0
            total_current_value = 0
            total_profit_loss = 0
            
            for fund in profit_data:
                try:
                    fund_code = fund.get('fund_code')
                    print(f"[import_profit_data] 处理基金: {fund_code}")
                    if not fund_code:
                        print(f"[import_profit_data] 错误: fund_code 为空")
                        fail_count += 1
                        continue
                    
                    profit_loss = fund.get('profit_loss', 0)
                    fund_name = fund.get('fund_name')
                    print(f"[import_profit_data] 盈亏: {profit_loss}, 基金名称: {fund_name}")
                    
                    # 获取基金份额和最新净值
                    cursor.execute(
                        "SELECT shares, fund_name FROM portfolio_fund WHERE portfolio_id = ? AND fund_code = ?",
                        (portfolio_id, fund_code)
                    )
                    row = cursor.fetchone()
                    print(f"[import_profit_data] 查询portfolio_fund: portfolio_id={portfolio_id}, fund_code={fund_code}, row={row}")
                    
                    if row:
                        shares = row['shares']
                        if not fund_name:
                            fund_name = row['fund_name']
                        print(f"[import_profit_data] 获取到份额: {shares}, 基金名称: {fund_name}")
                    else:
                        # 基金不存在，无法导入盈亏
                        print(f"[import_profit_data] 错误: 基金不存在于组合中")
                        fail_count += 1
                        continue
                    
                    # 查询最新净值
                    latest_nav = self._get_latest_nav(fund_code)
                    print(f"[import_profit_data] 最新净值: {latest_nav}")
                    if not latest_nav:
                        # 无法获取净值，尝试同步
                        print(f"[import_profit_data] 本地无净值数据，尝试同步...")
                        try:
                            from syncers.group_syncers import sync_single_fund_nav
                            sync_result = sync_single_fund_nav(fund_code)
                            if sync_result.get('success'):
                                # 重新查询
                                latest_nav = self._get_latest_nav(fund_code)
                                print(f"[import_profit_data] 同步后最新净值: {latest_nav}")
                        except Exception as e:
                            print(f"[import_profit_data] 同步净值失败: {e}")
                    
                    if not latest_nav:
                        # 仍然无法获取净值，跳过
                        print(f"[import_profit_data] 错误: 无法获取最新净值")
                        fail_count += 1
                        continue
                    
                    # 自动计算当前市值：shares × latest_nav
                    current_value = shares * latest_nav
                    print(f"[import_profit_data] 当前市值: {current_value} = {shares} × {latest_nav}")
                    
                    # 计算成本净值（摊薄后的买入净值）
                    # 公式：cost_nav = (current_value - profit_loss) / shares
                    # 盈利时 profit_loss 为正，成本 = 市值 - 盈利
                    # 亏损时 profit_loss 为负，成本 = 市值 - (-亏损) = 市值 + 亏损
                    cost_nav = (current_value - profit_loss) / shares if shares > 0 else 0
                    print(f"[import_profit_data] 成本净值计算: ({current_value} - {profit_loss}) / {shares} = {cost_nav}")
                    
                    print(f"[import_profit_data] 导入模式: {import_mode}, row是否存在: {row is not None}")
                    if import_mode == 'overwrite' or not row:
                        # 覆盖模式：直接用新的成本净值更新
                        # 盈亏将通过 buy_nav * shares 和 latest_nav * shares 实时计算
                        print(f"[import_profit_data] 执行覆盖模式: INSERT OR REPLACE buy_nav={cost_nav}, cost_nav={cost_nav}")
                        cursor.execute('''
                            INSERT OR REPLACE INTO portfolio_fund (
                                portfolio_id, fund_code, fund_name, shares, 
                                buy_nav, cost_nav, 
                                import_date, import_source, update_time
                            ) VALUES (
                                ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                            )
                        ''', (
                            portfolio_id, fund_code, fund_name, shares,
                            cost_nav, cost_nav,  # buy_nav和cost_nav相同，都是摊薄成本净值
                            import_date, source_type
                        ))
                        print(f"[import_profit_data] 覆盖模式执行完成, 影响行数: {cursor.rowcount}")
                    else:
                        # 累加模式：累加盈亏金额，重新计算成本净值
                        print(f"[import_profit_data] 执行累加模式")
                        cursor.execute(
                            "SELECT shares, buy_nav FROM portfolio_fund WHERE portfolio_id = ? AND fund_code = ?",
                            (portfolio_id, fund_code)
                        )
                        old_data = cursor.fetchone()
                        print(f"[import_profit_data] 累加模式查询旧数据: {old_data}")
                        if old_data:
                            # 获取现有持仓信息
                            old_shares = old_data['shares'] or 0
                            old_buy_nav = old_data['buy_nav'] or 0
                            print(f"[import_profit_data] 旧数据: shares={old_shares}, buy_nav={old_buy_nav}")
                            
                            # 计算现有成本
                            old_cost = old_shares * old_buy_nav
                            print(f"[import_profit_data] 旧成本: {old_cost}")
                            
                            # 累加盈亏：新的成本 = 原成本 - 新盈亏
                            # 盈利时 profit_loss 为正，成本减少
                            # 亏损时 profit_loss 为负，成本增加
                            new_cost = old_cost - profit_loss
                            print(f"[import_profit_data] 新成本计算: {old_cost} - {profit_loss} = {new_cost}")
                            
                            # 份额不变，重新计算成本净值
                            accumulated_cost_nav = new_cost / old_shares if old_shares > 0 else 0
                            print(f"[import_profit_data] 累加后成本净值: {accumulated_cost_nav}")
                            
                            cursor.execute('''
                                UPDATE portfolio_fund SET 
                                    buy_nav = ?, 
                                    cost_nav = ?, 
                                    import_date = ?, 
                                    import_source = ?, 
                                    update_time = CURRENT_TIMESTAMP
                                WHERE portfolio_id = ? AND fund_code = ?
                            ''', (
                                accumulated_cost_nav, accumulated_cost_nav,
                                import_date, source_type, portfolio_id, fund_code
                            ))
                            print(f"[import_profit_data] 累加模式UPDATE完成, 影响行数: {cursor.rowcount}")
                        else:
                            # 不存在，插入新记录
                            print(f"[import_profit_data] 累加模式但无旧数据, 执行INSERT")
                            cursor.execute('''
                                INSERT INTO portfolio_fund (
                                    portfolio_id, fund_code, fund_name, shares, 
                                    buy_nav, cost_nav, 
                                    import_date, import_source
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                portfolio_id, fund_code, fund_name, shares,
                                cost_nav, cost_nav,
                                import_date, source_type
                            ))
                            print(f"[import_profit_data] 累加模式INSERT完成, 影响行数: {cursor.rowcount}")
                    
                    success_count += 1
                    total_current_value += current_value
                    total_profit_loss += profit_loss
                    print(f"[import_profit_data] 单只基金处理成功: success_count={success_count}, current_value={current_value}, profit_loss={profit_loss}")
                    
                except Exception as e:
                    print(f"[import_profit_data] 单只基金处理异常: {e}")
                    import traceback
                    traceback.print_exc()
                    fail_count += 1
            
            print(f"[import_profit_data] 处理完成: success_count={success_count}, fail_count={fail_count}")
            
            # 记录导入历史
            cursor.execute('''
                INSERT INTO portfolio_import_history (
                    portfolio_id, import_date, fund_count, 
                    total_current_value, total_profit_loss, 
                    import_mode, source_type, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                portfolio_id, import_date, success_count,
                total_current_value, total_profit_loss,
                import_mode, source_type, f'导入 {success_count} 只基金'
            ))
            
            conn.commit()
            
            result = {
                'success': True,
                'portfolio_id': portfolio_id,
                'import_date': import_date,
                'import_mode': import_mode,
                'success_count': success_count,
                'fail_count': fail_count,
                'total_current_value': total_current_value,
                'total_profit_loss': total_profit_loss,
                'total_profit_rate': total_profit_loss / (total_current_value - total_profit_loss) if (total_current_value - total_profit_loss) > 0 else 0
            }
            print(f"[import_profit_data] 返回结果: {result}")
            return result


# ==================== 便捷函数 ====================

def create_portfolio(name: str, description: str = None) -> Dict[str, Any]:
    """便捷函数：创建组合"""
    return PortfolioManager().create_portfolio(name, description)


def delete_portfolio(portfolio_id: int) -> Dict[str, Any]:
    """便捷函数：删除组合"""
    return PortfolioManager().delete_portfolio(portfolio_id)


def list_portfolios() -> List[Dict[str, Any]]:
    """便捷函数：查询所有组合"""
    return PortfolioManager().list_portfolios()


def get_portfolio(portfolio_id: int) -> Optional[Dict[str, Any]]:
    """便捷函数：获取组合详情"""
    return PortfolioManager().get_portfolio(portfolio_id)


def add_funds_to_portfolio(portfolio_id: int,
                           holdings: Dict[str, Dict[str, any]],
                           exclude_money_market: bool = True) -> Dict[str, Any]:
    """便捷函数：添加成分基金（支持单只或批量）
    
    Args:
        portfolio_id: 组合ID
        holdings: 持仓数据字典，格式为 {
            fund_code: {
                'shares': 份额,
                'amount': 金额,
                'buy_date': 买入日期,
                'buy_nav': 买入净值,
                'notes': 备注
            }
        }
        exclude_money_market: 是否排除货币基金（默认True）
    
    Returns:
        添加结果
    """
    return PortfolioManager().add_funds_to_portfolio(portfolio_id, holdings, exclude_money_market)


def list_portfolio_funds(portfolio_id: int) -> List[Dict[str, Any]]:
    """便捷函数：查询组合成分基金"""
    return PortfolioManager().list_portfolio_funds(portfolio_id)


def record_holding(portfolio_id: int, fund_code: str, shares: float, **kwargs) -> Dict[str, Any]:
    """便捷函数：记录持仓快照"""
    return PortfolioManager().record_holding(portfolio_id, fund_code, shares, **kwargs)


def update_portfolio_fund(portfolio_id: int, fund_code: str, **kwargs) -> Dict[str, Any]:
    """便捷函数：更新成分基金"""
    return PortfolioManager().update_portfolio_fund(portfolio_id, fund_code, **kwargs)


def get_portfolio_profit_loss_report(portfolio_id: int, from_date: str, to_date: str = None) -> Dict[str, Any]:
    """便捷函数：获取组合盈亏报告"""
    return PortfolioManager().get_portfolio_profit_loss_report(portfolio_id, from_date, to_date)


def import_profit_data(portfolio_id: int, profit_data: List[Dict[str, Any]], 
                      import_date: str = None, import_mode: str = 'accumulate',
                      source_type: str = 'manual') -> Dict[str, Any]:
    """便捷函数：导入盈亏数据到指定组合
    
    Args:
        portfolio_id: 组合ID
        profit_data: 盈亏数据列表，每项包含：
            - fund_code: 基金代码
            - current_value: 当前持有金额
            - profit_loss: 持仓收益
            - fund_name: 基金名称（可选）
        import_date: 导入日期（默认今天）
        import_mode: 导入模式
            - 'overwrite': 覆盖模式，替换现有数据
            - 'accumulate': 累加模式，与现有数据累加（默认）
        source_type: 数据来源
    
    Returns:
        导入结果统计
    """
    return PortfolioManager().import_profit_data(portfolio_id, profit_data, 
                                              import_date, import_mode, source_type)


def import_profit_data_from_table(table_data: List[Dict[str, Any]], portfolio_id: int,
                                 import_mode: str = 'overwrite') -> Dict[str, Any]:
    """从表格数据导入盈亏

    Args:
        table_data: 表格数据，格式为 [{code, name, amount, profit}]
        portfolio_id: 组合ID
        import_mode: 导入模式

    Returns:
        导入结果
    """
    # 转换为标准格式
    profit_data = []
    for item in table_data:
        profit_data.append({
            'fund_code': item.get('code'),
            'fund_name': item.get('name'),
            'current_value': item.get('amount', 0),
            'profit_loss': item.get('profit', 0)
        })

    return import_profit_data(portfolio_id, profit_data, import_mode=import_mode,
                             source_type='table_import')


# ==================== 交易维护接口 ====================

def record_buy_transaction(portfolio_id: int, fund_code: str,
                           shares: float, amount: float,
                           transaction_date: str = None,
                           nav: float = None, fee: float = 0,
                           notes: str = None) -> Dict[str, Any]:
    """
    记录买入交易并更新持仓

    公式：
    - 新成本 = (原数量 × 原成本 + 买入投入金额) / (原数量 + 买入数量)
    - 新持仓数量 = 原数量 + 买入数量

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        shares: 买入份额
        amount: 买入投入金额
        transaction_date: 交易日期（默认今天）
        nav: 交易时净值（可选）
        fee: 手续费（可选）
        notes: 备注（可选）

    Returns:
        交易记录结果
    """
    if not transaction_date:
        transaction_date = datetime.now().strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查组合是否存在
        cursor.execute('SELECT id FROM portfolio WHERE id = ?', (portfolio_id,))
        if not cursor.fetchone():
            return {'success': False, 'error': '组合不存在'}

        # 检查基金是否已存在于组合中
        cursor.execute('''
            SELECT shares, buy_nav FROM portfolio_fund
            WHERE portfolio_id = ? AND fund_code = ?
        ''', (portfolio_id, fund_code))
        existing = cursor.fetchone()

        # 计算新的成本净值和持仓数量
        if existing:
            old_shares = existing['shares'] or 0
            old_buy_nav = existing['buy_nav'] or 0

            # 新持仓数量 = 原数量 + 买入数量
            new_shares = old_shares + shares

            # 新成本 = (原数量 × 原成本 + 买入投入金额) / (原数量 + 买入数量)
            if new_shares > 0:
                new_buy_nav = (old_shares * old_buy_nav + amount) / new_shares
            else:
                new_buy_nav = nav if nav else (amount / shares if shares > 0 else 0)
        else:
            # 新买入，直接使用买入数据
            new_shares = shares
            new_buy_nav = nav if nav else (amount / shares if shares > 0 else 0)

        # 记录交易
        cursor.execute('''
            INSERT INTO portfolio_transaction
            (portfolio_id, fund_code, transaction_type, transaction_date,
             shares, amount, nav, fee, notes)
            VALUES (?, ?, 'BUY', ?, ?, ?, ?, ?, ?)
        ''', (portfolio_id, fund_code, transaction_date, shares, amount, nav, fee, notes))

        # 更新或插入成分基金记录
        fund_name = PortfolioManager()._get_fund_name(fund_code)
        if existing:
            cursor.execute('''
                UPDATE portfolio_fund SET
                    shares = ?, buy_nav = ?, update_time = CURRENT_TIMESTAMP
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (new_shares, new_buy_nav, portfolio_id, fund_code))
        else:
            cursor.execute('''
                INSERT INTO portfolio_fund
                (portfolio_id, fund_code, fund_name, shares, buy_nav, buy_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (portfolio_id, fund_code, fund_name, new_shares, new_buy_nav, transaction_date, notes))

        # 记录持仓历史
        cursor.execute('''
            INSERT OR REPLACE INTO holding_history
            (portfolio_id, fund_code, record_date, shares, nav, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (portfolio_id, fund_code, transaction_date, new_shares, nav, notes or '买入交易'))

        conn.commit()

        return {
            'success': True,
            'transaction_type': 'BUY',
            'fund_code': fund_code,
            'fund_name': fund_name,
            'shares': shares,
            'amount': amount,
            'new_total_shares': new_shares,
            'new_buy_nav': round(new_buy_nav, 4) if new_buy_nav else None,
            'transaction_date': transaction_date
        }


def record_sell_transaction(portfolio_id: int, fund_code: str,
                            shares: float, amount: float,
                            transaction_date: str = None,
                            nav: float = None, fee: float = 0,
                            notes: str = None) -> Dict[str, Any]:
    """
    记录卖出交易并更新持仓

    公式：
    - 新成本 = (原数量 × 原成本 - 卖出获得金额) / (原数量 - 卖出数量)
    - 新持仓数量 = 原数量 - 卖出数量
    - 卖出所得计入组合现金字段

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        shares: 卖出份额
        amount: 卖出获得金额
        transaction_date: 交易日期（默认今天）
        nav: 交易时净值（可选）
        fee: 手续费（可选）
        notes: 备注（可选）

    Returns:
        交易记录结果
    """
    if not transaction_date:
        transaction_date = datetime.now().strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查组合是否存在
        cursor.execute('SELECT id, cash FROM portfolio WHERE id = ?', (portfolio_id,))
        portfolio = cursor.fetchone()
        if not portfolio:
            return {'success': False, 'error': '组合不存在'}

        current_cash = portfolio['cash'] or 0

        # 检查基金是否存在于组合中
        cursor.execute('''
            SELECT shares, buy_nav FROM portfolio_fund
            WHERE portfolio_id = ? AND fund_code = ?
        ''', (portfolio_id, fund_code))
        existing = cursor.fetchone()

        if not existing:
            return {'success': False, 'error': '该基金不在组合中'}

        old_shares = existing['shares'] or 0
        old_buy_nav = existing['buy_nav'] or 0

        # 检查卖出份额是否超过持仓
        if shares > old_shares:
            return {'success': False, 'error': f'卖出份额({shares})超过持仓({old_shares})'}

        # 新持仓数量 = 原数量 - 卖出数量
        new_shares = old_shares - shares

        # 新成本 = (原数量 × 原成本 - 卖出获得金额) / (原数量 - 卖出数量)
        if new_shares > 0:
            new_buy_nav = (old_shares * old_buy_nav - amount) / new_shares
            if new_buy_nav < 0:
                new_buy_nav = 0  # 成本不能为负
        else:
            new_buy_nav = None  # 全部卖出，成本清空

        # 使用传入的nav或计算nav作为confirmed_nav
        confirmed_nav = nav if nav else (amount / shares if shares > 0 else 0)

        # 记录交易
        cursor.execute('''
            INSERT INTO portfolio_transaction
            (portfolio_id, fund_code, transaction_type, transaction_date,
             shares, amount, nav, confirmed_nav, fee, notes)
            VALUES (?, ?, 'SELL', ?, ?, ?, ?, ?, ?, ?)
        ''', (portfolio_id, fund_code, transaction_date, shares, amount, nav, confirmed_nav, fee, notes))

        # 更新成分基金记录
        if new_shares > 0:
            cursor.execute('''
                UPDATE portfolio_fund SET
                    shares = ?, buy_nav = ?, update_time = CURRENT_TIMESTAMP
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (new_shares, new_buy_nav, portfolio_id, fund_code))
        else:
            # 全部卖出，删除记录
            cursor.execute('''
                DELETE FROM portfolio_fund
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))

        # 更新组合现金（卖出所得计入现金）
        new_cash = current_cash + amount
        cursor.execute('''
            UPDATE portfolio SET cash = ?, update_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_cash, portfolio_id))

        # 记录持仓历史
        if new_shares > 0:
            cursor.execute('''
                INSERT OR REPLACE INTO holding_history
                (portfolio_id, fund_code, record_date, shares, nav, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (portfolio_id, fund_code, transaction_date, new_shares, nav, notes or '卖出交易'))

        conn.commit()

        fund_name = PortfolioManager()._get_fund_name(fund_code)

        return {
            'success': True,
            'transaction_type': 'SELL',
            'fund_code': fund_code,
            'fund_name': fund_name,
            'shares': shares,
            'amount': amount,
            'new_total_shares': new_shares,
            'new_buy_nav': round(new_buy_nav, 4) if new_buy_nav else None,
            'cash_added': amount,
            'new_cash_balance': new_cash,
            'transaction_date': transaction_date
        }


def execute_buy_back_transaction(portfolio_id: int, fund_code: str,
                                 target_sell_transaction_id: int,
                                 shares: float, amount: float,
                                 transaction_date: str = None,
                                 nav: float = None, fee: float = 0,
                                 notes: str = None) -> Dict[str, Any]:
    """
    执行波段捡回交易

    功能：
    1. 记录买入交易
    2. 标记对应的卖出记录为已回收 (is_recovered = 1)
    3. 扣除组合现金

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码
        target_sell_transaction_id: 目标卖出交易记录ID（要标记为已回收的卖单）
        shares: 买入份额
        amount: 买入金额
        transaction_date: 交易日期（默认今天）
        nav: 交易时净值（可选）
        fee: 手续费（可选）
        notes: 备注（可选）

    Returns:
        交易记录结果
    """
    if not transaction_date:
        transaction_date = datetime.now().strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查组合是否存在
        cursor.execute('SELECT id, cash FROM portfolio WHERE id = ?', (portfolio_id,))
        portfolio = cursor.fetchone()
        if not portfolio:
            return {'success': False, 'error': '组合不存在'}

        current_cash = portfolio['cash'] or 0

        # 检查现金是否充足
        if current_cash < amount:
            return {'success': False, 'error': f'现金不足，当前现金{current_cash:.2f}，需要{amount:.2f}'}

        # 验证目标卖出记录是否存在且未回收
        cursor.execute('''
            SELECT id, shares, is_recovered FROM portfolio_transaction
            WHERE id = ? AND portfolio_id = ? AND fund_code = ? AND transaction_type = 'SELL'
        ''', (target_sell_transaction_id, portfolio_id, fund_code))
        sell_record = cursor.fetchone()

        if not sell_record:
            return {'success': False, 'error': '目标卖出记录不存在'}

        if sell_record['is_recovered'] == 1:
            return {'success': False, 'error': '该卖出记录已被回收，不能重复捡回'}

        if abs(sell_record['shares'] - shares) > 0.01:
            return {'success': False, 'error': f'捡回份额({shares})必须与卖出份额({sell_record["shares"]})一致'}

        # 记录买入交易
        cursor.execute('''
            INSERT INTO portfolio_transaction
            (portfolio_id, fund_code, transaction_type, transaction_date,
             shares, amount, nav, fee, notes)
            VALUES (?, ?, 'BUY', ?, ?, ?, ?, ?, ?)
        ''', (portfolio_id, fund_code, transaction_date, shares, amount, nav, fee,
              notes or f'波段捡回 - 对应卖出记录#{target_sell_transaction_id}'))

        buy_transaction_id = cursor.lastrowid

        # 标记卖出记录为已回收
        cursor.execute('''
            UPDATE portfolio_transaction
            SET is_recovered = 1
            WHERE id = ?
        ''', (target_sell_transaction_id,))

        # 更新成分基金记录（买入增加持仓）
        cursor.execute('''
            SELECT shares, buy_nav FROM portfolio_fund
            WHERE portfolio_id = ? AND fund_code = ?
        ''', (portfolio_id, fund_code))
        existing = cursor.fetchone()

        if existing:
            old_shares = existing['shares'] or 0
            old_buy_nav = existing['buy_nav'] or 0

            # 新持仓数量 = 原数量 + 买入数量
            new_shares = old_shares + shares

            # 新成本 = (原数量 × 原成本 + 买入金额) / (原数量 + 买入数量)
            if new_shares > 0:
                new_buy_nav = (old_shares * old_buy_nav + amount) / new_shares
            else:
                new_buy_nav = nav if nav else (amount / shares if shares > 0 else 0)

            cursor.execute('''
                UPDATE portfolio_fund SET
                    shares = ?, buy_nav = ?, update_time = CURRENT_TIMESTAMP
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (new_shares, new_buy_nav, portfolio_id, fund_code))
        else:
            # 新建持仓记录
            new_buy_nav = nav if nav else (amount / shares if shares > 0 else 0)
            cursor.execute('''
                INSERT INTO portfolio_fund
                (portfolio_id, fund_code, shares, buy_nav, create_time, update_time)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (portfolio_id, fund_code, shares, new_buy_nav))

        # 扣除组合现金
        new_cash = current_cash - amount
        cursor.execute('''
            UPDATE portfolio SET cash = ?, update_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_cash, portfolio_id))

        conn.commit()

        fund_name = PortfolioManager()._get_fund_name(fund_code)

        return {
            'success': True,
            'transaction_type': 'BUY',
            'fund_code': fund_code,
            'fund_name': fund_name,
            'shares': shares,
            'amount': amount,
            'target_sell_transaction_id': target_sell_transaction_id,
            'buy_transaction_id': buy_transaction_id,
            'new_cash_balance': new_cash,
            'transaction_date': transaction_date
        }


def get_portfolio_transactions(portfolio_id: int, fund_code: str = None,
                               start_date: str = None, end_date: str = None,
                               transaction_type: str = None) -> List[Dict[str, Any]]:
    """
    获取组合交易记录

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码（可选，筛选特定基金）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        transaction_type: 交易类型（可选，BUY/SELL）

    Returns:
        交易记录列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = '''
            SELECT t.*, fi.fund_name
            FROM portfolio_transaction t
            LEFT JOIN fund_info fi ON t.fund_code = fi.fund_code
            WHERE t.portfolio_id = ?
        '''
        params = [portfolio_id]

        if fund_code:
            query += ' AND t.fund_code = ?'
            params.append(fund_code)

        if start_date:
            query += ' AND t.transaction_date >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND t.transaction_date <= ?'
            params.append(end_date)

        if transaction_type:
            query += ' AND t.transaction_type = ?'
            params.append(transaction_type)

        query += ' ORDER BY t.transaction_date DESC, t.create_time DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_portfolio_cash(portfolio_id: int, cash: float) -> Dict[str, Any]:
    """
    更新组合现金余额

    Args:
        portfolio_id: 组合ID
        cash: 现金金额

    Returns:
        更新结果
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM portfolio WHERE id = ?', (portfolio_id,))
        if not cursor.fetchone():
            return {'success': False, 'error': '组合不存在'}

        cursor.execute('''
            UPDATE portfolio SET cash = ?, update_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (cash, portfolio_id))
        conn.commit()

        return {
            'success': True,
            'portfolio_id': portfolio_id,
            'cash': cash
        }


def get_portfolio_cash(portfolio_id: int) -> Dict[str, Any]:
    """
    获取组合现金余额

    Args:
        portfolio_id: 组合ID

    Returns:
        现金信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, cash FROM portfolio WHERE id = ?', (portfolio_id,))
        row = cursor.fetchone()

        if not row:
            return {'success': False, 'error': '组合不存在'}

        return {
            'success': True,
            'portfolio_id': row['id'],
            'portfolio_name': row['name'],
            'cash': row['cash'] or 0
        }


def calculate_fund_available_cash(portfolio_id: int, fund_code: str) -> Dict[str, Any]:
    """
    计算成分基金的可用现金

    计算公式：
    - 可用现金 = 所有卖出交易获得金额 - 所有买入交易投入金额
    - 如果结果为正，表示该基金有可用现金（净卖出）
    - 如果结果为负，表示该基金有投入成本（净买入）

    Args:
        portfolio_id: 组合ID
        fund_code: 基金代码

    Returns:
        可用现金信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查基金是否在组合中
        cursor.execute('''
            SELECT fund_name FROM portfolio_fund
            WHERE portfolio_id = ? AND fund_code = ?
        ''', (portfolio_id, fund_code))
        fund = cursor.fetchone()

        if not fund:
            return {
                'success': False,
                'error': '该基金不在组合中'
            }

        # 计算所有买入交易的投入金额总和
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_buy_amount
            FROM portfolio_transaction
            WHERE portfolio_id = ? AND fund_code = ? AND transaction_type = 'BUY'
        ''', (portfolio_id, fund_code))
        buy_result = cursor.fetchone()
        total_buy_amount = buy_result['total_buy_amount'] or 0

        # 计算所有卖出交易的获得金额总和
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_sell_amount
            FROM portfolio_transaction
            WHERE portfolio_id = ? AND fund_code = ? AND transaction_type = 'SELL'
        ''', (portfolio_id, fund_code))
        sell_result = cursor.fetchone()
        total_sell_amount = sell_result['total_sell_amount'] or 0

        # 计算可用现金
        available_cash = total_sell_amount - total_buy_amount

        return {
            'success': True,
            'portfolio_id': portfolio_id,
            'fund_code': fund_code,
            'fund_name': fund['fund_name'],
            'total_buy_amount': total_buy_amount,
            'total_sell_amount': total_sell_amount,
            'available_cash': available_cash
        }


def get_portfolio_funds_available_cash(portfolio_id: int) -> Dict[str, Any]:
    """
    获取组合内所有成分基金的可用现金

    Args:
        portfolio_id: 组合ID

    Returns:
        所有成分基金的可用现金信息
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 检查组合是否存在
        cursor.execute('SELECT id, name FROM portfolio WHERE id = ?', (portfolio_id,))
        portfolio = cursor.fetchone()

        if not portfolio:
            return {'success': False, 'error': '组合不存在'}

        # 获取组合内所有基金
        cursor.execute('''
            SELECT fund_code, fund_name FROM portfolio_fund
            WHERE portfolio_id = ?
            ORDER BY fund_code
        ''', (portfolio_id,))
        funds = cursor.fetchall()

        if not funds:
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'portfolio_name': portfolio['name'],
                'fund_count': 0,
                'funds': []
            }

        # 批量计算所有基金的可用现金
        funds_cash = []
        total_available_cash = 0

        for fund in funds:
            fund_code = fund['fund_code']
            cash_info = calculate_fund_available_cash(portfolio_id, fund_code)
            if cash_info['success']:
                funds_cash.append({
                    'fund_code': fund_code,
                    'fund_name': cash_info['fund_name'],
                    'available_cash': cash_info['available_cash'],
                    'total_buy_amount': cash_info['total_buy_amount'],
                    'total_sell_amount': cash_info['total_sell_amount']
                })
                total_available_cash += cash_info['available_cash']

        return {
            'success': True,
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio['name'],
            'fund_count': len(funds_cash),
            'total_available_cash': total_available_cash,
            'funds': funds_cash
        }


def calculate_portfolio_available_cash_batch(portfolio_id: int) -> Dict[str, float]:
    """
    批量计算组合内所有基金的可用现金（优化版，单次查询）
    
    用于止盈计算等需要快速获取所有基金可用现金的场景
    
    Args:
        portfolio_id: 组合ID
        
    Returns:
        基金代码到可用现金的映射字典
        {
            '000001': 5000.00,
            '110022': 0.00,
            '161725': -2000.00
        }
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 一次性查询所有基金的买入和卖出金额
        cursor.execute('''
            SELECT 
                fund_code,
                SUM(CASE WHEN transaction_type = 'BUY' THEN amount ELSE 0 END) as total_buy,
                SUM(CASE WHEN transaction_type = 'SELL' THEN amount ELSE 0 END) as total_sell
            FROM portfolio_transaction
            WHERE portfolio_id = ?
            GROUP BY fund_code
        ''', (portfolio_id,))
        
        rows = cursor.fetchall()
        
        # 构建可用现金映射
        available_cash_map = {}
        for row in rows:
            fund_code = row['fund_code']
            total_buy = row['total_buy'] or 0
            total_sell = row['total_sell'] or 0
            available_cash_map[fund_code] = total_sell - total_buy
        
        return available_cash_map


if __name__ == '__main__':
    pm = PortfolioManager()
    
    print("=" * 60)
    print("PortfolioManager 测试")
    print("=" * 60)
    
    print("\n1. 创建组合:")
    result = pm.create_portfolio("测试组合", "这是一个测试组合")
    print(f"   结果: {result}")
    
    if result['success']:
        portfolio_id = result['portfolio_id']
        
        print("\n2. 查询所有组合:")
        portfolios = pm.list_portfolios()
        for p in portfolios:
            print(f"   - {p['id']}: {p['name']}")
        
        print("\n3. 添加成分基金:")
        result = pm.add_fund_to_portfolio(portfolio_id, '000001', shares=1000)
        print(f"   结果: {result}")
        
        print("\n4. 查询成分基金:")
        funds = pm.list_portfolio_funds(portfolio_id)
        for f in funds:
            print(f"   - {f['fund_code']}: {f['fund_name']}")
        
        print("\n5. 删除组合:")
        result = pm.delete_portfolio(portfolio_id)
        print(f"   结果: {result}")
