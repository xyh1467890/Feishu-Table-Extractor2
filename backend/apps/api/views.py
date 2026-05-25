from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from .feishu_api import extract_bitable_info
from .feishu_cookie_api import extract_bitable_info_by_cookie


@csrf_exempt
@require_http_methods(["POST"])
def fetch_bitable(request):
    """
    获取飞书多维表格数据

    请求参数:
    - auth_type: 认证类型 ('token' 或 'cookie')
    - auth_data: 认证数据 (token 或 cookie)
    - feishu_url: 飞书多维表格链接
    - fetch_records: 是否获取记录内容 (boolean, 默认为 True)
    """
    print(f"Received request: {request.method} {request.path}")
    print(f"Request body: {request.body}")
    
    try:
        # 尝试解析JSON
        try:
            data = json.loads(request.body)
        except Exception as e:
            print(f"JSON parse error: {e}")
            return JsonResponse({
                'success': False,
                'error': '请求体格式错误'
            }, status=400)
        
        print(f"Parsed data: {data}")
        
        # 支持驼峰命名和蛇形命名
        auth_type = data.get('auth_type') or data.get('authType')
        auth_data = data.get('auth_data') or data.get('authData')
        feishu_url = data.get('feishu_url') or data.get('feishuUrl')
        fetch_records = data.get('fetch_records') if 'fetch_records' in data else (data.get('fetchRecords') if 'fetchRecords' in data else True)
        
        # 转换字符串的true/false为布尔值
        if isinstance(fetch_records, str):
            fetch_records = fetch_records.lower() == 'true'
        
        print(f"Params: auth_type={auth_type}, feishu_url={feishu_url}, fetch_records={fetch_records}")

        if not auth_type or not auth_data or not feishu_url:
            print("Missing required parameters")
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            }, status=400)

        if auth_type == 'token':
            print("Using token authentication")
            result = extract_bitable_info(
                feishu_url=feishu_url,
                user_token=auth_data,
                fetch_records=fetch_records
            )
        elif auth_type == 'cookie':
            print("Using cookie authentication")
            result = extract_bitable_info_by_cookie(
                feishu_url=feishu_url,
                cookie=auth_data
            )
        else:
            print(f"Unsupported auth type: {auth_type}")
            return JsonResponse({
                'success': False,
                'error': '不支持的认证类型'
            }, status=400)

        return JsonResponse({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """健康检查接口"""
    return JsonResponse({
        'success': True,
        'message': '服务运行正常'
    })
