"""
加密工具模块，提供数据加密和解密功能
"""
import json
import os
import logging
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypt_data_to_file(data_obj, password=b"water_quality_analysis_key", 
                         salt=b"water_quality_salt", iv=b"fixed_iv_16bytes", 
                         output_dir=None, logger=None):
    """
    加密数据并保存到文件
    
    Args:
        data_obj: 要加密的数据对象(将被转换为JSON)
        password: 加密密码字节串
        salt: 盐值字节串
        iv: 初始化向量字节串(16字节)
        output_dir: 输出文件路径，若为None则自动生成
        logger: 日志记录器，若为None则不记录日志
        
    Returns:
        str: 输出文件的路径
    """
    # 使用默认日志器如果未提供
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # 生成加密密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES256需要32字节密钥
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        
        # 记录使用的IV
        logger.info(f"使用IV: {iv}")
        
        # 准备加密器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # 将结果转换为JSON
        data_json = json.dumps(data_obj, ensure_ascii=False)
        
        # 对数据进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data_json.encode('utf-8')) + padder.finalize()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 将IV与加密数据一起存储（IV可以是公开的）
        final_data = iv + encrypted_data
        
        # 如果未提供输出路径，则生成带时间戳的文件名
        if output_dir is None:
            # 确保models_dir存在
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'models')
            os.makedirs(output_dir, exist_ok=True)
            
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"encrypted_result_{timestamp}.bin")
        
        # 保存加密数据到文件
        with open(output_path, 'wb') as f:
            f.write(final_data)
        
        logger.info(f"结果已加密并保存到: {output_path}")
        
        # 记录解密所需的参数（仅在本地日志中）
        logger.info("===== 解密所需参数（仅供内部使用）=====")
        logger.info(f"加密算法: AES256-CBC with PKCS7 padding")
        logger.info(f"password: {password}")
        logger.info(f"salt: {salt}")
        logger.info(f"iterations: 100000")
        logger.info(f"key length: 32 bytes")
        logger.info(f"IV: 固定值 {iv}，仍存储在加密文件的前16个字节")
        logger.info("解密步骤: 1)读取文件前16字节作为IV（虽然是固定值）; 2)使用相同参数通过PBKDF2派生密钥; 3)使用AES256-CBC和IV解密剩余数据; 4)去除PKCS7填充")
        logger.info("===============================")
        
        return output_path
    except Exception as e:
        logger.error(f"加密数据时出错: {str(e)}")
        return None


def decrypt_file(file_path, password=b"water_quality_analysis_key", 
                salt=b"water_quality_salt", logger=None):
    """
    解密文件内容
    
    Args:
        file_path: 加密文件路径
        password: 加密密码字节串
        salt: 盐值字节串
        logger: 日志记录器，若为None则不记录日志
        
    Returns:
        dict: 解密后的JSON数据对象，失败时返回None
    """
    # 使用默认日志器如果未提供
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # 读取加密文件
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # 从文件读取IV（前16字节）
        iv = file_data[:16]
        encrypted_data = file_data[16:]
        
        # 从密码和盐值生成密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        
        # 解密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        # 解密数据
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        # 解析JSON
        result = json.loads(decrypted_data)
        logger.info(f"成功解密文件: {file_path}")
        return result
    except Exception as e:
        logger.error(f"解密文件失败: {str(e)}")
        return None 