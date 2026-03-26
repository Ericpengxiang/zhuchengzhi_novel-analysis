"""
用户认证API视图
处理注册、登录、登出等功能
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from .models import User


def cors_response(func):
    """CORS装饰器"""
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, JsonResponse):
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            response["Access-Control-Allow-Credentials"] = "true"
        return response
    return wrapper


@csrf_exempt
@cors_response
@require_http_methods(["POST"])
def user_register(request):
    """用户注册"""
    try:
        import json
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        nickname = data.get('nickname', '').strip()

        # 验证必填字段
        if not username or not password:
            return JsonResponse({
                'code': 400,
                'message': '用户名和密码不能为空',
                'data': None
            })

        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return JsonResponse({
                'code': 400,
                'message': '用户名长度必须在3-20个字符之间',
                'data': None
            })

        # 验证密码长度
        if len(password) < 6:
            return JsonResponse({
                'code': 400,
                'message': '密码长度不能少于6位',
                'data': None
            })

        # 创建用户
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email if email else '',
                nickname=nickname if nickname else username,
            )
            return JsonResponse({
                'code': 200,
                'message': '注册成功',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                }
            })
        except IntegrityError:
            return JsonResponse({
                'code': 400,
                'message': '用户名已存在',
                'data': None
            })
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'message': '请求数据格式错误',
            'data': None
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'注册失败：{str(e)}',
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["POST"])
def user_login(request):
    """用户登录"""
    try:
        import json
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        remember_me = data.get('remember_me', False)

        if not username or not password:
            return JsonResponse({
                'code': 400,
                'message': '用户名和密码不能为空',
                'data': None
            })

        # 验证用户
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 登录用户
            login(request, user)
            
            # 设置session过期时间
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 7)  # 7天
            else:
                request.session.set_expiry(60 * 60 * 24)  # 1天

            return JsonResponse({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'nickname': user.nickname or user.username,
                    'email': user.email,
                }
            })
        else:
            return JsonResponse({
                'code': 401,
                'message': '用户名或密码错误',
                'data': None
            })
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'message': '请求数据格式错误',
            'data': None
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'登录失败：{str(e)}',
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["POST"])
def user_logout(request):
    """用户登出"""
    try:
        logout(request)
        return JsonResponse({
            'code': 200,
            'message': '登出成功',
            'data': None
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'登出失败：{str(e)}',
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def user_info(request):
    """获取当前用户信息"""
    try:
        if request.user.is_authenticated:
            return JsonResponse({
                'code': 200,
                'message': 'success',
                'data': {
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'nickname': request.user.nickname or request.user.username,
                    'email': request.user.email,
                }
            })
        else:
            return JsonResponse({
                'code': 401,
                'message': '未登录',
                'data': None
            })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'获取用户信息失败：{str(e)}',
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["POST"])
def user_update(request):
    """更新用户信息（用户名和密码）"""
    try:
        import json
        data = json.loads(request.body)
        
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'code': 401,
                'message': '未登录',
                'data': None
            })
        
        username = data.get('username', '').strip()
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # 验证必填字段
        if not username:
            return JsonResponse({
                'code': 400,
                'message': '用户名不能为空',
                'data': None
            })
        
        if not old_password or not new_password:
            return JsonResponse({
                'code': 400,
                'message': '原密码和新密码不能为空',
                'data': None
            })
        
        # 验证新密码长度
        if len(new_password) < 6:
            return JsonResponse({
                'code': 400,
                'message': '新密码长度不能少于6位',
                'data': None
            })
        
        # 验证原密码是否正确
        user = authenticate(request, username=request.user.username, password=old_password)
        if user is None:
            return JsonResponse({
                'code': 400,
                'message': '原密码错误',
                'data': None
            })
        
        # 更新用户信息
        user = request.user
        user.nickname = username
        user.set_password(new_password)  # 使用set_password来加密密码
        user.save()
        
        return JsonResponse({
            'code': 200,
            'message': '修改成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'nickname': user.nickname,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'message': '请求数据格式错误',
            'data': None
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'修改失败：{str(e)}',
            'data': None
        })
