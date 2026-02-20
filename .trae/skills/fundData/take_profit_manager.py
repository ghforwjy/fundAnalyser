"""
止盈参数模板管理模块

功能：
1. 模板管理：创建、编辑、删除、查询止盈参数模板
2. 基金配置：为基金设置使用的模板或自定义参数
3. 参数优先级：自定义参数 > 指定模板 > 默认模板
"""

import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funddb import get_db_connection


class TakeProfitTemplateManager:
    
    def list_templates(self) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM take_profit_template 
                ORDER BY is_default DESC, is_system DESC, name ASC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM take_profit_template WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM take_profit_template WHERE name = ?', (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_default_template(self) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM take_profit_template WHERE is_default = 1')
            row = cursor.fetchone()
            if row:
                return dict(row)
        
        return {
            'id': 0,
            'name': '默认参数',
            'first_threshold': 0.20,
            'first_sell_ratio': 0.30,
            'step_size': 0.05,
            'follow_up_sell_ratio': 0.20,
            'enable_cost_control': 1,
            'target_diluted_cost': 0.0,
            'enable_buy_back': 0,
            'buy_back_threshold': 0.20
        }
    
    def create_template(self, name: str, description: str = None,
                        first_threshold: float = 0.20,
                        first_sell_ratio: float = 0.30,
                        step_size: float = 0.05,
                        follow_up_sell_ratio: float = 0.20,
                        enable_cost_control: bool = True,
                        target_diluted_cost: float = 0.0,
                        enable_buy_back: bool = False,
                        buy_back_threshold: float = 0.20) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO take_profit_template 
                    (name, description, first_threshold, first_sell_ratio, step_size, 
                     follow_up_sell_ratio, enable_cost_control, target_diluted_cost,
                     enable_buy_back, buy_back_threshold)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, first_threshold, first_sell_ratio, step_size,
                      follow_up_sell_ratio, 1 if enable_cost_control else 0, target_diluted_cost,
                      1 if enable_buy_back else 0, buy_back_threshold))
                
                template_id = cursor.lastrowid
                conn.commit()
                
                return {'success': True, 'template_id': template_id, 'message': '模板创建成功'}
            except Exception as e:
                return {'success': False, 'message': str(e)}
    
    def update_template(self, template_id: int, **kwargs) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT is_system FROM take_profit_template WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'message': '模板不存在'}
            
            allowed_fields = ['name', 'description', 'first_threshold', 'first_sell_ratio',
                              'step_size', 'follow_up_sell_ratio', 'enable_cost_control', 
                              'target_diluted_cost', 'enable_buy_back', 'buy_back_threshold']
            
            updates = []
            values = []
            for key, value in kwargs.items():
                if key in allowed_fields:
                    if key in ['enable_cost_control', 'enable_buy_back']:
                        value = 1 if value else 0
                    updates.append(f'{key} = ?')
                    values.append(value)
            
            if not updates:
                return {'success': False, 'message': '没有可更新的字段'}
            
            values.append(template_id)
            sql = f"UPDATE take_profit_template SET {', '.join(updates)}, update_time = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(sql, values)
            conn.commit()
            
            return {'success': True, 'message': '模板更新成功'}
    
    def delete_template(self, template_id: int) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT is_system, is_default FROM take_profit_template WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'message': '模板不存在'}
            
            if row['is_system']:
                return {'success': False, 'message': '系统预设模板不可删除'}
            
            if row['is_default']:
                return {'success': False, 'message': '默认模板不可删除，请先设置其他模板为默认'}
            
            cursor.execute('DELETE FROM fund_take_profit_config WHERE template_id = ?', (template_id,))
            cursor.execute('DELETE FROM take_profit_template WHERE id = ?', (template_id,))
            conn.commit()
            
            return {'success': True, 'message': '模板删除成功'}
    
    def set_default_template(self, template_id: int) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM take_profit_template WHERE id = ?', (template_id,))
            if not cursor.fetchone():
                return {'success': False, 'message': '模板不存在'}
            
            cursor.execute('UPDATE take_profit_template SET is_default = 0')
            cursor.execute('UPDATE take_profit_template SET is_default = 1 WHERE id = ?', (template_id,))
            conn.commit()
            
            return {'success': True, 'message': '默认模板设置成功'}
    
    def get_fund_config(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM fund_take_profit_config 
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            config = cursor.fetchone()
            
            result = {
                'portfolio_id': portfolio_id,
                'fund_code': fund_code,
                'param_source': 'default',
                'template_id': None,
                'template_name': None,
                'first_threshold': 0.20,
                'first_sell_ratio': 0.30,
                'step_size': 0.05,
                'follow_up_sell_ratio': 0.20,
                'enable_cost_control': True,
                'target_diluted_cost': 0.0,
                'enable_buy_back': False,
                'buy_back_threshold': 0.20
            }
            
            has_custom_params = False
            if config:
                config = dict(config)
                result['template_id'] = config.get('template_id')
                result['enabled'] = config.get('enabled', 1)
                
                if config.get('custom_first_threshold') is not None:
                    has_custom_params = True
                    result['first_threshold'] = config['custom_first_threshold']
                    result['first_sell_ratio'] = config['custom_first_sell_ratio']
                    result['step_size'] = config['custom_step_size']
                    result['follow_up_sell_ratio'] = config['custom_follow_up_sell_ratio']
                    result['enable_cost_control'] = bool(config['custom_enable_cost_control'])
                    result['target_diluted_cost'] = config['custom_target_diluted_cost']
                    result['enable_buy_back'] = bool(config.get('custom_enable_buy_back', 0))
                    result['buy_back_threshold'] = config.get('custom_buy_back_threshold', 0.20)
                    result['param_source'] = 'custom'
            
            if not has_custom_params:
                template = None
                if config and config.get('template_id'):
                    cursor.execute('SELECT * FROM take_profit_template WHERE id = ?', (config['template_id'],))
                    template = cursor.fetchone()
                    result['param_source'] = 'template'
                else:
                    cursor.execute('SELECT * FROM take_profit_template WHERE is_default = 1')
                    template = cursor.fetchone()
                    result['param_source'] = 'default'
                
                if template:
                    template = dict(template)
                    result['template_id'] = template['id']
                    result['template_name'] = template['name']
                    result['first_threshold'] = template['first_threshold']
                    result['first_sell_ratio'] = template['first_sell_ratio']
                    result['step_size'] = template['step_size']
                    result['follow_up_sell_ratio'] = template['follow_up_sell_ratio']
                    result['enable_cost_control'] = bool(template['enable_cost_control'])
                    result['target_diluted_cost'] = template['target_diluted_cost']
                    result['enable_buy_back'] = bool(template.get('enable_buy_back', 0))
                    result['buy_back_threshold'] = template.get('buy_back_threshold', 0.20)
            
            return result
    
    def set_fund_template(self, portfolio_id: int, fund_code: str, 
                          template_id: int = None) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM fund_take_profit_config 
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE fund_take_profit_config 
                    SET template_id = ?, 
                        custom_first_threshold = NULL,
                        custom_first_sell_ratio = NULL,
                        custom_step_size = NULL,
                        custom_follow_up_sell_ratio = NULL,
                        custom_enable_cost_control = NULL,
                        custom_target_diluted_cost = NULL,
                        update_time = CURRENT_TIMESTAMP
                    WHERE portfolio_id = ? AND fund_code = ?
                ''', (template_id, portfolio_id, fund_code))
            else:
                cursor.execute('''
                    INSERT INTO fund_take_profit_config 
                    (portfolio_id, fund_code, template_id)
                    VALUES (?, ?, ?)
                ''', (portfolio_id, fund_code, template_id))
            
            conn.commit()
            
            return {'success': True, 'message': '基金模板设置成功'}
    
    def set_fund_custom_params(self, portfolio_id: int, fund_code: str,
                                first_threshold: float = None,
                                first_sell_ratio: float = None,
                                step_size: float = None,
                                follow_up_sell_ratio: float = None,
                                enable_cost_control: bool = None,
                                target_diluted_cost: float = None,
                                enable_buy_back: bool = None,
                                buy_back_threshold: float = None) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM fund_take_profit_config 
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE fund_take_profit_config 
                    SET custom_first_threshold = ?,
                        custom_first_sell_ratio = ?,
                        custom_step_size = ?,
                        custom_follow_up_sell_ratio = ?,
                        custom_enable_cost_control = ?,
                        custom_target_diluted_cost = ?,
                        custom_enable_buy_back = ?,
                        custom_buy_back_threshold = ?,
                        update_time = CURRENT_TIMESTAMP
                    WHERE portfolio_id = ? AND fund_code = ?
                ''', (first_threshold, first_sell_ratio, step_size, follow_up_sell_ratio,
                      1 if enable_cost_control else 0 if enable_cost_control is not None else None,
                      target_diluted_cost,
                      1 if enable_buy_back else 0 if enable_buy_back is not None else None,
                      buy_back_threshold, portfolio_id, fund_code))
            else:
                cursor.execute('''
                    INSERT INTO fund_take_profit_config 
                    (portfolio_id, fund_code, custom_first_threshold, custom_first_sell_ratio,
                     custom_step_size, custom_follow_up_sell_ratio, custom_enable_cost_control,
                     custom_target_diluted_cost, custom_enable_buy_back, custom_buy_back_threshold)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (portfolio_id, fund_code, first_threshold, first_sell_ratio,
                      step_size, follow_up_sell_ratio,
                      1 if enable_cost_control else 0 if enable_cost_control is not None else None,
                      target_diluted_cost,
                      1 if enable_buy_back else 0 if enable_buy_back is not None else None,
                      buy_back_threshold))
            
            conn.commit()
            
            return {'success': True, 'message': '基金自定义参数设置成功'}
    
    def clear_fund_custom_params(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE fund_take_profit_config 
                SET custom_first_threshold = NULL,
                    custom_first_sell_ratio = NULL,
                    custom_step_size = NULL,
                    custom_follow_up_sell_ratio = NULL,
                    custom_enable_cost_control = NULL,
                    custom_target_diluted_cost = NULL,
                    custom_enable_buy_back = NULL,
                    custom_buy_back_threshold = NULL,
                    update_time = CURRENT_TIMESTAMP
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            
            conn.commit()
            
            return {'success': True, 'message': '基金自定义参数已清除'}
    
    def reset_fund_config(self, portfolio_id: int, fund_code: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM fund_take_profit_config 
                WHERE portfolio_id = ? AND fund_code = ?
            ''', (portfolio_id, fund_code))
            
            conn.commit()
            
            return {'success': True, 'message': '基金配置已重置为默认'}
    
    def get_portfolio_fund_configs(self, portfolio_id: int) -> List[Dict[str, Any]]:
        from portfolio_manager import list_portfolio_funds
        
        funds = list_portfolio_funds(portfolio_id)
        configs = []
        
        for fund in funds:
            config = self.get_fund_config(portfolio_id, fund['fund_code'])
            config['fund_name'] = fund.get('fund_name', '')
            configs.append(config)
        
        return configs
    
    def batch_set_fund_template(self, portfolio_id: int, fund_codes: List[str],
                                 template_id: int = None) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for fund_code in fund_codes:
                cursor.execute('''
                    SELECT id FROM fund_take_profit_config 
                    WHERE portfolio_id = ? AND fund_code = ?
                ''', (portfolio_id, fund_code))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute('''
                        UPDATE fund_take_profit_config 
                        SET template_id = ?, 
                            custom_first_threshold = NULL,
                            custom_first_sell_ratio = NULL,
                            custom_step_size = NULL,
                            custom_follow_up_sell_ratio = NULL,
                            custom_enable_cost_control = NULL,
                            custom_target_diluted_cost = NULL,
                            custom_enable_buy_back = NULL,
                            custom_buy_back_threshold = NULL,
                            update_time = CURRENT_TIMESTAMP
                        WHERE portfolio_id = ? AND fund_code = ?
                    ''', (template_id, portfolio_id, fund_code))
                else:
                    cursor.execute('''
                        INSERT INTO fund_take_profit_config 
                        (portfolio_id, fund_code, template_id)
                        VALUES (?, ?, ?)
                    ''', (portfolio_id, fund_code, template_id))
            
            conn.commit()
            
            return {'success': True, 'message': f'已为 {len(fund_codes)} 只基金设置模板'}


