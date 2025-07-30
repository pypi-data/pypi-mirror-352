"""
AutoWaterQualityModeler 使用示例

这个脚本展示了如何使用 AutoWaterQualityModeler 库来自动构建水质预测模型。
"""

import pandas as pd
import os
import logging
import logging.handlers
from autowaterqualitymodeler.src.modeler import AutoWaterQualityModeler

def main(spectrum_data, merged_data, metric_data):
    # 获取或配置logger
    # 如果main.py已经配置过日志，则直接使用
    logger = logging.getLogger(__name__)

    logger.info("启动一键式特征排序建模或模型微调程序...")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"当前目录: {current_dir}")
    
    # 数据文件路径
    config_path = os.path.join(current_dir, "config", "features_config.json")
    logger.info(f"配置文件路径: {config_path} (存在: {os.path.exists(config_path)})")
    
    # 加载光谱数据
    spectrum_data.columns = spectrum_data.columns.astype(float)  # 确保列名是波长值

    # 初始化建模器
    try:
        modeler = AutoWaterQualityModeler(
            features_config_path=config_path,
            min_wavelength=400,
            max_wavelength=900
        )
        logger.info("成功初始化AutoWaterQualityModeler")
    except Exception as e:
        logger.error(f"初始化建模器失败: {e}", exc_info=True)
        return
    
    # 指定数据类型并一键建模
    try:
        # 执行建模
        model_dict, dict_df = modeler.fit(
            spectrum_data=spectrum_data,
            merged_data=merged_data,
            metric_data=metric_data,
            data_type="aerospot"
        )
        
        return model_dict, dict_df
        
    except Exception as e:
        logger.error(f"建模过程出错: {e}", exc_info=True)
        return {}