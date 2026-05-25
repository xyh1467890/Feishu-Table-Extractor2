"""
飞书 Cookie API 模块
用于通过 Cookie 方式获取数据表信息
"""

import json
import requests
from urllib.parse import urlparse


def parse_app_id_from_cookie_url(feishu_url):
    """从飞书链接中解析 base_token"""
    parsed = urlparse(feishu_url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2 or parts[0] != "base":
        raise ValueError("不是有效的飞书多维表格链接")

    return parts[1]


def extract_bitable_info_by_cookie(feishu_url, cookie):
    """
    通过 Cookie 方式提取飞书多维表格信息

    Args:
        feishu_url: 飞书多维表格链接
        cookie: 飞书 Cookie 字符串

    Returns:
        包含 base_token 和 tables 信息的字典
    """
    base_token = parse_app_id_from_cookie_url(feishu_url)
    
    # 构建请求头
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 访问多维表格页面获取数据
    try:
        # 注意：这里简化了 Cookie 方式的实现，实际需要根据飞书的具体接口调整
        # 由于 Cookie 方式较为复杂且可能不稳定，这里提供基础框架
        # 实际应用中建议使用 Token 方式
        
        # 模拟获取表信息（示例实现）
        tables = []
        
        return {
            "base_token": base_token,
            "tables": tables,
            "note": "Cookie 方式已获取 base_token，建议使用 Token 方式获取完整数据"
        }
    except Exception as e:
        raise RuntimeError(f"通过 Cookie 方式获取数据失败: {str(e)}")
