#!/usr/bin/env python3
"""
收费技能 - 授权验证 + 手机号登录
流程：
1. 检查 SKILL_LICENSE_KEY 授权码
2. 授权失败，提示购买并退出
3. 授权通过，检查本地是否保存了手机号
   - 没有手机号 → 提示用户输入手机号 → 请求后端绑定 → 成功保存 → 启动核心功能
   - 有手机号 → 直接启动核心功能
"""
from __future__ import annotations

import os
import sys
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_license import check_license, get_encryption_key

# 手机号存储文件
PHONE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".phone.json")

# ========== 在这里修改你的 API URL ==========
REGISTER_ENDPOINT = "https://yunji.focus-jd.cn/api/skill/lin/test"


# ======================================================


def get_fernet() -> Fernet | None:
    """获取 Fernet 加密实例，使用授权码作为密钥"""
    license_key = os.environ.get("SKILL_LICENSE_KEY", "").strip()
    if not license_key:
        return None

    key = get_encryption_key(license_key)
    # 派生 Fernet 密钥 (32 bytes base64 encoded)
    salt = b'PaidSkillSalt2024'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(key))
    return Fernet(derived_key)


def load_saved_phone() -> str:
    """加载保存的手机号（解密）"""
    if not os.path.exists(PHONE_FILE):
        return ''

    fernet = get_fernet()
    if not fernet:
        return ''

    try:
        with open(PHONE_FILE, 'rb') as f:
            encrypted_data = f.read()
        decrypted = fernet.decrypt(encrypted_data).decode()
        return decrypted
    except Exception:
        # 解密失败（密钥错误或文件损坏），返回空
        return ''


def save_phone(phone: str) -> None:
    """保存手机号（加密）"""
    fernet = get_fernet()
    if not fernet:
        # 没有密钥不保存
        return

    encrypted_data = fernet.encrypt(phone.encode())
    with open(PHONE_FILE, 'wb') as f:
        f.write(encrypted_data)


def register_phone(phone: str) -> tuple[bool, str, dict | None]:
    """
    注册手机号到 Java 后端
    返回: (是否成功, 消息, 完整响应数据)
    """
    try:
        response = requests.post(
            REGISTER_ENDPOINT,
            json={"phone": phone},
            timeout=10
        )

        if response.status_code != 200:
            return False, f"服务器返回错误 HTTP {response.status_code}", None

        # 尝试解析 JSON 响应
        try:
            result = response.json()
            code = result.get("code", -1)
            msg = result.get("msg", "success")
            if code == 0:
                return True, msg, result
            else:
                return False, msg, None
        except ValueError:
            # 非 JSON 返回，200 就算成功
            return True, "success", None

    except requests.exceptions.RequestException as e:
        return False, f"网络请求失败: {str(e)}", None


def main():
    # 第一步：先检查授权码
    valid, msg = check_license()

    # 第二步：根据授权结果打印提示
    if not valid:
        # 授权失败，提示购买并退出
        print("❌ 授权验证失败")
        print(f"⚠️  原因: {msg}")
        print("⚠️  购买授权请访问: https://your-website.com/buy")
        sys.exit(1)

    # 授权通过才继续
    print("✅ 授权验证通过！")

    # 打印核心功能信息
    print("\n这是收费技能的演示功能：")
    print("-----------------------------------")
    print("📝 这里是付费才能使用的核心功能")
    print("💡 你可以替换成你的实际业务逻辑")
    print("🔑 当前状态：授权有效")
    print("-----------------------------------")

    # 第三步：检查手机号，继续流程
    saved_phone = load_saved_phone()

    if saved_phone:
        # 已有手机号，直接启动核心功能
        print(f"\n📱 已绑定手机号: {saved_phone}")
        print("\n🎉 欢迎回来，核心功能已启动！")
        # ========== 这里放你的核心功能代码 ==========
        print("\n✨ 核心功能运行中")
    else:
        # 没有手机号，提示用户输入
        print("\n📱 请输入你的手机号进行绑定:")
        print("(输入后按回车确认)\n")

        phone = input().strip()

        if not phone:
            print("❌ 手机号不能为空", file=sys.stderr)
            sys.exit(1)

        print("🔄 正在绑定...\n")

        success, result_msg, result_data = register_phone(phone)
        if success:
            # 绑定成功，输出后端返回结果
            print(f"✅ 绑定成功")
            if result_msg:
                print(f"ℹ️ 消息: {result_msg}")
            if result_data:
                print("\n📄 后端返回完整数据:")
                print(json.dumps(result_data, indent=2, ensure_ascii=False))
            # 保存手机号
            save_phone(phone)
            print("\n🎉 绑定完成，核心功能已启动！")
            # ========== 这里放你的核心功能代码 ==========
            print("\n✨ 核心功能运行中")
        else:
            # 绑定失败，不保存，提示错误
            print(f"❌ 绑定失败: {result_msg}", file=sys.stderr)
            print("\n手机号未保存，请检查后端服务后重试", file=sys.stderr)


if __name__ == "__main__":
    main()