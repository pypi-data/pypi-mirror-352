from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

import logging


from .spectral_calculator import SpectralCalculator

# 获取模块日志记录器
logger = logging.getLogger(__name__)

class AutoWaterQualityModeler:
    """自动水质建模器，支持从配置文件加载特征定义"""
    
    DATA_TYPES = ["warning_device", "shore_data", "smart_water", "aerospot"]
    
    def __init__(self, 
                 features_config_path: str = "config/features_config.json",
                 min_wavelength: int = 400, 
                 max_wavelength: int = 900,
                 smooth_window: int = 11, 
                 smooth_order: int = 3):
        """
        初始化自动水质建模器
        
        Args:
            features_config_path: 特征配置文件路径
            min_wavelength: 最小波长
            max_wavelength: 最大波长
            smooth_window: 平滑窗口大小
            smooth_order: 平滑多项式阶数
        """
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
        self.smooth_window = smooth_window
        self.smooth_order = smooth_order
        
        # 加载特征配置文件
        self.features_config = self._load_features_config(features_config_path)
        
        # 加载三刺激值系数表
        self._load_tris_coefficients()
        
    def _load_features_config(self, config_path: str) -> Dict:
        """加载特征配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置文件格式
            if not all(data_type in config for data_type in self.DATA_TYPES):
                missing = [dt for dt in self.DATA_TYPES if dt not in config]
                logger.warning(f"配置文件中缺少以下数据类型: {missing}")
                # 为缺失类型创建空配置
                for dt in missing:
                    config[dt] = {}
                    
            return config
        except Exception as e:
            logger.error(f"加载特征配置文件失败: {e}", exc_info=True)
            # 返回空配置
            return {data_type: {} for data_type in self.DATA_TYPES}
        
    def _load_tris_coefficients(self):
        """加载三刺激值系数表"""
        try:
            # 尝试加载CIE三刺激值系数表
            internal_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'D65xCIE.xlsx')
            self.tris_coeff = pd.read_excel(internal_path, header=0, index_col=0)
        except Exception as e:
            logger.warning(f"加载三刺激值系数表失败: {e}", exc_info=True)
            # 创建空表，后续需要用到三刺激值时会报错
            self.tris_coeff = pd.DataFrame()
        
    def fit(self, 
            spectrum_data: pd.DataFrame, 
            merged_data: pd.DataFrame,
            metric_data: pd.DataFrame,
            data_type: str = "aerospot",
            ) -> str:
        """
        一键式建模流程
        
        Args:
            spectrum_data: 光谱数据DataFrame（列名为波段，每行是一条光谱样本）
            metric_data: 实测值DataFrame（每列是一个水质指标）
            data_type: 数据类型，必须是"warning_device"、"shore_data"或"smart_water"之一
            output_path: 输出加密模型的路径，默认在当前目录创建
            password: 加密密码（已不再使用，保留参数以保持兼容性）
            
        Returns:
            生成的加密模型文件路径
        """
        # 验证数据类型
        if data_type not in self.DATA_TYPES:
            raise ValueError(f"不支持的数据类型: {data_type}，必须是 {self.DATA_TYPES} 之一")
        logger.info(f"开始建模，数据类型: {data_type}")

        # 按照优先级获取模型参数（指标级别 > 数据类型级别 > 全局级别）
        model_params = {}
    
        # 1. 获取全局模型参数（最低优先级）
        global_params = self.features_config.get("model_params", {})
        model_params.update(global_params)
        
        # 2. 获取数据类型级别的模型参数（中等优先级）
        if data_type and data_type in self.features_config:
            data_type_params = self.features_config[data_type].get("model_params", {})
            if data_type_params:
                model_params.update(data_type_params)
                min_samples = model_params.get("min_samples", 6)

        # 构建模型字典
        models_dict = {}

        if len(spectrum_data) >= min_samples:
            logger.info(f"样本量：{len(spectrum_data)}，初步满足{data_type}类型数据默认最小样本量：{min_samples},采用自动建模。")
            # 1. 数据预处理
            processed_spectrum = self._preprocess_spectrum(spectrum_data)

            # 收集反演结果
            pred_dict = pd.DataFrame()
            # 2. 为每个水质指标建模
            for column in metric_data.columns:
                target = metric_data[column].dropna()
                
                # 获取该指标在该数据类型下的特征定义
                feature_definitions = self._get_feature_definitions(data_type, column)
                
                if not feature_definitions:
                    logger.warning(f"未找到 {data_type} 下 {column} 指标的特征定义，将跳过该指标")
                    continue
                
                # 计算特征
                features = self._calculate_features(processed_spectrum, feature_definitions)
                
                if features.empty:
                    logger.warning(f"{column} 指标的特征计算结果为空，将跳过该指标")
                    continue
                
                # 拟合模型
                model_result, pred_data = self._fit_model(features, target, data_type, column, model_params)
                
                if model_result:
                    models_dict[column] = model_result
                    pred_dict = pd.concat([pred_dict, pred_data], axis=1)
                    pred_dict = pred_dict.sort_index()
                    logger.info(f"成功为 {column} 指标建立模型")
                else:
                    logger.warning(f"为 {column} 指标建立模型失败")
            logger.info("一键式特征排序建模完成...")
        else:
            logger.info(f"样本量：{len(spectrum_data)}，不满足{data_type}类型数据默认最小样本量：{min_samples},采用模型微调。")
            # 采用模型微调(初步反演值和实测值线性拟合系数)
            models_dict, pred_dict = self._fit_linear_models(merged_data, metric_data)
            logger.info("模型微调完成...")

        return models_dict, pred_dict

    def _get_feature_definitions(self, data_type: str, metric_name: str) -> List[Dict]:
        """获取指定数据类型和指标的特征定义"""
        feature_references = []
        
        # 从配置中获取特征引用
        if data_type in self.features_config and metric_name in self.features_config[data_type]:
            # 配置已统一为字典格式，直接获取features
            feature_references = self.features_config[data_type][metric_name]["features"]
        # 如果找不到特定指标的定义，尝试使用通用定义
        elif data_type in self.features_config and "default" in self.features_config[data_type]:
            # 默认配置也是统一的字典格式
            feature_references = self.features_config[data_type]["default"]["features"]
        
        if not feature_references:
            return []
        
        # 获取完整的特征定义
        full_definitions = []
        for ref in feature_references:
            if "feature_id" not in ref:
                logger.warning(f"特征引用缺少feature_id: {ref}")
                continue
                
            feature_id = ref["feature_id"]
            
            # 获取基础特征定义
            if "features" in self.features_config and feature_id in self.features_config["features"]:
                base_definition = self.features_config["features"][feature_id].copy()
                
                # 如果有自定义波段映射，则合并
                if "bands" in ref:
                    base_definition["bands"] = ref["bands"]
                    
                full_definitions.append(base_definition)
            else:
                logger.warning(f"未找到特征ID为 {feature_id} 的定义")
        
        return full_definitions

    def _calculate_features(self, spectrum_data: pd.DataFrame, 
                            feature_definitions: List[Dict]) -> pd.DataFrame:
        """根据特征定义计算特征值"""
        features = pd.DataFrame(index=spectrum_data.index)
        
        # 实例化特征计算器
        calculator = SpectralCalculator(spectrum_data, self.tris_coeff)
        
        for feature_def in feature_definitions:
            feature_name = feature_def.get("name")
            formula = feature_def.get("formula")
            band_map = feature_def.get("bands", {})
            
            if not feature_name or not formula:
                continue
            
            try:
                # 替换公式中的波段为实际波长
                expr = formula
                for band, wavelength in band_map.items():
                    expr = expr.replace(band, str(wavelength))
                
                # 计算特征值
                feature_values = calculator.evaluate(expr)
                
                # 添加到特征DataFrame
                features[feature_name] = feature_values
                
            except Exception as e:
                logger.error(f"计算特征 {feature_name} 失败: {e}", exc_info=True)
        
        return features

    def _fit_model(self, features: pd.DataFrame, target: pd.Series, data_type: str = None, metric_name: str = None, model_params: dict = {}) -> Dict:
        """
        拟合特征与目标变量关系，返回模型参数
        
        Args:
            features: 特征数据
            target: 目标变量
            data_type: 数据类型，用于获取特定数据类型的模型参数
            metric_name: 指标名称，用于获取特定指标的模型参数
        
        Returns:
            模型参数字典
        """
        # 3. 获取指标级别的模型参数（最高优先级）
        if data_type and metric_name and data_type in self.features_config and metric_name in self.features_config[data_type]:
            # 配置已统一为字典格式，直接获取model_params
            metric_params = self.features_config[data_type][metric_name].get("model_params", {})
            if metric_params:
                model_params.update(metric_params)
        
        # 获取各个模型参数，使用默认值作为最终回退
        max_features = model_params.get("max_features", 5)
        min_samples = model_params.get("min_samples", 1)
        
        # 为每个特征拟合幂函数模型
        feature_fits = {}
        
        for feature_name in features.columns:
            feature_data = features[feature_name].dropna()
            # 删除特征为非正数的行
            feature_data = feature_data[feature_data > 0]
            
            # 对齐特征和目标数据
            common_idx = feature_data.index.intersection(target.index)
            if len(common_idx) < min_samples:  # 最小样本数阈值
                logger.warning(f'特征：{feature_name}可用样本量为{len(common_idx)}，不满足自定义最小样本量：{min_samples}，不再参与指标：{feature_name} 后续建模。')
                continue
                
            x_data = feature_data.loc[common_idx].values
            y_data = target.loc[common_idx].values

            # 处理无效值
            valid_mask = ~np.isnan(x_data) & ~np.isnan(y_data) & (x_data > 0) & (y_data > 0)
            if np.sum(valid_mask) < min_samples:  # 至少需要最小样本量
                logger.warning(f'特征：{feature_name}可用样本量为{np.sum(valid_mask)}，不满足自定义最小样本量：{min_samples}，不再参与指标：{feature_name} 后续建模。')
                continue
                
            x_valid = x_data[valid_mask]
            y_valid = y_data[valid_mask]
            
            # 记录原始数据范围
            logger.info(f"拟合数据范围 - x: {np.min(x_valid)}-{np.max(x_valid)}, y: {np.min(y_valid)}-{np.max(y_valid)}")
            
            try:
                # 拟合 y = a * x^b
                params = self._perform_power_fitting(x_valid, y_valid)
                
                if params:
                    a, b, corr, rmse, r2 = params
                    feature_fits[feature_name] = {
                        'a': float(a), 'b': float(b), 'corr': float(corr), 
                        'rmse': float(rmse), 'r2': float(r2)
                    }
            except Exception as e:
                logger.error(f"拟合特征 {feature_name} 失败: {e}", exc_info=True)
        
        if not feature_fits:
            return {}, pd.Series(np.nan, index=target.index, name=metric_name)
        
        # 按相关性排序
        sorted_features = sorted(feature_fits.items(), 
                                key=lambda x: abs(x[1]['corr']), 
                                reverse=True)
        
        # 判断max_features是数字还是"all",如果为all则跳过循环，否则进行循环筛选
        if isinstance(max_features, int):
            # 选择相关性最高的特征，不再使用阈值筛选
            best_features = sorted_features[:max_features]
            init_n = 1
        elif max_features == "all":
            best_features = sorted_features
            init_n = len(best_features)
        else:
            raise ValueError(f"max_features 必须是数字或 'all'")
            
        if not best_features:
            return {}, pd.Series(np.nan, index=target.index, name=metric_name)
        
        # 计算最终模型
        final_model = {}
        best_combination = None
        best_corr = -1
        
        # 尝试不同数量的特征组合
        for n in range(init_n, len(best_features) + 1):
            selected_features = best_features[:n]
            total_weight = sum(abs(f[1]['corr']) for f in selected_features)
            
            # 计算每个特征的权重
            weights = {f[0]: abs(f[1]['corr']) / total_weight for f in selected_features}
            
            # 计算反演结果
            inverted_values = {}
            for feature_name, params in selected_features:
                # 使用 a * x^b 公式进行反演
                x_data = features[feature_name].dropna()
                # 删除非正数的行
                x_data = x_data[x_data > 0]
                common_idx = x_data.index.intersection(target.index)
                x_values = x_data.loc[common_idx].values
                inverted = params['a'] * np.power(x_values, params['b'])
                inverted_values[feature_name] = pd.Series(inverted, index=common_idx)
            
            
            # 计算加权结果
            if inverted_values:
                # 确保所有特征的反演结果有共同的索引
                common_indices = set.intersection(*[set(series.index) for series in inverted_values.values()])
                if common_indices:
                    common_indices_list = list(common_indices)
                    weighted_result = pd.Series(0, index=common_indices_list, name=metric_name)
                    for feature_name in inverted_values:
                        weighted_result += inverted_values[feature_name].loc[common_indices_list] * weights[feature_name]
                    
                    # 计算与真实值的相关性
                    y_true = target.loc[weighted_result.index]
                    corr = np.corrcoef(weighted_result, y_true)[0, 1]
                    rmse = np.sqrt(np.mean((weighted_result - y_true) ** 2))
                    
                    # 更新最佳组合
                    if corr > best_corr:
                        best_corr = corr
                        best_combination = {
                            'n_features': n,
                            'features': selected_features,
                            'weights': weights,
                            'corr': corr,
                            'rmse': rmse,
                            'pred_data': pd.Series(weighted_result, index=target.index, name=metric_name)
                        }
        
        # 使用最佳组合构建最终模型
        if best_combination:
            for feature_name, params in best_combination['features']:
                final_model[feature_name] = {
                    'w': best_combination['weights'][feature_name],
                    'a': params['a'],
                    'b': params['b']
                }
        
        return final_model, best_combination['pred_data']

    def _fit_linear_models(self, merged_subset, metric_subset):
        """
        对每个指标拟合线性回归模型(强制通过原点)
        
        Args:
            merged_data: 合并后的数据DataFrame(航测数据)
            metric_data: 实测数据DataFrame
            
        Returns:
            dict: 各指标的拟合系数字典，格式为{指标名: 系数}
        """
        logger.info("开始模型微调...")
        models_dict = {}
        pred_dict = pd.DataFrame()
        
        # 获取两个DataFrame中共同的指标列
        common_indicators = set(merged_subset.columns).intersection(set(metric_subset.columns))
        if not common_indicators:
            common_indicators = merged_subset.columns  # 如果没有共同列，使用合并数据的所有列
            
        logger.info(f"将拟合 {len(common_indicators)} 个指标的模型")
        
        for indicator in common_indicators:
            try:
                # 获取航测和测量的指标数据，先在DataFrame上处理
                x_df = merged_subset[indicator].dropna()
                y_df = metric_subset[indicator].dropna()
                
                # 获取共同的有效索引
                common_indices = x_df.index.intersection(y_df.index)
                valid_count = len(common_indices)
                
                if valid_count < 2:
                    logger.warning(f"指标 {indicator} 的有效数据点少于2个（{valid_count}个），无法拟合")
                    models_dict[indicator] = None
                    continue
                
                # 提取有效样本值
                x_values = x_df.loc[common_indices].values
                y_values = y_df.loc[common_indices].values
                
                # 显示用于拟合的数据和索引
                logger.info(f"指标 {indicator} 拟合数据（共{valid_count}个有效点）：")
                for i in range(min(valid_count, 5)):  # 只显示前5个点，避免日志过长
                    idx = common_indices[i]
                    logger.info(f"  样本点 {i+1} [索引: {idx}]: 航测值 = {x_values[i]:.4f}, 测量值 = {y_values[i]:.4f}")
                
                if valid_count > 5:
                    logger.info(f"  ... 共{valid_count}个点")
                
                # 使用有效数据点
                X_valid = x_values.reshape(-1, 1)
                y_valid = y_values
                
                # 创建线性回归模型，不设置截距（强制经过原点）
                model = LinearRegression(fit_intercept=False)
                model.fit(X_valid, y_valid)
                
                # 获取拟合系数
                coefficient = float(model.coef_[0])
                
                # 计算拟合优度 R²
                y_pred = model.predict(X_valid)
                r2 = 1 - np.sum((y_valid - y_pred) ** 2) / np.sum((y_valid - np.mean(y_valid)) ** 2)
                
                # 计算均方根误差(RMSE)
                rmse = np.sqrt(np.mean((y_valid - y_pred) ** 2))
                
                # 将结果存入字典
                models_dict[indicator] = coefficient
                # 确保pred_dict中存在所需的索引和列
                # 更新预测值
                pred_series = pd.Series(y_pred, index=common_indices, name=indicator)
                pred_dict = pd.concat([pred_dict, pred_series], axis=1)
                
                # 记录拟合结果到日志
                logger.info(f"指标 {indicator} 拟合完成: 系数 = {coefficient:.4f}, "
                               f"R² = {r2:.4f}, RMSE = {rmse:.4f}, 样本数 = {valid_count}")
                
            except Exception as e:
                logger.error(f"拟合指标 {indicator} 时出错: {str(e)}")
                models_dict[indicator] = None
        
        logger.info(f"线性回归拟合完成，共处理 {len(models_dict)} 个指标")
        if len(models_dict) == len(pred_dict.columns):
            pred_dict = pred_dict.sort_index()
            return models_dict, pred_dict
        else:
            logger.error("成功拟合指标数量与预测结果数量不一致，请检查数据")
            return models_dict, pd.DataFrame()
 
    def _preprocess_spectrum(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理光谱数据
        
        Args:
            spectrum_data: 光谱数据
            
        Returns:
            预处理后的光谱数据
        """
        # 1. 确保列名是浮点数
        try:
            spectrum_data.columns = spectrum_data.columns.astype(float)
        except:
            raise ValueError("光谱数据列名必须是可转换为浮点数的波长值")
        
        # 2. 截取波段范围
        valid_columns = (spectrum_data.columns >= self.min_wavelength) & \
                        (spectrum_data.columns <= self.max_wavelength)
        if not valid_columns.any():
            raise ValueError(f"在范围 {self.min_wavelength}-{self.max_wavelength} 内没有有效波段")
            
        spectrum = spectrum_data.loc[:, valid_columns].copy()
        
        # 3. 清洗数据
        spectrum.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # 异常值处理（值小于0或大于1的替换为NaN）
        mask = (spectrum < 0) | (spectrum > 1)
        spectrum[mask] = np.nan
        
        # 填充缺失值
        spectrum = spectrum.ffill(axis=1).bfill(axis=1)
        
        # 4. 重采样到整数波长
        spectrum = self._resample_spectrum(spectrum)
        
        # 5. 平滑处理
        spectrum = self._smooth_spectrum(spectrum)
        
        # 6. 异常检测与剔除
        # spectrum, _ = self._filter_anomalies(spectrum)
        
        return spectrum

    def _resample_spectrum(self, spectrum: pd.DataFrame) -> pd.DataFrame:
        """重采样光谱到整数波长"""
        from scipy.interpolate import CubicSpline
        
        # 原始波长
        wavelengths = spectrum.columns.values
        data = spectrum.values
        
        # 定义目标波长（整数）
        target_wavelengths = np.arange(
            self.min_wavelength,
            self.max_wavelength + 1,
            1
        )
        
        # 初始化重采样数据
        resampled_data = np.zeros((data.shape[0], len(target_wavelengths)))
        
        # 对每条光谱进行重采样
        for i in range(data.shape[0]):
            try:
                # 使用三次样条插值
                cs = CubicSpline(wavelengths, data[i, :], bc_type="not-a-knot")
                resampled_data[i, :] = cs(target_wavelengths)
            except Exception as e:
                # 样本插值失败时，使用线性插值作为备选
                logger.warning(f"样本 {i} 三次样条插值失败，使用线性插值: {e}")
                resampled = np.interp(target_wavelengths, wavelengths, data[i, :])
                resampled_data[i, :] = resampled
        
        # 创建重采样后的DataFrame
        resampled_df = pd.DataFrame(
            resampled_data, 
            index=spectrum.index, 
            columns=target_wavelengths
        )
        
        return resampled_df

    def _smooth_spectrum(self, spectrum: pd.DataFrame) -> pd.DataFrame:
        """使用Savitzky-Golay滤波器平滑光谱"""
        from scipy.signal import savgol_filter
        
        data = spectrum.values
        
        # 确保窗口长度为奇数
        window_length = self.smooth_window
        if window_length % 2 == 0:
            window_length += 1
        
        # 确保窗口长度小于数据点数
        if window_length >= data.shape[1]:
            window_length = min(data.shape[1] - 1, 11)
            if window_length % 2 == 0:
                window_length -= 1
                
        # 确保多项式阶数小于窗口长度
        polyorder = min(self.smooth_order, window_length - 1)
        
        # 应用Savitzky-Golay滤波器
        try:
            smoothed_data = savgol_filter(data, window_length, polyorder, axis=1)
            
            # 保留窗口两端的原始数据
            half_window = window_length // 2
            smoothed_data[:, :half_window] = data[:, :half_window]
            smoothed_data[:, -half_window:] = data[:, -half_window:]
            
            return pd.DataFrame(smoothed_data, index=spectrum.index, columns=spectrum.columns)
        except Exception as e:
            logger.warning(f"平滑处理失败，返回原始数据: {e}", exc_info=True)
            return spectrum

    def _filter_anomalies(self, spectrum: pd.DataFrame, threshold: float = 0.1) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        使用信噪比检测和剔除异常光谱
        
        Args:
            spectrum: 光谱数据
            threshold: 信噪比阈值
            
        Returns:
            (正常光谱数据, 异常光谱数据)
        """
        from scipy.signal import savgol_filter
        
        # 找出噪声严重的光谱
        noisy_indices = []
        
        for i, (idx, row) in enumerate(spectrum.iterrows()):
            # 使用Savitzky-Golay滤波器获得平滑光谱
            try:
                smoothed = savgol_filter(row.values, 11, 3)
                
                # 计算残差
                residuals = row.values - smoothed
                
                # 计算残差标准差占波动范围的比例（信噪比）
                residual_std = np.std(residuals)
                data_range = smoothed.max() - smoothed.min()
                
                snr = residual_std / data_range if data_range > 0 else float('inf')
                
                # 如果信噪比超过阈值，标记为噪声
                if snr > threshold:
                    noisy_indices.append(idx)
            except:
                # 处理异常，可能是数据太少等原因
                continue
        
        # 分离正常和异常光谱
        normal_spectrum = spectrum.drop(noisy_indices, errors='ignore')
        anomalous_spectrum = spectrum.loc[noisy_indices] if noisy_indices else pd.DataFrame()
        
        logger.info(f"检测到 {len(noisy_indices)} 条异常光谱被剔除")
        
        return normal_spectrum, anomalous_spectrum

    def _encrypt_and_save(self, models_dict: Dict, output_path: str) -> str:
        """将模型参数加密为AES256格式并保存"""
        # 1. 添加元数据
        final_dict = {
            "metadata": {
                "created_time": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "models": models_dict
        }
        
        # 2. 转换为JSON字符串
        # indent=2 参数使JSON字符串格式化输出，每个层级缩进2个空格，使输出的JSON更易读
        json_data = json.dumps(models_dict, ensure_ascii=False, indent=2)
        
        # 3. 从密码生成密钥
        # 生成加密密钥
        password = b"water_quality_analysis_key"
        salt = b"water_quality_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
                        
        # 使用固定的初始化向量，而不是随机生成
        iv = b"fixed_iv_16bytes"  # 固定的16字节IV
        
        # 准备加密器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        # 对数据进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_data.encode('utf-8')) + padder.finalize()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 将IV与加密数据一起存储（IV可以是公开的）
        final_data = iv + encrypted_data

        
        # 5. 将盐和加密数据一起保存
        with open(output_path, 'wb') as f:
            f.write(final_data)
        logger.info(f"结果已加密并保存到: {output_path}")
        
        # 记录解密所需的参数（仅在本地日志中）
        logger.debug("===== 解密所需参数（仅供内部使用）=====")
        logger.debug(f"加密算法: AES256-CBC with PKCS7 padding")
        logger.debug(f"password: {password}")
        logger.debug(f"salt: {salt}")
        logger.debug(f"iterations: 100000")
        logger.debug(f"key length: 32 bytes")
        logger.debug(f"IV: 固定值 {iv}，仍存储在加密文件的前16个字节")
        logger.debug("解密步骤: 1)读取文件前16字节作为IV（虽然是固定值）; 2)使用相同参数通过PBKDF2派生密钥; 3)使用AES256-CBC和IV解密剩余数据; 4)去除PKCS7填充")
        logger.debug("===============================")
        return output_path

    def _perform_power_fitting(self, x_valid, y_valid, initial_guess=None):
        """执行幂函数拟合: y = a * x^b"""
        from scipy.optimize import curve_fit
        from scipy.stats import pearsonr
        import warnings
        
        # 定义拟合函数并捕获警告
        def fit_function(x, a, b):
            # 捕获幂运算中的警告并记录参数值
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = a * np.power(x, b)
                
                # 如果有警告产生，则记录参数信息
                if len(w) > 0 and issubclass(w[-1].category, RuntimeWarning):
                    # 记录产生警告时的参数值
                    logger.warning(f"幂运算溢出警告! 参数值: a={a}, b={b}")
                    logger.warning(f"x值范围: {np.min(x)} - {np.max(x)}")
                    
                    # 寻找导致溢出的具体x值
                    problem_indices = np.isnan(result) | np.isinf(result)
                    if np.any(problem_indices):
                        problem_x = x[problem_indices]
                        logger.warning(f"导致问题的x值: {problem_x[:10]} ...")
            
            return result
        
        try:
            
            
            # 初始猜测值
            if initial_guess is None:
                initial_guess = [1.0, 1.0]
            
            # 设置参数约束，防止产生极端参数值
            # a参数通常不需要太大，b参数应该在合理范围内
            bounds = (
                [-1000, -20],  # 下限：a可以为负，但b不应过度负值
                [1000, 20]     # 上限：限制a和b的绝对值
            )
            
            # 执行拟合，添加参数约束
            popt, pcov = curve_fit(
                fit_function, 
                x_valid, 
                y_valid, 
                p0=initial_guess, 
                maxfev=10000, 
                method='trf',   # 使用trust-region方法支持边界约束
                bounds=bounds
            )
            
            # 获取参数
            a, b = popt
            
            # 计算参数估计的标准误差
            perr = np.sqrt(np.diag(pcov))
            logger.info(f"拟合参数: a={a}±{perr[0]}, b={b}±{perr[1]}")
            
            # 计算预测值
            y_pred = fit_function(x_valid, a, b)
            
            # 计算评价指标
            corr_coef, _ = pearsonr(y_valid, y_pred)
            rmse = np.sqrt(np.mean((y_pred - y_valid) ** 2))
            ss_res = np.sum((y_valid - y_pred) ** 2)
            ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # 记录拟合质量
            logger.info(f"拟合质量: 相关系数={corr_coef:.4f}, RMSE={rmse:.4f}, R²={r_squared:.4f}")
            
            return a, b, corr_coef, rmse, r_squared
        except Exception as e:
            logger.error(f"拟合失败: {e}", exc_info=True)
            return None

    @staticmethod
    def decrypt_model(model_path: str, password: str = None) -> Dict:
        """解密模型文件，返回模型字典"""
        logger = logging.getLogger(__name__)
        
        with open(model_path, 'rb') as file:
            file_data = file.read()
        
        # 从文件读取IV（前16字节）
        iv = file_data[:16]
        encrypted_data = file_data[16:]
        
        # 使用固定密码和盐值
        password = b"water_quality_analysis_key"
        salt = b"water_quality_salt"
        
        # 从密码和盐值重新生成密钥
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
        try:
            models_dict = json.loads(decrypted_data)
            logger.debug(f"成功解密模型文件: {model_path}")
            return models_dict
        except Exception as e:
            logger.error(f"解析解密后的JSON数据失败: {e}", exc_info=True)
            raise 