def list_take_profit_templates() -> List[Dict[str, Any]]:
    return TakeProfitTemplateManager().list_templates()

def get_take_profit_template(template_id: int) -> Optional[Dict[str, Any]]:
    return TakeProfitTemplateManager().get_template(template_id)

def get_default_take_profit_template() -> Dict[str, Any]:
    return TakeProfitTemplateManager().get_default_template()

def create_take_profit_template(**kwargs) -> Dict[str, Any]:
    return TakeProfitTemplateManager().create_template(**kwargs)

def update_take_profit_template(template_id: int, **kwargs) -> Dict[str, Any]:
    return TakeProfitTemplateManager().update_template(template_id, **kwargs)

def delete_take_profit_template(template_id: int) -> Dict[str, Any]:
    return TakeProfitTemplateManager().delete_template(template_id)

def set_default_take_profit_template(template_id: int) -> Dict[str, Any]:
    return TakeProfitTemplateManager().set_default_template(template_id)

def get_fund_take_profit_config(portfolio_id: int, fund_code: str) -> Dict[str, Any]:
    return TakeProfitTemplateManager().get_fund_config(portfolio_id, fund_code)

def set_fund_take_profit_template(portfolio_id: int, fund_code: str, template_id: int = None) -> Dict[str, Any]:
    return TakeProfitTemplateManager().set_fund_template(portfolio_id, fund_code, template_id)

def set_fund_take_profit_custom_params(portfolio_id: int, fund_code: str, **kwargs) -> Dict[str, Any]:
    return TakeProfitTemplateManager().set_fund_custom_params(portfolio_id, fund_code, **kwargs)

def get_portfolio_take_profit_configs(portfolio_id: int) -> List[Dict[str, Any]]:
    return TakeProfitTemplateManager().get_portfolio_fund_configs(portfolio_id)


if __name__ == "__main__":
    manager = TakeProfitTemplateManager()
    
    print("=== 止盈参数模板列表 ===")
    templates = manager.list_templates()
    for t in templates:
        print(f"  {t['id']}: {t['name']} (默认: {t['is_default']}, 系统: {t['is_system']})")
    
    print("\n=== 默认模板 ===")
    default = manager.get_default_template()
    print(f"  {default}")
